import unittest
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.models.question import Question
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User
from app.schemas.statistics import UserStatisticsResponse
from app.services.quiz_service import submit_answer
from app.services.recommend_service import (
    get_recommendations,
    record_recommendation_interaction,
)
from app.services.result_service import save_result
from app.services.statistics_service import (
    calculate_recommendation_quality_metrics,
    get_user_statistics,
)


class StatisticsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(login_id="statistics-user", password=hash_password("123456"))
        self.other_user = User(login_id="other-user", password=hash_password("123456"))
        self.db.add_all([self.user, self.other_user])
        self.db.flush()
        self.db.add(
            Stage(
                stage_id=1,
                title="주식 기초",
                description="주식 기초 학습",
                difficulty=1,
            )
        )
        self.db.add(
            Question(
                question_id=1,
                stage_id=1,
                question="주식 기초 문제",
                choice1="정답",
                choice2="오답 1",
                choice3="오답 2",
                choice4="오답 3",
                answer=1,
                explanation="설명",
                difficulty=1,
                tag="주식 기초",
            )
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_interactions_are_idempotent_and_owner_only(self) -> None:
        recommendation = get_recommendations(self.db, self.user.user_id)[0]
        recommendation_id = recommendation["recommendation_id"]
        completed_at = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)

        click = record_recommendation_interaction(
            self.db, self.user.user_id, recommendation_id, "click"
        )
        start = record_recommendation_interaction(
            self.db, self.user.user_id, recommendation_id, "start"
        )
        first_complete = record_recommendation_interaction(
            self.db,
            self.user.user_id,
            recommendation_id,
            "complete",
            now=completed_at,
        )
        duplicate_complete = record_recommendation_interaction(
            self.db,
            self.user.user_id,
            recommendation_id,
            "complete",
            now=completed_at + timedelta(days=1),
        )

        self.assertFalse(click.already_applied)
        self.assertFalse(start.already_applied)
        self.assertFalse(first_complete.already_applied)
        self.assertTrue(duplicate_complete.already_applied)
        self.assertEqual(
            duplicate_complete.history.completed_at.replace(tzinfo=timezone.utc),
            completed_at,
        )
        with self.assertRaises(HTTPException) as forbidden:
            record_recommendation_interaction(
                self.db, self.other_user.user_id, recommendation_id, "click"
            )
        self.assertEqual(forbidden.exception.status_code, 403)

    def test_completed_recommendation_without_post_quiz_is_pending(self) -> None:
        recommendation = get_recommendations(self.db, self.user.user_id)[0]
        record_recommendation_interaction(
            self.db,
            self.user.user_id,
            recommendation["recommendation_id"],
            "complete",
        )

        statistics = get_user_statistics(self.db, self.user.user_id)
        UserStatisticsResponse.model_validate(statistics)
        effect = statistics["recommendation_effectiveness"]["effects"][0]

        self.assertEqual(effect["status"], "pending")
        self.assertIsNone(effect["post_accuracy"])
        self.assertIsNone(effect["accuracy_change"])
        self.assertFalse(effect["retested_after_recommendation"])
        self.assertEqual(
            statistics["recommendation_effectiveness"]["pending_count"], 1
        )

    def test_statistics_measure_recommendation_improvement(self) -> None:
        baseline_time = datetime.now(timezone.utc) - timedelta(days=2)
        self.db.add(
            Result(
                user_id=self.user.user_id,
                stage_id=1,
                score=0,
                correct_count=0,
                total_question=1,
                created_at=baseline_time,
            )
        )
        self.db.commit()
        recommendation = get_recommendations(
            self.db,
            self.user.user_id,
            now=baseline_time + timedelta(days=1),
        )[0]
        answer = submit_answer(
            self.db,
            self.user.user_id,
            1,
            1,
            "statistics-correct-answer",
        )
        save_result(
            self.db,
            self.user.user_id,
            1,
            10,
            1,
            1,
            answer_attempt_ids=[answer["attempt_id"]],
            submission_id="statistics-result",
            recommendation_id=recommendation["recommendation_id"],
        )

        statistics = get_user_statistics(self.db, self.user.user_id)
        UserStatisticsResponse.model_validate(statistics)
        effect = statistics["recommendation_effectiveness"]["effects"][0]

        self.assertEqual(statistics["overall_accuracy"], 50.0)
        self.assertEqual(statistics["cumulative_score"], 10)
        self.assertEqual(statistics["weakest_topic"]["topic"], "주식 기초")
        self.assertEqual(statistics["most_improved_topic"]["accuracy_change"], 100.0)
        self.assertEqual(effect["status"], "measured")
        self.assertEqual(effect["baseline_accuracy"], 0.0)
        self.assertEqual(effect["post_accuracy"], 100.0)
        self.assertEqual(effect["accuracy_change"], 100.0)
        self.assertEqual(effect["score_change"], 10)
        self.assertEqual(effect["wrong_count_change"], -1)
        self.assertTrue(effect["retested_after_recommendation"])

    def test_operator_quality_metrics_are_calculated_without_public_route(self) -> None:
        recommendation = get_recommendations(self.db, self.user.user_id)[0]
        record_recommendation_interaction(
            self.db,
            self.user.user_id,
            recommendation["recommendation_id"],
            "complete",
        )

        metrics = calculate_recommendation_quality_metrics(self.db)

        self.assertEqual(metrics["recommendation_count"], 1)
        self.assertEqual(metrics["click_rate"], 100.0)
        self.assertEqual(metrics["completion_rate"], 100.0)
        self.assertEqual(metrics["retest_rate"], 0.0)
        self.assertEqual(metrics["top_recommendation_selection_rate"], 100.0)
        self.assertEqual(metrics["default_recommendation_completion_rate"], 100.0)
        self.assertIsNone(metrics["post_recommendation_improvement_rate"])


if __name__ == "__main__":
    unittest.main()
