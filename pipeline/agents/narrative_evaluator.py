import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a narrative analyst (Pass 1). Read the provided story. Determine if the story has a definitive ending.

REJECT IF:
- The author asks for advice on what to do next.
- The situation ends on a cliffhanger or is 'to be continued'.
- The central conflict is actively ongoing.

ACCEPT IF:
- The central conflict is resolved.
- The author is reflecting on a past event that is fully concluded.

Output 'ACCEPT' followed by a brief justification, otherwise output 'REJECT' followed by a brief justification."""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(content: str) -> str:
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=content, temperature=0.0)


def evaluate_narrative_resolution(state: PipelineState) -> PipelineState:
    """Agent 2: Pass 1 — filter stories without a definitive ending."""
    filtered: list[StoryRecord] = []

    for story in state.raw_stories:
        try:
            result = _call_llm(story.content)
            if result.strip().upper().startswith("ACCEPT"):
                filtered.append(story)
            else:
                logger.info(f"[narrative_evaluator] REJECTED reddit_id={story.reddit_id}")
        except Exception as e:
            logger.error(f"[narrative_evaluator] error on reddit_id={story.reddit_id}: {e}")

    logger.info(
        f"[narrative_evaluator] passed={len(filtered)}/{len(state.raw_stories)}"
    )
    state.filtered_stories = filtered
    return state
