CREATE TABLE IF NOT EXISTS answer_attempt (
    attempt_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id INT NULL,
    stage_id INT NOT NULL,
    selected_answer INT NULL,
    correct BOOLEAN NOT NULL,
    submission_id VARCHAR(64) NULL,
    created_at DATETIME(6) NOT NULL,
    CONSTRAINT uq_answer_attempt_user_submission UNIQUE (user_id, submission_id),
    CONSTRAINT ck_answer_attempt_selected_answer
        CHECK (selected_answer IS NULL OR selected_answer BETWEEN 1 AND 4),
    CONSTRAINT fk_answer_attempt_user FOREIGN KEY (user_id) REFERENCES user(user_id),
    CONSTRAINT fk_answer_attempt_question FOREIGN KEY (question_id) REFERENCES question(question_id),
    CONSTRAINT fk_answer_attempt_stage FOREIGN KEY (stage_id) REFERENCES stage(stage_id),
    INDEX ix_answer_attempt_user_stage_created (user_id, stage_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recommendation_history (
    recommendation_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stage_id INT NOT NULL,
    learning_id INT NULL,
    recommended_at DATETIME(6) NOT NULL,
    priority INT NOT NULL,
    recommendation_score DOUBLE NOT NULL,
    reason TEXT NOT NULL,
    clicked BOOLEAN NOT NULL DEFAULT FALSE,
    learning_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at DATETIME(6) NULL,
    CONSTRAINT ck_recommendation_priority_positive CHECK (priority >= 1),
    CONSTRAINT ck_recommendation_score_nonnegative CHECK (recommendation_score >= 0),
    CONSTRAINT fk_recommendation_user FOREIGN KEY (user_id) REFERENCES user(user_id),
    CONSTRAINT fk_recommendation_stage FOREIGN KEY (stage_id) REFERENCES stage(stage_id),
    CONSTRAINT fk_recommendation_learning FOREIGN KEY (learning_id) REFERENCES learning(learning_id),
    INDEX ix_recommendation_user_stage_time (user_id, stage_id, recommended_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
