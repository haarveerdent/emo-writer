from supabase import create_client, Client
from pipeline.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
