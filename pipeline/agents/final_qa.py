import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the final QA gatekeeper (Pass 2). Review the TITLE and BODY one last time.

Verify three things:
1. The prose flows naturally — no awkward gaps or abrupt transitions.
2. There are ZERO real names, specific locations, or identifying details in either the title or body.
3. The story clearly ends — the reader is not left hanging.

Make any minor final tweaks necessary to ensure publication quality. Do NOT rewrite extensively.

Respond in this exact format:
TITLE: <final title>
BODY: <final body>"""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(title: str, content: str) -> str:
    user_message = f"TITLE: {title}\nBODY: {content}"
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=user_message, temperature=0.1)


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


def run_final_qa(state: PipelineState) -> PipelineState:
    """Agent 7: Pass 2 — final QA gate on title and content."""
    qa_passed: list[StoryRecord] = []

    for story in state.final_polished_stories:
        try:
            response = _call_llm(story.title, story.content)
            new_title, new_content = _parse_response(response)
            qa_passed.append(
                StoryRecord(
                    reddit_id=story.reddit_id,
                    title=new_title or story.title,
                    content=new_content or story.content,
                    subreddit=story.subreddit,
                    upvotes=story.upvotes,
                )
            )
        except Exception as e:
            logger.error(f"[final_qa] error on reddit_id={story.reddit_id}: {e}")

    logger.info(f"[final_qa] passed={len(qa_passed)}/{len(state.final_polished_stories)}")
    state.qa_passed_stories = qa_passed
    return state
