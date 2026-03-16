import os

# --- Reddit scraping config ---
TARGET_SUBREDDITS = [
    # Original
    "TrueOffMyChest",
    "confessions",
    "offmychest",
    "relationship_advice",
    # High-volume resolved drama
    "AITAH",
    "AmItheAsshole",
    "tifu",
    # Revenge / vindication (strong narrative arcs)
    "ProRevenge",
    "pettyrevenge",
    "MaliciousCompliance",
    # Family & toxic relationships
    "raisedbynarcissists",
    "JustNoMIL",
    "JUSTNOFAMILY",
    "entitledparents",
    "EstrangedAdultChildren",
    # Grief & survival
    "survivorsofabuse",
    "widowers",
    # Workplace & career
    "antiwork",
    "WorkReform",
    "jobs",
    "careerguidance",
    "ExperiencedDevs",
    "cscareerquestions",
    "AskHR",
    "weddingplanning",
    "recruitinghell",
    "managers",
]
POST_LIMIT = 50          # per subreddit per fetch call
MIN_UPVOTE_THRESHOLD = 500
MIN_WORD_COUNT = 1000

# --- OpenAI ---
OPENAI_MODEL = "gpt-5-nano"

# --- Supabase ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PUBLISHED_STORIES_TABLE = "published_stories"

# --- Token management ---
MAX_CONTENT_CHARS = 8000   # ~1200-1500 words; ensures 1000-word minimum survives truncation
