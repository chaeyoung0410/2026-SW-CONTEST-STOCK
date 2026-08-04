# AI 학습 추천 API

모든 API는 `Authorization: Bearer <access_token>` 헤더가 필요합니다.

## 추천 조회

`GET /learning/recommend?limit=4`

- `limit`: 1~10, 기본값 4
- 기존 프론트 호환을 위해 `stage_id`, `title`, `content`, `pages`를 유지합니다.
- 조회된 추천은 `recommendation_history`에 노출 이력으로 저장됩니다.

```json
[
  {
    "stage_id": 4,
    "content_id": 4,
    "title": "주식 주문 유형",
    "content": "주식 주문 유형의 차이를 학습합니다.",
    "pages": [],
    "recommendation_id": 31,
    "priority": 1,
    "recommendation_score": 78.4,
    "recommendation_reason": "최근 주식 주문 유형 문제에서 3회 오답이 발생해 복습이 필요합니다.",
    "weak_topic": "주식 주문 유형",
    "current_accuracy": 40.0,
    "total_attempts": 5,
    "correct_count": 2,
    "wrong_count": 3,
    "difficulty": 2,
    "recently_recommended": false
  }
]
```

신규 사용자는 빈 배열 대신 현재 접근 가능한 가장 낮은 단계의 기본 콘텐츠를 받습니다.

## 추천 클릭·학습 완료 기록

`PATCH /learning/recommendations/{recommendation_id}`

요청 본문에는 하나 이상의 필드가 필요합니다.

```json
{
  "clicked": true,
  "learning_completed": true
}
```

```json
{
  "recommendation_id": 31,
  "clicked": true,
  "learning_completed": true,
  "completed_at": "2026-08-04T10:30:00Z"
}
```

다른 사용자의 추천 이력은 수정할 수 없습니다.

새 프론트는 상태별 POST API를 사용합니다. 기존 PATCH는 호환용으로 유지됩니다.

```text
POST /learning/recommendations/{recommendation_id}/click
POST /learning/recommendations/{recommendation_id}/start
POST /learning/recommendations/{recommendation_id}/complete
```

```json
{
  "recommendation_id": 31,
  "interaction": "complete",
  "already_applied": false,
  "clicked": true,
  "clicked_at": "2026-08-04T10:00:00Z",
  "learning_started": true,
  "started_at": "2026-08-04T10:05:00Z",
  "learning_completed": true,
  "completed_at": "2026-08-04T10:30:00Z"
}
```

같은 완료 요청을 다시 보내면 최초 `completed_at`을 유지하고
`already_applied=true`를 반환합니다.

## 답안 제출의 중복 방지

기존 `POST /answer` 요청은 그대로 지원하며 `submission_id`가 선택 필드로 추가됐습니다.

```json
{
  "user_id": 1,
  "question_id": 12,
  "answer": 2,
  "submission_id": "8603bf62-1e72-4e96-9dd8-5e0ca19e281d"
}
```

같은 사용자가 동일한 `submission_id`를 재전송하면 새로운 풀이 기록을 만들지 않고 최초
결과를 반환합니다. 동일 키를 다른 문제에 사용하면 `409 Conflict`를 반환합니다.

## 퀴즈 결과 확정과 추천 완료

기존 `POST /result` 필드는 그대로 지원하며, 새 프론트는 다음 선택 필드를 함께 보냅니다.

```json
{
  "user_id": 1,
  "stage_id": 2,
  "score": 10,
  "correct_count": 1,
  "total_question": 1,
  "answer_attempt_ids": [42],
  "submission_id": "d921c9d0-4162-4c1b-b20c-f12ea7ca629f",
  "recommendation_id": 31
}
```

- `answer_attempt_ids`가 있으면 서버 저장 답안으로 점수와 정답 수를 대조합니다.
- `submission_id` 재전송은 기존 결과를 반환하고 `result/history`를 중복 생성하지 않습니다.
- `recommendation_id`가 있으면 결과 저장과 같은 트랜잭션에서 추천 학습을 완료 처리합니다.
- 잠긴 단계, 실제 문제 수와 다른 `total_question`, 조작된 점수는 거부합니다.

## 사용자 학습 통계

`GET /users/me/statistics`

완료된 퀴즈 `result`를 기준으로 전체·최근 30일·단계별 통계를 계산합니다. 추천
효과는 추천 생성 당시 스냅샷과 추천에 연결된 결과를 비교합니다. 후속 결과가 없으면
효과 상태는 `pending`이고 후속 값과 변화량은 `null`입니다.

```json
{
  "total_attempts": 10,
  "correct_count": 7,
  "wrong_count": 3,
  "overall_accuracy": 70.0,
  "recent_accuracy": 80.0,
  "cumulative_score": 70,
  "recent_score_change": 10,
  "stages": [],
  "weakest_topic": {
    "stage_id": 2,
    "topic": "주식 주문 유형",
    "accuracy": 40.0,
    "wrong_count": 3,
    "accuracy_change": null
  },
  "most_improved_topic": null,
  "recommendations": {
    "recommended_count": 4,
    "clicked_count": 2,
    "started_count": 2,
    "completed_count": 1
  },
  "recommendation_effectiveness": {
    "completed_content_count": 1,
    "evaluated_count": 0,
    "pending_count": 1,
    "average_accuracy_change": null,
    "improved_recommendation_rate": null,
    "effects": []
  }
}
```

운영 품질 지표는 `statistics_service.calculate_recommendation_quality_metrics()`에서
계산하지만 관리자 권한 체계가 없어 공개 라우터는 추가하지 않았습니다.

## 추천 점수

점수 계산은 `app/services/recommendation_scoring.py`의 순수 함수로 분리되어 있습니다.

```text
점수 = 오답 횟수(최대 30)
     + 낮은 정답률(최대 25)
     + 난이도(최대 8)
     + 현재 진도 근접도(최대 15)
     + 최근 오답(최대 15)
     + 미학습 주제(7)
     - 최근 7일 추천 패널티(최대 12)
     - 최근 14일 완료 패널티(최대 18)
     - 직전 1순위 반복 패널티(10)
```

모든 패널티는 콘텐츠를 완전히 제외하지 않으며 최종 점수는 0 미만이 될 수 없습니다.
