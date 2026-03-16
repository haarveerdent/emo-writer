from pydantic import BaseModel, Field
from typing import List


class StoryRecord(BaseModel):
    model_config = {"frozen": False}

    reddit_id: str
    title: str
    content: str
    subreddit: str
    upvotes: int


class PipelineState(BaseModel):
    model_config = {"frozen": False}

    # Loaded at startup from Supabase — used by Agent 1 for dedup
    published_story_ids: List[str] = Field(default_factory=list)

    # Agent 1 output
    raw_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 2 output (Pass 1 narrative filter)
    filtered_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 3 output (Pass 2 consensus filter)
    consensus_filtered_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 4 output (Pass 1 PII removal — title + content)
    anonymized_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 5 output (Pass 2 PII audit — title + content)
    verified_anonymized_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 6 output (Pass 1 editorial polish)
    final_polished_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 7 output (Pass 2 QA gate)
    qa_passed_stories: List[StoryRecord] = Field(default_factory=list)

    # Agent 8 output
    database_insert_status: List[str] = Field(default_factory=list)
