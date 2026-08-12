# AI 추천학습 Gemini 퀴즈 API

## 추천 목록

`GET /learning/recommend`

인증 사용자의 누적 문제 풀이를 `AnswerAttempt` 중심으로 집계합니다. 오답률이 0%인
주제는 제외하고, 오답률 내림차순 → 오답 수 내림차순 → `stage_id` 오름차순으로
정렬한 상위 4개를 반환합니다.

응답에는 `weak_topic`, `wrong_rate`, `wrong_count`, `total_attempts`와
`recommendation_id`가 포함됩니다.

완료된 주제는 목록에서 제외됩니다. 단, 완료 시점 이후 같은 스테이지에서 새 오답이
발생하면 누적 오답률을 기준으로 다시 후보가 됩니다.

## 퀴즈 생성

`POST /learning/recommendations/{recommendation_id}/quiz`

추천 카드를 클릭했을 때 호출합니다. Gemini structured output으로 4지선다 3문제를
생성하며 문제 본문, 보기, 정답, 해설은 DB에 저장하지 않습니다.

```json
{
  "recommendation_id": 12,
  "stage_id": 3,
  "topic": "PER",
  "questions": [
    {
      "question": "PER에 대한 설명으로 알맞은 것은?",
      "choices": ["보기 1", "보기 2", "보기 3", "보기 4"],
      "correct_answer": 0,
      "explanation": "정답 해설"
    }
  ]
}
```

실제 `questions` 배열은 정확히 3개이며 `correct_answer`는 0 기반 인덱스입니다.
키 미설정·잘못된 출력·일반 SDK 오류는 `503`, Gemini rate limit은 `429`로 반환합니다.

## 완료 판정

`POST /learning/recommendations/{recommendation_id}/quiz/complete`

```json
{
  "correct_count": 2,
  "total_questions": 3
}
```

3문제 중 2문제 이상 정답이면 `RecommendationHistory.learning_completed`와
`completed_at`을 갱신합니다. 0~1문제 정답이면 완료하지 않습니다.

## 환경변수

```text
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite
```

API key는 백엔드 환경변수에서만 읽으며 프론트엔드에 전달하지 않습니다.
