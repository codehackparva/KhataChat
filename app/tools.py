from datetime import date
from app.db import sb, get_or_create_party

VALID_TYPES = {"sale_cash", "sale_credit", "expense", "credit_payment_received"}
NEEDS_PARTY = {"sale_credit", "credit_payment_received"}

def add_transaction(type, amount_rupees, party=None, note=None, tx_date=None):
    if type not in VALID_TYPES:
        return {"ok": False, "error": f"invalid type: {type}"}
    paise = round(float(amount_rupees) * 100)
    if paise <= 0:
        return {"ok": False, "error": "amount must be positive"}
    if type in NEEDS_PARTY and not party:
        return {"ok": False, "error": "party name required for credit entries"}
    row = {
        "type": type,
        "amount_paise": paise,
        "party_id": get_or_create_party(party) if party else None,
        "note": note,
        "date": tx_date or date.today().isoformat(),
    }
    sb.table("transactions").insert(row).execute()
    return {"ok": True, "saved": {"type": type, "amount_rupees": paise / 100, "party": party}}

def query_ledger(metric, start_date=None, end_date=None, party=None):
    rows = sb.table("transactions").select(
        "type,amount_paise,date,parties(name)").execute().data
    # fine at demo scale; Supabase returns max 1000 rows by default

    def in_range(r):
        return ((not start_date or r["date"] >= start_date) and
                (not end_date or r["date"] <= end_date))

    def total(types, rows_):
        return sum(r["amount_paise"] for r in rows_ if r["type"] in types) / 100

    scoped = [r for r in rows if in_range(r)]
    if metric == "total_sales":
        return {"value": total({"sale_cash", "sale_credit"}, scoped)}
    if metric == "total_expenses":
        return {"value": total({"expense"}, scoped)}
    if metric == "profit":
        return {"value": total({"sale_cash", "sale_credit"}, scoped)
                         - total({"expense"}, scoped)}
    if metric in ("party_balance", "outstanding_credit"):
        owed = {}
        for r in rows:  # balances are all-time, not date-filtered
            if not r["parties"]:
                continue
            name = r["parties"]["name"]
            sign = 1 if r["type"] == "sale_credit" else \
                  -1 if r["type"] == "credit_payment_received" else 0
            owed[name] = owed.get(name, 0) + sign * r["amount_paise"] / 100
        if metric == "party_balance":
            return {"party": party, "owed": owed.get((party or "").strip().title(), 0)}
        return {"owed_by_party": {n: v for n, v in owed.items() if v > 0}}
    return {"error": f"unknown metric: {metric}"}