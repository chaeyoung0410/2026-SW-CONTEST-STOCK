-- Apply after 002_result_integrity_sqlite.sql.
PRAGMA foreign_keys = ON;

ALTER TABLE recommendation_history ADD COLUMN clicked_at DATETIME NULL;
ALTER TABLE recommendation_history
    ADD COLUMN learning_started BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE recommendation_history ADD COLUMN started_at DATETIME NULL;
ALTER TABLE recommendation_history ADD COLUMN baseline_accuracy FLOAT NULL;
ALTER TABLE recommendation_history ADD COLUMN baseline_score INTEGER NULL;
ALTER TABLE recommendation_history ADD COLUMN baseline_wrong_count INTEGER NULL;
ALTER TABLE recommendation_history
    ADD COLUMN completion_result_id INTEGER NULL REFERENCES result(result_id);
ALTER TABLE recommendation_history
    ADD COLUMN is_default_recommendation BOOLEAN NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS ix_recommendation_completion_result_id
    ON recommendation_history (completion_result_id);

UPDATE recommendation_history
SET clicked_at = recommended_at
WHERE clicked = 1 AND clicked_at IS NULL;

UPDATE recommendation_history
SET learning_started = 1,
    started_at = COALESCE(started_at, completed_at, recommended_at)
WHERE learning_completed = 1;
