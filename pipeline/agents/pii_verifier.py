import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a strict privacy auditor (Pass 2). Read the provided TITLE and BODY. Look specifically for any missed names, specific locations, exact ages, school names, or company names.

If you find ANY identifying information, correct it immediately using generic placeholders. If no changes are needed, output the text as-is.

Respond in this exact format:
TITLE: <audited title>
BODY: <audited body>"""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(title: str, content: str) -> str:
    user_message = f"TITLE: {title}\nBODY: {content}"
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=user_message, temperature=0.0)


def _parse_response(response: str) -> tuple[str, str]:
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


def verify_pii_removal(state: PipelineState) -> PipelineState:
    """Agent 5: Pass 2 — audit PII removal on both title and content."""
    verified: list[StoryRecord] = []

    for story in state.anonymized_stories:
        try:
            response = _call_llm(story.title, story.content)
            new_title, new_content = _parse_response(response)
            verified.append(
                StoryRecord(
                    reddit_id=story.reddit_id,
                    title=new_title or story.title,
                    content=new_content or story.content,
                    subreddit=story.subreddit,
                    upvotes=story.upvotes,
                )
            )
        except Exception as e:
            logger.error(f"[pii_verifier] error on reddit_id={story.reddit_id}: {e}")

    logger.info(f"[pii_verifier] processed={len(verified)}/{len(state.anonymized_stories)}")
    state.verified_anonymized_stories = verified
    return state
