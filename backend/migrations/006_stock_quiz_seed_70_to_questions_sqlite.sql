-- Import 005_stock_quiz_seed_70_source_sqlite.sql's `quizzes` rows into the application's
-- `question` table while preserving existing question IDs referenced by
-- answer_attempt.
--
-- Prerequisite: load 005_stock_quiz_seed_70_source_sqlite.sql first so `quizzes` contains
-- exactly the intended 70 rows (5 rows for each stage).

PRAGMA foreign_keys = ON;

BEGIN IMMEDIATE;

CREATE TEMP TABLE quiz_ranked AS
SELECT
    id,
    stage,
    concept,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    CASE correct_answer
        WHEN 'A' THEN 1
        WHEN 'B' THEN 2
        WHEN 'C' THEN 3
        WHEN 'D' THEN 4
    END AS answer,
    explanation,
    difficulty,
    ROW_NUMBER() OVER (PARTITION BY stage ORDER BY id) AS stage_row
FROM quizzes;

CREATE TEMP TABLE existing_question_ranked AS
SELECT
    question_id,
    stage_id,
    ROW_NUMBER() OVER (PARTITION BY stage_id ORDER BY question_id) AS stage_row
FROM question;

-- Reuse existing question IDs per stage so historical foreign keys remain
-- valid. On the initial seed this updates two rows; on a repeat run it updates
-- all five rows without inserting duplicates.
UPDATE question
SET
    question = (
        SELECT q.question FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    choice1 = (
        SELECT q.option_a FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    choice2 = (
        SELECT q.option_b FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    choice3 = (
        SELECT q.option_c FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    choice4 = (
        SELECT q.option_d FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    answer = (
        SELECT q.answer FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    explanation = (
        SELECT q.explanation FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    difficulty = (
        SELECT q.difficulty FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    ),
    tag = (
        SELECT q.concept FROM quiz_ranked q
        JOIN existing_question_ranked e
          ON e.stage_id = q.stage AND e.stage_row = q.stage_row
        WHERE e.question_id = question.question_id
    )
WHERE question_id IN (SELECT question_id FROM existing_question_ranked WHERE stage_row <= 5);

INSERT INTO question (
    stage_id,
    question,
    choice1,
    choice2,
    choice3,
    choice4,
    answer,
    explanation,
    difficulty,
    tag
)
SELECT
    stage,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    answer,
    explanation,
    difficulty,
    concept
FROM quiz_ranked q
WHERE NOT EXISTS (
    SELECT 1
    FROM existing_question_ranked e
    WHERE e.stage_id = q.stage
      AND e.stage_row = q.stage_row
)
ORDER BY stage, stage_row;

DROP TABLE existing_question_ranked;
DROP TABLE quiz_ranked;

COMMIT;
