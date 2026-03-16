import re
from pipeline.config import MAX_CONTENT_CHARS


def truncate_to_sentence_boundary(text: str, max_chars: int = MAX_CONTENT_CHARS) -> str:
    """Truncate text at a sentence boundary, never mid-sentence."""
    if len(text) <= max_chars:
        return text

    chunk = text[:max_chars]
    # Find the last sentence-ending punctuation before the limit
    match = re.search(r"[.!?][^.!?]*$", chunk)
    if match:
        return chunk[: match.start() + 1]
    return chunk
