-- Apply after 001_ai_recommendation_mysql.sql.

ALTER TABLE result
    ADD COLUMN submission_id VARCHAR(64) NULL,
    ADD CONSTRAINT uq_result_user_submission UNIQUE (user_id, submission_id),
    ADD CONSTRAINT ck_result_score_nonnegative CHECK (score >= 0),
    ADD CONSTRAINT ck_result_correct_nonnegative CHECK (correct_count >= 0),
    ADD CONSTRAINT ck_result_total_positive CHECK (total_question > 0),
    ADD CONSTRAINT ck_result_correct_not_over_total CHECK (correct_count <= total_question);

ALTER TABLE answer_attempt
    ADD COLUMN result_id INT NULL,
    ADD CONSTRAINT fk_answer_attempt_result
        FOREIGN KEY (result_id) REFERENCES result(result_id),
    ADD INDEX ix_answer_attempt_result_id (result_id);
