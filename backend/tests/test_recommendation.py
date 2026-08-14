import unittest
from datetime import datetime, timezone

from pydantic import ValidationError
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.models.answer_attempt import AnswerAttempt
from app.models.history import History
from app.models.progress import Progress
from app.models.question import Question
from app.models.recommendation_history import RecommendationHistory
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User
from app.schemas.result import ResultRequest
from app.services.auth_service import login
from app.services.quiz_service import submit_answer
from app.services.recommend_service import get_recommendations
from app.services.recommendation_quiz_service import complete_recommendation_quiz
from app.services.recommendation_scoring import RecommendationSignals, calculate_recommendation_score
from app.services.result_service import save_result


class RecommendationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(login_id="tester", password=hash_password("123456"))
        self.db.add(self.user)
        self.db.flush()
        self._add_stage(1, "주식 기초", "주식", difficulty=1)
        self._add_stage(2, "주식 주문", "주식 주문 유형", difficulty=2)
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _add_stage(self, stage_id: int, title: str, tag: str, difficulty: int) -> None:
        self.db.add(
            Stage(
                stage_id=stage_id,
                title=title,
                description=f"{title} 기본 학습 콘텐츠",
                difficulty=difficulty,
            )
        )
        self.db.add(
            Question(
                question_id=stage_id,
                stage_id=stage_id,
                question=f"{title} 문제",
                choice1="정답",
                choice2="오답 1",
                choice3="오답 2",
                choice4="오답 3",
                answer=1,
                explanation=f"{title} 설명",
                difficulty=difficulty,
                tag=tag,
            )
        )

    def test_new_user_without_wrong_answers_gets_no_recommendation(self) -> None:
        items = get_recommendations(
            self.db,
            self.user.user_id,
            now=datetime(2026, 8, 4, tzinfo=timezone.utc),
        )

        self.assertEqual(items, [])

    def test_weak_stage_is_ranked_first(self) -> None:
        self.db.add(Progress(user_id=self.user.user_id, stage_id=1, cleared=True, score=10, accuracy=100))
        self.db.add_all(
            [
                AnswerAttempt(
                    user_id=self.user.user_id,
                    question_id=2,
                    stage_id=2,
                    selected_answer=2,
                    correct=False,
                    submission_id=f"wrong-{index}",
                )
                for index in range(3)
            ]
        )
        self.db.add(
            AnswerAttempt(
                user_id=self.user.user_id,
                question_id=1,
                stage_id=1,
                selected_answer=1,
                correct=True,
                submission_id="correct-stage-1",
            )
        )
        self.db.commit()

        items = get_recommendations(self.db, self.user.user_id)

        self.assertEqual(items[0]["stage_id"], 2)
        self.assertEqual(items[0]["wrong_count"], 3)
        self.assertEqual(items[0]["current_accuracy"], 0)
        self.assertIn("3회 오답", items[0]["recommendation_reason"])

    def test_same_cumulative_data_keeps_stable_ranking(self) -> None:
        self.db.add(Progress(user_id=self.user.user_id, stage_id=1, cleared=True, score=10, accuracy=100))
        self.db.add_all(
            [
                AnswerAttempt(
                    user_id=self.user.user_id,
                    question_id=stage_id,
                    stage_id=stage_id,
                    selected_answer=2,
                    correct=False,
                    submission_id=f"stable-wrong-{stage_id}",
                )
                for stage_id in (1, 2)
            ]
        )
        self.db.commit()
        now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)

        first = get_recommendations(self.db, self.user.user_id, limit=2, now=now)
        second = get_recommendations(self.db, self.user.user_id, limit=2, now=now)

        self.assertEqual(first[0]["stage_id"], 1)
        self.assertEqual(second[0]["stage_id"], 1)
        history_count = self.db.scalar(select(func.count()).select_from(RecommendationHistory))
        self.assertEqual(history_count, 4)

    def test_submission_id_prevents_duplicate_attempt(self) -> None:
        first = submit_answer(self.db, self.user.user_id, 1, 2, "same-submission-id")
        second = submit_answer(self.db, self.user.user_id, 1, 2, "same-submission-id")

        self.assertEqual(first["attempt_id"], second["attempt_id"])
        attempt_count = self.db.scalar(select(func.count()).select_from(AnswerAttempt))
        self.assertEqual(attempt_count, 1)

    def test_locked_stage_answer_and_result_are_rejected(self) -> None:
        with self.assertRaises(HTTPException) as answer_error:
            submit_answer(self.db, self.user.user_id, 2, 1, "locked-stage-answer")
        self.assertEqual(answer_error.exception.status_code, 403)

        with self.assertRaises(HTTPException) as result_error:
            save_result(self.db, self.user.user_id, 2, 10, 1, 1)
        self.assertEqual(result_error.exception.status_code, 403)

    def test_result_is_server_verified_idempotent_and_does_not_complete_recommendation(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "recommendation-baseline-wrong")
        recommendation = get_recommendations(self.db, self.user.user_id)[0]
        answer = submit_answer(
            self.db,
            self.user.user_id,
            1,
            1,
            "verified-answer-submission",
        )
        request = {
            "user_id": self.user.user_id,
            "stage_id": 1,
            "score": 10,
            "correct_count": 1,
            "total_question": 1,
            "answer_attempt_ids": [answer["attempt_id"]],
            "submission_id": "verified-result-submission",
        }

        first = save_result(self.db, **request)
        second = save_result(self.db, **request)

        self.assertEqual(first, second)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Result)), 1)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(History)), 1)
        attempt = self.db.get(AnswerAttempt, answer["attempt_id"])
        history = self.db.get(
            RecommendationHistory, recommendation["recommendation_id"]
        )
        self.assertIsNotNone(attempt.result_id)
        self.assertFalse(history.learning_completed)
        self.assertIsNone(history.completed_at)

    def test_tampered_score_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as error:
            save_result(self.db, self.user.user_id, 1, 20, 1, 1)
        self.assertEqual(error.exception.status_code, 422)

    def test_legacy_result_and_new_unfinalized_attempt_are_both_counted(self) -> None:
        self.db.add(
            Result(
                user_id=self.user.user_id,
                stage_id=1,
                score=0,
                correct_count=0,
                total_question=1,
            )
        )
        self.db.add(
            AnswerAttempt(
                user_id=self.user.user_id,
                question_id=1,
                stage_id=1,
                selected_answer=1,
                correct=True,
                submission_id="new-unfinalized-answer",
            )
        )
        self.db.commit()

        item = get_recommendations(self.db, self.user.user_id)[0]

        self.assertEqual(item["total_attempts"], 2)
        self.assertEqual(item["correct_count"], 1)
        self.assertEqual(item["wrong_count"], 1)

    def test_recommendation_click_and_completion_are_recorded(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "feedback-baseline-wrong")
        item = get_recommendations(self.db, self.user.user_id)[0]
        result = complete_recommendation_quiz(
            self.db,
            self.user.user_id,
            item["recommendation_id"],
            2,
            3,
        )
        history = self.db.get(RecommendationHistory, item["recommendation_id"])

        self.assertTrue(result["passed"])
        self.assertTrue(history.clicked)
        self.assertTrue(history.learning_completed)
        self.assertIsNotNone(history.completed_at)

    def test_login_and_result_validation_regression(self) -> None:
        user, token = login(self.db, "tester", "123456")
        self.assertEqual(user.user_id, self.user.user_id)
        self.assertTrue(token)
        with self.assertRaises(ValidationError):
            ResultRequest(
                user_id=self.user.user_id,
                stage_id=1,
                score=10,
                correct_count=2,
                total_question=1,
            )


class RecommendationScoringTestCase(unittest.TestCase):
    def test_more_wrong_and_lower_accuracy_raise_score(self) -> None:
        strong = calculate_recommendation_score(
            RecommendationSignals(
                wrong_count=1,
                total_attempts=5,
                accuracy=80,
                difficulty=1,
                progress_distance=0,
            )
        )
        weak = calculate_recommendation_score(
            RecommendationSignals(
                wrong_count=4,
                total_attempts=5,
                accuracy=20,
                difficulty=2,
                progress_distance=0,
                days_since_last_wrong=0,
            )
        )
        self.assertGreater(weak.total, strong.total)

    def test_invalid_counts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_recommendation_score(
                RecommendationSignals(
                    wrong_count=2,
                    total_attempts=1,
                    accuracy=0,
                    difficulty=1,
                    progress_distance=0,
                )
            )


if __name__ == "__main__":
    unittest.main()
