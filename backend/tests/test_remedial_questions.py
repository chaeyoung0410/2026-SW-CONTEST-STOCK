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
from app.models.answer_attempt import AnswerAttempt
from app.models.question import Question
from app.models.remedial_question_cache import RemedialQuestionCache
from app.models.stage import Stage
from app.models.user import User
from app.schemas.remedial import GeminiRemedialQuestionSet
from app.services.gemini_service import (
    GeminiNotConfiguredError,
    GeminiRateLimitError,
    GeminiServiceError,
    RemedialQuestionSource,
    generate_remedial_questions,
)
from app.services.quiz_service import submit_answer
from app.services.remedial_service import get_or_generate_remedial_questions


def valid_generated_payload() -> dict:
    return {
        "questions": [
            {
                "question": "PER이 낮은 기업을 평가할 때 함께 확인해야 할 것은?",
                "choices": ["업종과 성장성", "회사 로고", "주권 색상", "본사 층수"],
                "correct_answer": 0,
                "explanation": "PER은 업종과 성장 기대에 따라 적정 수준이 달라집니다.",
                "topic": "PER",
            },
            {
                "question": "이익이 감소한 기업의 PER이 갑자기 높아질 수 있는 이유는?",
                "choices": [
                    "주가 대비 이익이 줄어서",
                    "발행 주식이 사라져서",
                    "거래소가 폐장해서",
                    "배당이 늘어서",
                ],
                "correct_answer": 0,
                "explanation": "주가가 같아도 주당순이익이 줄면 PER은 높아질 수 있습니다.",
                "topic": "기업가치 평가",
            },
        ]
    }


class RemedialQuestionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(login_id="remedial-user", password=hash_password("123456"))
        self.db.add(self.user)
        self.db.add(
            Stage(
                stage_id=1,
                title="기업가치 평가",
                description="PER 등 기업가치 평가 지표를 학습합니다.",
                difficulty=2,
            )
        )
        self.db.add(
            Question(
                question_id=1,
                stage_id=1,
                question="PER은 무엇을 의미할까요?",
                choice1="주가를 주당순이익으로 나눈 값",
                choice2="주가를 주당순자산으로 나눈 값",
                choice3="배당금을 매출액으로 나눈 값",
                choice4="부채를 자본으로 나눈 값",
                answer=1,
                explanation="PER은 주가수익비율로 주가를 주당순이익으로 나눈 값입니다.",
                difficulty=2,
                tag="PER",
            )
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_correct_answer_does_not_call_generator(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 1, "correct-remedial-answer")
        generator = Mock(return_value=valid_generated_payload())

        with self.assertRaises(HTTPException) as error:
            get_or_generate_remedial_questions(
                self.db,
                self.user.user_id,
                1,
                generator=generator,
            )

        self.assertEqual(error.exception.status_code, 409)
        generator.assert_not_called()

    def test_wrong_answer_generates_valid_questions_and_reuses_cache(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "wrong-remedial-answer")
        generator = Mock(return_value=valid_generated_payload())

        first = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=generator,
        )
        second = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=generator,
        )

        self.assertTrue(first.available)
        self.assertFalse(first.cached)
        self.assertTrue(second.available)
        self.assertTrue(second.cached)
        self.assertEqual(len(first.questions), 2)
        self.assertTrue(all(len(item.choices) == 4 for item in first.questions))
        self.assertTrue(all(0 <= item.correct_answer <= 3 for item in first.questions))
        self.assertEqual(generator.call_count, 1)
        source = generator.call_args.args[0]
        self.assertEqual(source.stage_id, 1)
        self.assertEqual(source.topic, "PER")
        self.assertEqual(source.correct_answer_index, 0)
        self.assertEqual(
            self.db.scalar(select(func.count()).select_from(RemedialQuestionCache)),
            1,
        )

    def test_missing_api_key_returns_empty_result_without_breaking_answer(self) -> None:
        answer = submit_answer(
            self.db,
            self.user.user_id,
            1,
            2,
            "missing-key-wrong-answer",
        )
        generator = Mock(side_effect=GeminiNotConfiguredError("missing_api_key"))

        result = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=generator,
        )

        self.assertFalse(result.available)
        self.assertEqual(result.questions, [])
        self.assertIsNotNone(self.db.get(AnswerAttempt, answer["attempt_id"]))

    def test_gemini_failure_is_throttled_and_answer_remains_saved(self) -> None:
        answer = submit_answer(
            self.db,
            self.user.user_id,
            1,
            2,
            "api-failure-wrong-answer",
        )
        failing_generator = Mock(side_effect=GeminiServiceError("request_failed"))

        first = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=failing_generator,
        )
        second_generator = Mock(return_value=valid_generated_payload())
        second = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=second_generator,
        )

        self.assertFalse(first.available)
        self.assertFalse(second.available)
        self.assertTrue(second.cached)
        failing_generator.assert_called_once()
        second_generator.assert_not_called()
        self.assertFalse(self.db.get(AnswerAttempt, answer["attempt_id"]).correct)

    def test_rate_limit_returns_empty_result_and_uses_longer_cooldown(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "rate-limit-answer")
        now = datetime(2026, 8, 8, tzinfo=timezone.utc)

        result = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=Mock(side_effect=GeminiRateLimitError("rate_limited")),
            now=now,
        )
        cache = self.db.scalar(select(RemedialQuestionCache))

        self.assertFalse(result.available)
        self.assertIn("기존 게임", result.message)
        self.assertGreaterEqual(
            cache.retry_after.replace(tzinfo=timezone.utc),
            now + timedelta(minutes=15),
        )

    def test_insufficient_or_invalid_output_is_rejected(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "invalid-output-answer")
        invalid_payload = {"questions": valid_generated_payload()["questions"][:1]}

        result = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=Mock(return_value=invalid_payload),
        )

        self.assertFalse(result.available)
        self.assertEqual(result.questions, [])

    def test_exact_copy_of_source_question_is_rejected(self) -> None:
        submit_answer(self.db, self.user.user_id, 1, 2, "copied-output-answer")
        copied_payload = valid_generated_payload()
        copied_payload["questions"][0]["question"] = "PER은 무엇을 의미할까요?"

        result = get_or_generate_remedial_questions(
            self.db,
            self.user.user_id,
            1,
            generator=Mock(return_value=copied_payload),
        )

        self.assertFalse(result.available)
        self.assertEqual(result.questions, [])


