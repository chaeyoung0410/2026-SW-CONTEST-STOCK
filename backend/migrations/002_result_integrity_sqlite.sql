-- Apply after 001_ai_recommendation_sqlite.sql.
PRAGMA foreign_keys = ON;

ALTER TABLE result ADD COLUMN submission_id VARCHAR(64) NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_result_user_submission
    ON result (user_id, submission_id);

ALTER TABLE answer_attempt
    ADD COLUMN result_id INTEGER NULL REFERENCES result(result_id);
CREATE INDEX IF NOT EXISTS ix_answer_attempt_result_id
    ON answer_attempt (result_id);
