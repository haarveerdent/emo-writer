import logging
from datetime import datetime, timezone
from pipeline.state import PipelineState
from pipeline.clients.supabase_client import get_supabase_client
from pipeline.config import PUBLISHED_STORIES_TABLE

logger = logging.getLogger(__name__)


def store_to_supabase(state: PipelineState) -> PipelineState:
    """
    Agent 8: Upsert QA-passed stories into Supabase.
    Uses upsert with on_conflict='reddit_id' as safety net against duplicates.
    No LLM call.
    """
    supabase = get_supabase_client()
    statuses: list[str] = []

    for story in state.qa_passed_stories:
        try:
            record = {
                "reddit_id": story.reddit_id,
                "title": story.title,
                "content": story.content,
                "subreddit": story.subreddit,
                "upvotes": story.upvotes,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            supabase.table(PUBLISHED_STORIES_TABLE).upsert(
                record, on_conflict="reddit_id"
            ).execute()
            logger.info(f"[supabase_storage] SUCCESS reddit_id={story.reddit_id}")
            statuses.append(f"SUCCESS:{story.reddit_id}")
        except Exception as e:
            logger.error(f"[supabase_storage] ERROR reddit_id={story.reddit_id}: {e}")
            statuses.append(f"ERROR:{story.reddit_id}:{e}")

    state.database_insert_status = statuses
    return state
