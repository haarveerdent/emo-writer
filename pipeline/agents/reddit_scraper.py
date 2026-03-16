import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.reddit_client import fetch_hot_posts
from pipeline.utils.truncation import truncate_to_sentence_boundary
from pipeline.utils.retry import with_retry
from pipeline.config import TARGET_SUBREDDITS, POST_LIMIT, MIN_UPVOTE_THRESHOLD, MIN_WORD_COUNT

logger = logging.getLogger(__name__)


@with_retry(max_attempts=3, base_delay=2)
def _fetch(subreddit: str, limit: int) -> list[dict]:
    return fetch_hot_posts(subreddit, limit)


def scrape_and_deduplicate(state: PipelineState) -> PipelineState:
    """
    Agent 1: Scrape high-traction text posts via Reddit's public JSON API.
    No API credentials needed. Skips already-published posts.
    """
    published_ids = set(state.published_story_ids)
    seen_ids: set[str] = set()
    raw_stories: list[StoryRecord] = []

    for subreddit_name in TARGET_SUBREDDITS:
        try:
            posts = _fetch(subreddit_name, POST_LIMIT)
        except Exception as e:
            logger.warning(f"Failed to fetch r/{subreddit_name}: {e}")
            continue

        for post in posts:
            if not post.get("is_self"):
                continue
            if post.get("score", 0) < MIN_UPVOTE_THRESHOLD:
                continue
            post_id = post.get("id", "")
            if post_id in published_ids or post_id in seen_ids:
                continue
            body = post.get("selftext", "").strip()
            if not body or body in ("[removed]", "[deleted]"):
                continue
            if len(body.split()) < MIN_WORD_COUNT:
                continue

            seen_ids.add(post_id)
            raw_stories.append(
                StoryRecord(
                    reddit_id=post_id,
                    title=post.get("title", ""),
                    content=truncate_to_sentence_boundary(body),
                    subreddit=subreddit_name,
                    upvotes=post.get("score", 0),
                )
            )

    logger.info(f"[reddit_scraper] scraped={len(raw_stories)}")
    state.raw_stories = raw_stories
    return state
