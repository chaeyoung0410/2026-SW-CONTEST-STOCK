PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS answer_attempt (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES user(user_id),
    question_id INTEGER NULL REFERENCES question(question_id),
    stage_id INTEGER NOT NULL REFERENCES stage(stage_id),
    selected_answer INTEGER NULL,
    correct BOOLEAN NOT NULL,
    submission_id VARCHAR(64) NULL,
    created_at DATETIME NOT NULL,
    CONSTRAINT uq_answer_attempt_user_submission UNIQUE (user_id, submission_id),
    CONSTRAINT ck_answer_attempt_selected_answer
        CHECK (selected_answer IS NULL OR selected_answer BETWEEN 1 AND 4)
);

CREATE INDEX IF NOT EXISTS ix_answer_attempt_user_stage_created
    ON answer_attempt (user_id, stage_id, created_at);

CREATE TABLE IF NOT EXISTS recommendation_history (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES user(user_id),
    stage_id INTEGER NOT NULL REFERENCES stage(stage_id),
    learning_id INTEGER NULL REFERENCES learning(learning_id),
    recommended_at DATETIME NOT NULL,
    priority INTEGER NOT NULL CHECK (priority >= 1),
    recommendation_score FLOAT NOT NULL CHECK (recommendation_score >= 0),
    reason TEXT NOT NULL,
    clicked BOOLEAN NOT NULL DEFAULT 0,
    learning_completed BOOLEAN NOT NULL DEFAULT 0,
    completed_at DATETIME NULL
);

CREATE INDEX IF NOT EXISTS ix_recommendation_user_stage_time
    ON recommendation_history (user_id, stage_id, recommended_at);
