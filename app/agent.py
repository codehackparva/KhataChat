import time
from datetime import date
from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY
from app import tools

client = genai.Client(api_key=GEMINI_API_KEY)
MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]

SYSTEM = f"""You are a bookkeeping assistant for a small shop owner.
Users write in Gujarati, Hindi, English or a mix. Today is {date.today().isoformat()}.
Your only job: (1) turn messages into ledger entries with add_transaction,
(2) answer questions with query_ledger, (3) call ask_clarification if the
amount, direction or person is unclear.
Never calculate totals yourself. Never state a number that did not come from
a tool result. Refuse anything outside bookkeeping (loans, tax, investment advice).
Always write party names in English/Roman letters (રમેશ -> Ramesh), never in Gujarati or Devanagari script, and never add brackets to a name.
If a message has only an amount, or does not say who paid or what for, always call ask_clarification. Never guess from earlier messages.
When you answer from query_ledger, always state every rupee amount from the result next to each name, formatted like "Ramesh: ₹700". Show a loss as "₹5,750 loss", not as a negative number.
Reply in the same language the user used."""

add_tx = types.FunctionDeclaration(
    name="add_transaction",
    description="Record one ledger entry.",
    parameters={"type": "object", "properties": {
        "type": {"type": "string", "enum": ["sale_cash", "sale_credit", "expense", "credit_payment_received"]},
        "amount_rupees": {"type": "number"},
        "party": {"type": "string"},
        "note": {"type": "string"},
        "date": {"type": "string", "description": "YYYY-MM-DD, only if the user names a day"},
    }, "required": ["type", "amount_rupees"]},
)
query = types.FunctionDeclaration(
    name="query_ledger",
    description="Get totals from the ledger.",
    parameters={"type": "object", "properties": {
        "metric": {"type": "string", "enum": ["profit", "total_sales", "total_expenses", "outstanding_credit", "party_balance"]},
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "party": {"type": "string"},
    }, "required": ["metric"]},
)
clarify = types.FunctionDeclaration(
    name="ask_clarification",
    description="Ask the user a short question when the entry is unclear.",
    parameters={"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]},
)
CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM,
    tools=[types.Tool(function_declarations=[add_tx, query, clarify])],
)


def generate(contents):
    for model in MODELS:
        for attempt in range(3):
            try:
                return client.models.generate_content(model=model, contents=contents, config=CONFIG)
            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    time.sleep(1)
                    continue
                print("  (model error, trying next):", str(e)[:100])
                break
    return None


def run_turn(history, user_text):
    contents = history + [types.Content(role="user", parts=[types.Part(text=user_text)])]
    for _ in range(4):
        r = generate(contents)
        if r is None:
            return {"kind": "text", "text": "Server busy hai, thodi der baad try karo."}
        if not r.function_calls:
            return {"kind": "text", "text": r.text or ""}
        call = r.function_calls[0]
        args = dict(call.args)
        if call.name == "add_transaction":
            return {"kind": "confirm", "args": args}
        if call.name == "ask_clarification":
            return {"kind": "text", "text": args.get("question", "")}
        if call.name == "query_ledger":
            try:
                result = tools.query_ledger(**args)
            except Exception as e:
                result = {"error": str(e)}
            contents.append(r.candidates[0].content)
            contents.append(types.Content(role="user", parts=[
                types.Part.from_function_response(name="query_ledger", response=result)]))
    return {"kind": "text", "text": "Samajh nahi aaya, dobara likho."}


def save(a):
    return tools.add_transaction(
        type=a.get("type"), amount_rupees=a.get("amount_rupees"),
        party=a.get("party"), note=a.get("note"), tx_date=a.get("date"))


def main():
    history = []
    print("Munim ready. 'exit' likho band karne ke liye.")
    while True:
        text = input("\nYou: ").strip()
        if text.lower() in ("exit", "quit"):
            break
        out = run_turn(history, text)
        if out["kind"] == "confirm":
            a = out["args"]
            print(f"Save karun? {a.get('type')} | Rs {a.get('amount_rupees')} | {a.get('party')} | {a.get('note')}")
            if input("(yes/no): ").strip().lower() in ("yes", "y", "haan", "ha"):
                reply = "Saved." if save(a).get("ok") else "Save nahi hua, error aaya."
            else:
                reply = "Cancel kar diya."
        else:
            reply = out["text"]
        print("Munim:", reply)
        history.append(types.Content(role="user", parts=[types.Part(text=text)]))
        history.append(types.Content(role="model", parts=[types.Part(text=reply)]))


if __name__ == "__main__":
    main()