from app.tools import add_transaction, query_ledger
print(add_transaction("sale_credit", 500, party="ramesh"))
print(add_transaction("expense", 5000, note="rent"))
print(query_ledger("profit"))
print(query_ledger("outstanding_credit"))