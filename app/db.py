from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_or_create_party(name: str) -> int:
    name = name.strip().title()
    found = sb.table("parties").select("id").eq("name", name).execute().data
    if found:
        return found[0]["id"]
    return sb.table("parties").insert({"name": name}).execute().data[0]["id"]