-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS published_stories (
    id          UUID          DEFAULT gen_random_uuid() PRIMARY KEY,
    reddit_id   VARCHAR(20)   NOT NULL UNIQUE,
    title       TEXT          NOT NULL,
    content     TEXT          NOT NULL,
    subreddit   VARCHAR(100),
    upvotes     INTEGER       DEFAULT 0,
    created_at  TIMESTAMPTZ   DEFAULT NOW() NOT NULL
);

-- Fast dedup lookups at pipeline startup
CREATE INDEX IF NOT EXISTS idx_published_stories_reddit_id
    ON published_stories (reddit_id);

-- Display/dashboard queries (newest first)
CREATE INDEX IF NOT EXISTS idx_published_stories_created_at
    ON published_stories (created_at DESC);

-- RLS: service role bypasses; anon key is read-only
ALTER TABLE published_stories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access"
    ON published_stories FOR SELECT
    USING (true);
