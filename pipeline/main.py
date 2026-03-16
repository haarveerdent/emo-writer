import time
import logging
from dotenv import load_dotenv

load_dotenv()  # no-op in GitHub Actions; loads .env for local runs

from pipeline.utils.logging_config import configure_logging
from pipeline.clients.supabase_client import get_supabase_client
from pipeline.state import PipelineState
from pipeline.graph import build_graph
from pipeline.config import PUBLISHED_STORIES_TABLE

configure_logging()
logger = logging.getLogger(__name__)


def load_published_ids() -> list[str]:
    """Load all previously published reddit_ids from Supabase for dedup."""
    supabase = get_supabase_client()
    response = supabase.table(PUBLISHED_STORIES_TABLE).select("reddit_id").execute()
    return [row["reddit_id"] for row in response.data]


def main():
    start = time.time()
    logger.info("=== Pipeline run started ===")

    try:
        published_ids = load_published_ids()
        logger.info(f"Loaded {len(published_ids)} published story IDs for dedup")
    except Exception as e:
        logger.error(f"Failed to load published IDs from Supabase: {e}")
        raise SystemExit(1)

    initial_state = PipelineState(published_story_ids=published_ids)

    graph = build_graph()

    try:
        result = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise SystemExit(1)

    # LangGraph returns an AddableValuesDict — access as dict
    duration_ms = int((time.time() - start) * 1000)
    insert_statuses = result.get("database_insert_status", [])
    successes = [s for s in insert_statuses if s.startswith("SUCCESS")]
    errors = [s for s in insert_statuses if s.startswith("ERROR")]

    logger.info(
        f"=== Pipeline run complete === "
        f"scraped={len(result.get('raw_stories', []))} "
        f"after_pass1={len(result.get('filtered_stories', []))} "
        f"after_pass2={len(result.get('consensus_filtered_stories', []))} "
        f"published={len(successes)} "
        f"errors={len(errors)} "
        f"duration_ms={duration_ms}"
    )

    for err in errors:
        logger.warning(f"Insert error: {err}")


if __name__ == "__main__":
    main()
