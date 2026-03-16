import logging
from pipeline.state import PipelineState, StoryRecord
from pipeline.clients.openai_client import OpenAIResponsesClient
from pipeline.utils.retry import with_retry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an independent narrative auditor (Pass 2). Read the provided story. Your sole job is to verify that this story has a definitive, closed ending. Do not trust previous tags. If there is ANY indication the situation is ongoing or unresolved, you must reject it.

Output 'ACCEPT_CONSENSUS' if the ending is definitive, otherwise output 'REJECT_CONSENSUS'."""

client = OpenAIResponsesClient()


@with_retry(max_attempts=3, base_delay=2)
def _call_llm(content: str) -> str:
    return client.call(system_prompt=SYSTEM_PROMPT, user_message=content, temperature=0.0)


def evaluate_resolution_consensus(state: PipelineState) -> PipelineState:
    """Agent 3: Pass 2 — double-check narrative completeness."""
    consensus: list[StoryRecord] = []

    for story in state.filtered_stories:
        try:
            result = _call_llm(story.content)
            if result.strip().upper().startswith("ACCEPT_CONSENSUS"):
                consensus.append(story)
            else:
                logger.info(f"[consensus_evaluator] REJECTED reddit_id={story.reddit_id}")
        except Exception as e:
            logger.error(f"[consensus_evaluator] error on reddit_id={story.reddit_id}: {e}")

    logger.info(
        f"[consensus_evaluator] passed={len(consensus)}/{len(state.filtered_stories)}"
    )
    state.consensus_filtered_stories = consensus
    return state
