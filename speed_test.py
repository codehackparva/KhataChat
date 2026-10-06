import time
from google import genai
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

for m in MODELS:
    t = time.time()
    try:
        client.models.generate_content(model=m, contents="Ramesh ne 500 ka maal udhaar liya")
        print(f"{m}: {time.time() - t:.1f} sec")
    except Exception as e:
        print(f"{m}: ERROR after {time.time() - t:.1f} sec -> {str(e)[:80]}")