import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a final-pass editorial agent (Pass 1). Review the anonymized TITLE and BODY of this story.

Your tasks:
- Smooth out any awkward sentences caused by the removal of names or places.
- Ensure the body is structured with clear paragraphs.
- Make the title compelling and natural-sounding.
- Do NOT add new plot points or change facts.

Respond in this exact format:
TITLE: <polished title>
BODY: <polished body>"""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(title: str, content: str) -> str:
    user_message = f"TITLE: {title}\nBODY: {content}"
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=user_message, temperature=0.4)


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


def polish_editorial(state: PipelineState) -> PipelineState:
    """Agent 6: Pass 1 — editorial polish on title and content."""
    polished: list[StoryRecord] = []

    for story in state.verified_anonymized_stories:
        try:
            response = _call_llm(story.title, story.content)
            new_title, new_content = _parse_response(response)
            polished.append(
                StoryRecord(
                    reddit_id=story.reddit_id,
                    title=new_title or story.title,
                    content=new_content or story.content,
                    subreddit=story.subreddit,
                    upvotes=story.upvotes,
                )
            )
        except Exception as e:
            logger.error(f"[editorial_polisher] error on reddit_id={story.reddit_id}: {e}")

    logger.info(f"[editorial_polisher] processed={len(polished)}/{len(state.verified_anonymized_stories)}")
    state.final_polished_stories = polished
    return state
