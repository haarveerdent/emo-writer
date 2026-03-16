import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a privacy editor (Pass 1). Completely anonymize both the TITLE and BODY of the story.

RULES:
1. Replace all human names with descriptors (e.g., 'my friend', 'my partner') or single initials like 'J.'.
2. Replace specific cities, states, and countries with generic terms (e.g., 'a city in the midwest', 'my hometown').
3. Remove or generalize specific ages (e.g., '27' → 'late twenties').
4. Remove specific company names, school names, or job titles.
5. DO NOT change the emotional tone or alter the plot.

Respond in this exact format:
TITLE: <anonymized title>
BODY: <anonymized body>"""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(title: str, content: str) -> str:
    user_message = f"TITLE: {title}\nBODY: {content}"
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=user_message, temperature=0.0)


def _parse_response(response: str) -> tuple[str, str]:
    """Extract TITLE and BODY from the structured response."""
    lines = response.strip().splitlines()
    title = ""
    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith("TITLE:") and not in_body:
            title = line[len("TITLE:"):].strip()
        elif line.startswith("BODY:"):
            in_body = True
            body_lines.append(line[len("BODY:"):].strip())
        elif in_body:
            body_lines.append(line)

    return title, "\n".join(body_lines).strip()


def anonymize_pii(state: PipelineState) -> PipelineState:
    """Agent 4: Pass 1 — remove PII from both title and content."""
    anonymized: list[StoryRecord] = []

    for story in state.consensus_filtered_stories:
        try:
            response = _call_llm(story.title, story.content)
            new_title, new_content = _parse_response(response)
            if not new_title:
                new_title = story.title  # fallback: keep original if parse fails
            anonymized.append(
                StoryRecord(
                    reddit_id=story.reddit_id,
                    title=new_title,
                    content=new_content or story.content,
                    subreddit=story.subreddit,
                    upvotes=story.upvotes,
                )
            )
        except Exception as e:
            logger.error(f"[pii_anonymizer] error on reddit_id={story.reddit_id}: {e}")

    logger.info(f"[pii_anonymizer] processed={len(anonymized)}/{len(state.consensus_filtered_stories)}")
    state.anonymized_stories = anonymized
    return state
