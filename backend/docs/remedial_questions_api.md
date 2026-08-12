# Gemini 추가 학습 문제 API

## 설정

실제 키는 Git에 포함하지 않고 `backend/.env`에만 저장합니다.

```dotenv
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=15
GEMINI_RETRY_COOLDOWN_SECONDS=300
GEMINI_RATE_LIMIT_COOLDOWN_SECONDS=900
```

`.env`는 프로젝트 루트 `.gitignore`에서 제외되어 있습니다.

## 요청 흐름

1. 기존 `POST /answer`로 답안을 제출합니다.
2. 응답의 `correct`가 `false`일 때만 원본 `question_id`로 아래 API를 호출합니다.
3. 서버는 인증 사용자에게 해당 문제의 `AnswerAttempt.correct = false` 기록이 있는지
   확인합니다. 클라이언트가 문제 본문이나 정답을 보내지 않습니다.

```http
POST /question/12/remedial
Authorization: Bearer <access_token>
```

성공 응답의 `correct_answer`는 생성 문제의 `choices` 배열에 대한 0 기반 인덱스입니다.

```json
{
  "questions": [
    {
      "question": "PER이 낮다는 사실만으로 판단하기 어려운 이유는 무엇일까요?",
      "choices": ["업종 차이가 있을 수 있어서", "주식 수가 항상 같아서", "배당이 금지되어서", "매출이 공개되지 않아서"],
      "correct_answer": 0,
      "explanation": "PER은 업종과 성장 기대에 따라 적정 수준이 달라 비교 기준이 필요합니다.",
      "topic": "PER"
    },
    {
      "question": "두 기업의 PER을 비교할 때 함께 살펴볼 항목으로 가장 적절한 것은?",
      "choices": ["성장성과 업종", "회사 로고", "주권 색상", "본사 층수"],
      "correct_answer": 0,
      "explanation": "PER 비교에는 이익 성장성과 업종 특성을 함께 고려해야 합니다.",
      "topic": "기업가치 평가"
    }
  ],
  "available": true,
  "cached": false,
  "message": null
}
```

같은 사용자가 같은 원본 문제로 다시 요청하면 저장된 결과를 반환하며 `cached`가
`true`가 됩니다. 키 누락, 타임아웃, 할당량 초과, API 오류, 검증 실패 시에는 기존
`/answer` 결과에 영향을 주지 않고 다음과 같이 빈 결과를 반환합니다.

Free Tier 호출량을 아끼기 위해 SDK 자동 재시도는 사용하지 않습니다. `429
RESOURCE_EXHAUSTED`가 발생하면 해당 사용자·원본 문제 조합은 기본 15분 동안 다시
호출하지 않으며, 성공한 결과는 만료 없이 재사용합니다.

```json
{
  "questions": [],
  "available": false,
  "cached": false,
  "message": "추가 학습 문제를 현재 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."
}
```

오답 기록이 없는 문제를 요청하면 `409 Conflict`, 존재하지 않는 문제는 `404 Not
Found`, 인증 정보가 없으면 `401 Unauthorized`입니다.

## 프런트 호출 예시

기존 `/answer` 응답을 받은 직후 별도 요청하므로 Gemini 장애가 답안 판정을 막지
않습니다.

```javascript
if (!result.correct) {
  const remedialResponse = await apiFetch(
    `/question/${question.question_id}/remedial`,
    { method: "POST" }
  );
  const remedial = await remedialResponse.json();
  if (remedial.available) {
    // remedial.questions 두 개를 추가 학습 UI에 전달
  }
}
```
