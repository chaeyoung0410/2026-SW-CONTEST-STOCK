-- Apply after 003_recommendation_statistics_sqlite.sql.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS remedial_question_cache (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES user(user_id),
    source_question_id INTEGER NOT NULL REFERENCES question(question_id),
    stage_id INTEGER NOT NULL REFERENCES stage(stage_id),
    status VARCHAR(20) NOT NULL,
    payload_json TEXT NULL,
    model_name VARCHAR(100) NULL,
    retry_after DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT uq_remedial_cache_user_question UNIQUE (user_id, source_question_id),
    CONSTRAINT ck_remedial_cache_status
        CHECK (status IN ('pending', 'ready', 'unavailable'))
);

CREATE INDEX IF NOT EXISTS ix_remedial_cache_user_question
    ON remedial_question_cache (user_id, source_question_id);
