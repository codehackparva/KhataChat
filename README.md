# Munim (मुनीम): a chat-based digital khata for small shops

**SDG 8: Decent Work and Economic Growth (target 8.10, access to financial services for small businesses)**

Live demo: [PASTE LIVE LINK HERE AFTER DEPLOY]
Demo video: [PASTE VIDEO LINK HERE]

## The problem

Many small shopkeepers in India track sales, expenses and customer credit (udhaar) on paper or in their heads. They often don't know their weekly profit and forget who owes them money. Ledger apps with forms and menus are hard for owners who think and speak in Gujarati or Hindi.

[OPTIONAL: add 1-2 real quotes from shop owners you actually spoke to, with their permission. If you did not interview anyone, delete this line and do not invent quotes.]

## What Munim does

The shopkeeper types a message in Gujarati, Hindi, English or a mix:

- `Ramesh ne 500 ka maal udhaar liya` records a credit sale
- `paanch hazaar rent bhara` records an expense
- `kis kis ka paisa baaki hai?` lists who owes how much
- `aaj ka profit kitna hai?` reports sales minus expenses

Before anything is saved, Munim repeats the entry and waits for a yes. If a message is unclear (for example just `500 aaya`), it asks a question instead of guessing.

## Key design decision: the LLM never does the math

An LLM that adds numbers will eventually get one wrong, and in finance a wrong number destroys trust. So the work is split:

| Layer | Responsibility |
|---|---|
| LLM (Gemini) | Understand the message, pick a tool, phrase the reply |
| Python code | Validate input, store entries, compute every total |
| PostgreSQL (Supabase) | Store data and enforce rules at database level |

```
User message -> Gemini (tool calling) -> confirm step -> tools.py -> Supabase
                                     \-> query_ledger -> SQL/Python totals -> Gemini phrases the answer
```

Money is stored as integer paise, never floats. The LLM can only call three fixed tools and cannot write SQL:

1. `add_transaction`: saves an entry, only after user confirmation
2. `query_ledger`: fixed metrics (profit, sales, expenses, outstanding credit, party balance)
3. `ask_clarification`: asks the user when the message is ambiguous

## Reliability features

- Confirmation step before every write
- Database constraints (positive amounts, credit entries must name a customer)
- Retry and model fallback when the API returns 503 or 429
- Refuses anything outside bookkeeping (no loan, tax or investment advice)

## Results so far

Manual tests on single messages (not a full evaluation):

- Hindi number words (`paanch hazaar`, `dedh sau`) parsed correctly
- Gujarati script input (`રમેશે ૫૦૦ રૂપિયા પાછા આપ્યા`) parsed as a payment received from Ramesh
- Ambiguous input (`500 aaya`) triggered a clarifying question instead of a save
- Ledger totals checked by hand against the database rows

**Evaluation on a 25-message test set:** [FILL IN AFTER RUNNING tests/run_eval.py, for example "X of 25 parsed correctly, Y wrongly saved, Z correctly escalated". Do not write a number you did not measure.]

## Known limitations (found during testing)

- Gujarati names were once saved in Gujarati script, creating a duplicate customer. Fixed with a prompt rule, but not proven across many inputs.
- A Roman-script Hinglish message sometimes gets a reply in Gujarati or Devanagari.
- One entry in the session once defaulted to guessing from earlier messages before a prompt fix. Retested on a small number of cases only.
- "Profit" here is sales minus expenses. It ignores cost of goods, so it is not accounting profit.
- The demo uses one shared ledger with fake data and no user login. It is not safe for real shops yet.
- Free-tier LLM APIs can be slow or return 503 under load.
- Not yet tested with real shopkeepers.

## Tech stack

Python, Gemini API (function calling), Supabase (PostgreSQL), Gradio, deployed on [HOSTING PLATFORM].

## Run locally (Windows PowerShell)

```powershell
git clone https://github.com/USERNAME/munim.git
cd munim
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in `GEMINI_API_KEY`, `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`. Create the tables by running the SQL schema in your Supabase SQL Editor. Then:

```powershell
python -m app.ui
```

## Future work

- Multi-shop support with login and per-shop data
- WhatsApp interface
- Fine-tune a small local model on collected Gujarati/Hindi ledger messages
- Voice input

## Safety notes

The service key lives only in environment variables and is never committed. The demo contains only fictional data.