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