class GeminiStructuredOutputTestCase(unittest.TestCase):
    def test_schema_rejects_duplicate_choices_and_invalid_index(self) -> None:
        payload = valid_generated_payload()
        payload["questions"][0]["choices"] = ["같음", "같음", "셋", "넷"]
        payload["questions"][0]["correct_answer"] = 4

        with self.assertRaises(ValidationError):
            GeminiRemedialQuestionSet.model_validate(payload)

    def test_sdk_response_is_validated_with_pydantic_schema(self) -> None:
        response = type(
            "Response",
            (),
            {"parsed": valid_generated_payload(), "text": None},
        )()
        models = Mock()
        models.generate_content.return_value = response
        client = type("Client", (), {"models": models})()
        source = RemedialQuestionSource(
            stage_id=1,
            stage_title="기업가치 평가",
            stage_description="PER 학습",
            stage_difficulty=2,
            question="PER은 무엇인가요?",
            choices=["정답", "오답1", "오답2", "오답3"],
            correct_answer_index=0,
            correct_answer_text="정답",
            topic="PER",
            explanation="PER 설명",
        )

        result = generate_remedial_questions(
            source,
            api_key="test-key",
            model="test-model",
            client=client,
        )

        self.assertEqual(len(result.questions), 2)
        call = models.generate_content.call_args
        self.assertEqual(call.kwargs["model"], "test-model")
        self.assertIs(
            call.kwargs["config"].response_schema,
            GeminiRemedialQuestionSet,
        )

    def test_sdk_429_is_classified_without_retrying_in_service(self) -> None:
        class RateLimitClientError(Exception):
            code = 429
            status = "RESOURCE_EXHAUSTED"

        models = Mock()
        models.generate_content.side_effect = RateLimitClientError()
        client = type("Client", (), {"models": models})()
        source = RemedialQuestionSource(
            stage_id=1,
            stage_title="기업가치 평가",
            stage_description="PER 학습",
            stage_difficulty=2,
            question="PER은 무엇인가요?",
            choices=["정답", "오답1", "오답2", "오답3"],
            correct_answer_index=0,
            correct_answer_text="정답",
            topic="PER",
            explanation="PER 설명",
        )

        with self.assertRaises(GeminiRateLimitError):
            generate_remedial_questions(
                source,
                api_key="test-key",
                model="test-model",
                client=client,
            )

        models.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
