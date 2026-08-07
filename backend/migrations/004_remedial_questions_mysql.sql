-- Apply after 003_recommendation_statistics_mysql.sql.

CREATE TABLE IF NOT EXISTS remedial_question_cache (
    cache_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_question_id INT NOT NULL,
    stage_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    payload_json LONGTEXT NULL,
    model_name VARCHAR(100) NULL,
    retry_after DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    CONSTRAINT uq_remedial_cache_user_question UNIQUE (user_id, source_question_id),
    CONSTRAINT ck_remedial_cache_status
        CHECK (status IN ('pending', 'ready', 'unavailable')),
    CONSTRAINT fk_remedial_cache_user
        FOREIGN KEY (user_id) REFERENCES user(user_id),
    CONSTRAINT fk_remedial_cache_question
        FOREIGN KEY (source_question_id) REFERENCES question(question_id),
    CONSTRAINT fk_remedial_cache_stage
        FOREIGN KEY (stage_id) REFERENCES stage(stage_id),
    INDEX ix_remedial_cache_user_question (user_id, source_question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
