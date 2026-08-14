import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.answer_attempt import AnswerAttempt
from app.models.progress import Progress
from app.models.question import Question
from app.models.recommendation_history import RecommendationHistory
from app.models.remedial_question_cache import RemedialQuestionCache
from app.models.stage import Stage
from app.models.user import User
from app.schemas.recommendation_quiz import GeminiRecommendationQuestionSet
from app.services.gemini_service import (
    GeminiRateLimitError,
    GeminiServiceError,
    RecommendationQuizSource,
    generate_recommendation_quiz,
)
from app.services.recommend_service import get_recommendations
from app.services.recommendation_quiz_service import (
    complete_recommendation_quiz,
    generate_quiz_for_recommendation,
)


def generated_payload() -> dict:
    return {
        "questions": [
            {
                "question": f"PER 학습 확인 문제 {index + 1}입니다. 올바른 보기는?",
                "choices": ["정답", "오답 A", "오답 B", "오답 C"],
                "correct_answer": 0,
                "explanation": "PER의 의미와 활용을 확인하는 해설입니다.",
            }
            for index in range(3)
        ]
    }


class RecommendationRankingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(login_id="ranking-user", password=hash_password("123456"))
        self.db.add(self.user)
        self.db.flush()
        for stage_id in range(1, 7):
            self.db.add(
                Stage(
                    stage_id=stage_id,
                    title=f"주제 {stage_id}",
                    description=f"주제 {stage_id} 설명",
                    difficulty=1,
                )
            )
            self.db.add(
                Question(
                    question_id=stage_id,
                    stage_id=stage_id,
                    question=f"주제 {stage_id} 문제",
                    choice1="정답",
                    choice2="오답 1",
                    choice3="오답 2",
                    choice4="오답 3",
                    answer=1,
                    explanation="설명",
                    difficulty=1,
                    tag=f"주제 {stage_id}",
                )
            )
            if stage_id < 6:
                self.db.add(
                    Progress(
                        user_id=self.user.user_id,
                        stage_id=stage_id,
                        cleared=True,
                        score=0,
                        accuracy=0,
                    )
                )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def add_attempts(
        self,
        stage_id: int,
        outcomes: list[bool],
        *,
        start: datetime | None = None,
    ) -> None:
        start = start or datetime(2026, 8, 1, tzinfo=timezone.utc)
        for index, correct in enumerate(outcomes):
            self.db.add(
                AnswerAttempt(
                    user_id=self.user.user_id,
                    question_id=stage_id,
                    stage_id=stage_id,
                    selected_answer=1 if correct else 2,
                    correct=correct,
                    submission_id=f"{stage_id}-{start.timestamp()}-{index}",
                    created_at=start + timedelta(seconds=index),
                )
            )
        self.db.commit()

    def test_zero_wrong_rate_is_excluded_and_cumulative_rates_are_sorted(self) -> None:
        self.add_attempts(1, [True, True])
        self.add_attempts(2, [False, False, False, True])  # 75%
        self.add_attempts(3, [False, True])  # 50%
        self.add_attempts(4, [False, False, True, True, True])  # 40%

        items = get_recommendations(self.db, self.user.user_id)

        self.assertEqual([item["stage_id"] for item in items], [2, 3, 4])
        self.assertEqual([item["wrong_rate"] for item in items], [75.0, 50.0, 40.0])
        self.assertNotIn(1, [item["stage_id"] for item in items])

    def test_only_top_four_are_returned_with_deterministic_ties(self) -> None:
        self.add_attempts(1, [False, True])
        self.add_attempts(2, [False, True])
        self.add_attempts(3, [False, False, True, True])
        self.add_attempts(4, [False, True, True])
        self.add_attempts(5, [False, True, True, True])

        items = get_recommendations(self.db, self.user.user_id)

        self.assertEqual(len(items), 4)
        # 1~3은 50% 동률이며 오답 수가 많은 3이 먼저, 이후 stage_id 순이다.
        self.assertEqual([item["stage_id"] for item in items], [3, 1, 2, 4])

    def test_repeated_play_is_accumulated_instead_of_using_latest_result(self) -> None:
        self.add_attempts(1, [False, False])
        self.add_attempts(
            1,
            [True, True, True],
            start=datetime(2026, 8, 2, tzinfo=timezone.utc),
        )

        item = get_recommendations(self.db, self.user.user_id)[0]

        self.assertEqual(item["total_attempts"], 5)
        self.assertEqual(item["wrong_count"], 2)
        self.assertEqual(item["wrong_rate"], 40.0)

    def test_completion_promotes_next_candidate_and_new_wrong_recommends_again(self) -> None:
        for stage_id in range(1, 6):
            self.add_attempts(stage_id, [False, True])
        first = get_recommendations(
            self.db,
            self.user.user_id,
            now=datetime(2026, 8, 5, tzinfo=timezone.utc),
        )
        self.assertEqual([item["stage_id"] for item in first], [1, 2, 3, 4])

        complete_recommendation_quiz(
            self.db,
            self.user.user_id,
            first[0]["recommendation_id"],
            2,
            3,
            now=datetime(2026, 8, 6, tzinfo=timezone.utc),
        )
        promoted = get_recommendations(
            self.db,
            self.user.user_id,
            now=datetime(2026, 8, 7, tzinfo=timezone.utc),
        )
        self.assertEqual([item["stage_id"] for item in promoted], [2, 3, 4, 5])

        self.add_attempts(
            1,
            [False],
            start=datetime(2026, 8, 8, tzinfo=timezone.utc),
        )
        reranked = get_recommendations(
            self.db,
            self.user.user_id,
            now=datetime(2026, 8, 9, tzinfo=timezone.utc),
        )
        self.assertEqual(reranked[0]["stage_id"], 1)


class RecommendationQuizTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(login_id="quiz-user", password=hash_password("123456"))
        self.db.add(self.user)
        self.db.flush()
        self.db.add(Stage(stage_id=1, title="PER", description="PER 설명", difficulty=2))
        self.db.add(
            Question(
                question_id=1,
                stage_id=1,
                question="PER 문제",
                choice1="정답",
                choice2="오답",
                choice3="오답2",
                choice4="오답3",
                answer=1,
                explanation="설명",
                difficulty=2,
                tag="PER",
            )
        )
        self.db.add(
            AnswerAttempt(
                user_id=self.user.user_id,
                question_id=1,
                stage_id=1,
                selected_answer=2,
                correct=False,
                submission_id="quiz-baseline-wrong",
            )
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def recommendation(self) -> dict:
        return get_recommendations(self.db, self.user.user_id)[0]

    def test_generation_returns_exactly_three_and_does_not_store_questions(self) -> None:
        item = self.recommendation()
        question_count = self.db.scalar(select(func.count()).select_from(Question))
        cache_count = self.db.scalar(select(func.count()).select_from(RemedialQuestionCache))

        result = generate_quiz_for_recommendation(
            self.db,
            self.user.user_id,
            item["recommendation_id"],
            generator=Mock(return_value=generated_payload()),
        )

        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Question)), question_count)
        self.assertEqual(
            self.db.scalar(select(func.count()).select_from(RemedialQuestionCache)),
            cache_count,
        )
        history = self.db.get(RecommendationHistory, item["recommendation_id"])
        self.assertTrue(history.clicked)
        self.assertTrue(history.learning_started)
        self.assertFalse(history.learning_completed)

    def test_two_or_three_correct_complete_learning(self) -> None:
        for correct_count in (2, 3):
            item = self.recommendation()
            result = complete_recommendation_quiz(
                self.db,
                self.user.user_id,
                item["recommendation_id"],
                correct_count,
                3,
            )
            self.assertTrue(result["passed"])
            self.assertTrue(result["learning_completed"])
            history = self.db.get(RecommendationHistory, item["recommendation_id"])
            self.assertIsNotNone(history.completed_at)
            # 다음 반복을 위해 완료 이후 새 오답을 만든다.
            history.completed_at = datetime(2026, 8, 1)
            self.db.add(
                AnswerAttempt(
                    user_id=self.user.user_id,
                    question_id=1,
                    stage_id=1,
                    selected_answer=2,
                    correct=False,
                    submission_id=f"new-wrong-{correct_count}",
                    created_at=datetime(2026, 8, 2),
                )
            )
            self.db.commit()

    def test_zero_or_one_correct_does_not_complete_learning(self) -> None:
        for correct_count in (0, 1):
            item = self.recommendation()
            result = complete_recommendation_quiz(
                self.db,
                self.user.user_id,
                item["recommendation_id"],
                correct_count,
                3,
            )
            self.assertFalse(result["passed"])
            self.assertFalse(result["learning_completed"])
            self.assertIn(
                item["stage_id"],
                [candidate["stage_id"] for candidate in get_recommendations(self.db, self.user.user_id)],
            )

    def test_invalid_gemini_output_and_failures_are_safe(self) -> None:
        item = self.recommendation()
        with self.assertRaises(HTTPException) as invalid:
            generate_quiz_for_recommendation(
                self.db,
                self.user.user_id,
                item["recommendation_id"],
                generator=Mock(return_value={"questions": generated_payload()["questions"][:2]}),
            )
        self.assertEqual(invalid.exception.status_code, 503)

        with self.assertRaises(HTTPException) as failed:
            generate_quiz_for_recommendation(
                self.db,
                self.user.user_id,
                item["recommendation_id"],
                generator=Mock(side_effect=GeminiServiceError("request_failed")),
            )
        self.assertEqual(failed.exception.status_code, 503)

    def test_general_quiz_has_no_gemini_generation_route(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertNotIn("/question/{question_id}/remedial", paths)
        self.assertIn("/learning/recommendations/{recommendation_id}/quiz", paths)


class GeminiStructuredOutputTestCase(unittest.TestCase):
    def test_schema_requires_three_distinct_valid_questions(self) -> None:
        with self.assertRaises(ValidationError):
            GeminiRecommendationQuestionSet.model_validate(
                {"questions": generated_payload()["questions"][:2]}
            )
        duplicate = generated_payload()
        duplicate["questions"][1] = duplicate["questions"][0]
        with self.assertRaises(ValidationError):
            GeminiRecommendationQuestionSet.model_validate(duplicate)

    def test_sdk_uses_json_schema_and_rate_limit_is_classified(self) -> None:
        response = type("Response", (), {"parsed": generated_payload(), "text": None})()
        models = Mock()
        models.generate_content.return_value = response
        client = type("Client", (), {"models": models})()
        source = RecommendationQuizSource(1, "PER", "설명", 2, "PER", ["예시"])

        result = generate_recommendation_quiz(
            source, api_key="test-key", model="test-model", client=client
        )
        self.assertEqual(len(result.questions), 3)
        self.assertIs(
            models.generate_content.call_args.kwargs["config"].response_schema,
            GeminiRecommendationQuestionSet,
        )

        class RateLimitError(Exception):
            code = 429
            status = "RESOURCE_EXHAUSTED"

        models.generate_content.side_effect = RateLimitError()
        with self.assertRaises(GeminiRateLimitError):
            generate_recommendation_quiz(
                source, api_key="test-key", model="test-model", client=client
            )


if __name__ == "__main__":
    unittest.main()
