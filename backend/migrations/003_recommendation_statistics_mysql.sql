-- Apply after 002_result_integrity_mysql.sql.

ALTER TABLE recommendation_history
    ADD COLUMN clicked_at DATETIME(6) NULL,
    ADD COLUMN learning_started BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN started_at DATETIME(6) NULL,
    ADD COLUMN baseline_accuracy DOUBLE NULL,
    ADD COLUMN baseline_score INT NULL,
    ADD COLUMN baseline_wrong_count INT NULL,
    ADD COLUMN completion_result_id INT NULL,
    ADD COLUMN is_default_recommendation BOOLEAN NOT NULL DEFAULT FALSE,
    ADD CONSTRAINT ck_recommendation_baseline_accuracy
        CHECK (baseline_accuracy IS NULL OR baseline_accuracy BETWEEN 0 AND 100),
    ADD CONSTRAINT ck_recommendation_baseline_score
        CHECK (baseline_score IS NULL OR baseline_score >= 0),
    ADD CONSTRAINT ck_recommendation_baseline_wrong_count
        CHECK (baseline_wrong_count IS NULL OR baseline_wrong_count >= 0),
    ADD CONSTRAINT fk_recommendation_completion_result
        FOREIGN KEY (completion_result_id) REFERENCES result(result_id),
    ADD INDEX ix_recommendation_completion_result_id (completion_result_id);

UPDATE recommendation_history
SET clicked_at = recommended_at
WHERE clicked = TRUE AND clicked_at IS NULL;

UPDATE recommendation_history
SET learning_started = TRUE,
    started_at = COALESCE(started_at, completed_at, recommended_at)
WHERE learning_completed = TRUE;
