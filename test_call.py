import os, time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Tried in order. Names come from your own list_models output.
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash"]

add_tx = types.FunctionDeclaration(
    name="add_transaction",
    description="Record one ledger entry for a shop.",
    parameters={
        "type": "object",
        "properties": {
            "type": {"type": "string",
                     "enum": ["sale_cash", "sale_credit", "expense",
                              "credit_payment_received"]},
            "amount_rupees": {"type": "number"},
            "party": {"type": "string"},
            "note": {"type": "string"},
        },
        "required": ["type", "amount_rupees"],
    },
)
config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=[add_tx])])

def call_with_retry(msg):
    for model in MODELS:
        for attempt in range(3):
            try:
                return model, client.models.generate_content(
                    model=model, contents=msg, config=config)
            except Exception as e:
                s = str(e)
                if "503" in s or "429" in s:
                    time.sleep(2 ** (attempt + 1))  # 2s, 4s, 8s
                    continue
                print(f"  {model} failed: {s[:120]}")
                break  # non-retryable (e.g. 404): go to next model
    return None, None

tests = [
    "Ramesh ne 500 ka maal udhaar liya",
    "paanch hazaar rent bhara",
    "dedh sau ka cash sale hua",
    "રમેશે ૫૦૦ રૂપિયા પાછા આપ્યા",
]

for msg in tests:
    print("\nMESSAGE:", msg)
    model, r = call_with_retry(msg)
    if r is None:
        print("ALL MODELS FAILED")
    elif r.function_calls:
        for c in r.function_calls:
            print(f"[{model}] TOOL CALL:", c.name, dict(c.args))
    else:
        print(f"[{model}] NO TOOL CALL:", r.text)