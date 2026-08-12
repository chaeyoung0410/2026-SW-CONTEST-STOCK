# 프런트엔드 연동 명세 — Gemini 오답 추가 학습 문제

- 문서 버전: 1.0
- API 서버: FastAPI
- 로컬 Base URL: `http://127.0.0.1:8000`
- 인증 방식: `Authorization: Bearer <access_token>`

## 1. 기능 요약

사용자가 기존 퀴즈 문제를 틀린 경우, 서버가 DB에 저장된 원본 문제와 오답 기록을
확인한 뒤 Gemini로 관련 추가 문제 2개를 생성합니다.

프런트엔드는 원본 문제 본문, 정답, 해설 또는 Gemini API Key를 보내지 않습니다.
추가 문제 생성 요청에는 기존 문제의 `question_id`만 사용합니다.

```text
원본 문제 조회
  → 답안 제출
  → 서버 정답 판정 및 AnswerAttempt 저장
  → correct === false인 경우에만 추가 문제 요청
  → 생성 문제 2개 수신 또는 안전한 빈 결과 수신
```

Gemini 요청은 답안 제출과 분리되어 있습니다. 추가 문제 생성이 실패해도 기존 정답
판정, 점수 및 게임 진행을 취소하거나 재시도하면 안 됩니다.

## 2. 공통 요청 헤더

로그인 API에서 받은 `access_token`을 사용합니다. 현재 프런트는 토큰을
`localStorage.accessToken`에 저장합니다.

```http
Authorization: Bearer eyJ...
Content-Type: application/json
```

추가 문제 API는 요청 본문이 없으므로 `Content-Type`은 생략해도 됩니다.

## 3. 원본 문제 조회

### `GET /question/{stage_id}`

특정 스테이지의 기존 문제를 조회합니다.

#### 성공 응답: `200 OK`

```json
[
  {
    "question_id": 4,
    "question": "PER은 무엇을 의미할까요?",
    "choices": [
      "주가를 주당순이익으로 나눈 값",
      "주가를 주당순자산으로 나눈 값",
      "배당금을 매출액으로 나눈 값",
      "부채를 자본으로 나눈 값"
    ],
    "tag": "PER"
  }
]
```

원본 문제 응답에는 정답 인덱스가 포함되지 않습니다.

## 4. 기존 답안 제출

### `POST /answer`

#### 요청 본문

```json
{
  "user_id": 1,
  "question_id": 4,
  "answer": 2,
  "submission_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---:|:---:|---|
| `user_id` | number | O | 로그인 응답에서 받은 사용자 ID |
| `question_id` | number | O | 원본 문제 ID |
| `answer` | number | O | 기존 퀴즈 보기 번호, **1~4** |
| `submission_id` | string | 권장 | 중복 제출 방지용 8~64자 고유 값 |

#### 성공 응답: `200 OK`

```json
{
  "correct": false,
  "score": 0,
  "explanation": "PER은 주가수익비율입니다.",
  "correct_answer": "주가를 주당순이익으로 나눈 값",
  "attempt_id": 42
}
```

`correct === false`인 응답이 성공적으로 도착한 뒤에만 추가 문제 API를 호출합니다.
네트워크 오류나 `/answer` 실패 상태에서는 호출하지 않습니다.

## 5. 추가 학습 문제 생성/조회

### `POST /question/{question_id}/remedial`

인증된 현재 사용자에게 해당 원본 문제의 오답 기록이 있는지 서버가 직접 검사합니다.

#### 요청 예시

```http
POST /question/4/remedial HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer <access_token>
```

- 요청 본문: 없음
- `question_id`: 방금 제출한 원본 문제의 ID
- Gemini API Key와 내부 프롬프트는 프런트에서 취급하지 않음

#### 생성 성공: `200 OK`

```json
{
  "questions": [
    {
      "question": "PER이 낮은 기업을 비교할 때 함께 확인해야 할 요소는?",
      "choices": [
        "업종과 성장성",
        "회사 로고",
        "본사 층수",
        "주권 색상"
      ],
      "correct_answer": 0,
      "explanation": "PER은 업종과 성장 기대에 따라 적정 수준이 달라집니다.",
      "topic": "PER"
    },
    {
      "question": "순이익이 감소하면 PER이 높아질 수 있는 이유는?",
      "choices": [
        "주가 대비 이익이 줄기 때문에",
        "거래소가 폐장하기 때문에",
        "배당이 없어지기 때문에",
        "주식 이름이 바뀌기 때문에"
      ],
      "correct_answer": 0,
      "explanation": "주가가 같아도 주당순이익이 감소하면 PER은 높아질 수 있습니다.",
      "topic": "기업가치 평가"
    }
  ],
  "available": true,
  "cached": false,
  "message": null
}
```

### 생성 문제 필드

| 필드 | 타입 | 설명 |
|---|---:|---|
| `question` | string | 생성된 한국어 객관식 문제 |
| `choices` | string[4] | 중복되지 않는 보기 4개 |
| `correct_answer` | number | `choices` 기준 **0~3 인덱스** |
| `explanation` | string | 정답 근거와 개념 설명 |
| `topic` | string | 원본 `tag` 또는 밀접한 관련 개념 |

> 주의: 기존 `/answer` 요청의 `answer`는 1~4이고, 생성 문제의
> `correct_answer`는 배열 기준 0~3입니다.

### 캐시 응답

동일 사용자와 동일 `question_id`로 이미 생성된 문제가 있으면 Gemini를 호출하지 않고
같은 문제를 반환합니다.

응답 본문은 위의 생성 성공 응답과 동일하며 `cached`만 `true`로 바뀝니다.

`cached`는 표시 여부를 결정하는 값이 아닙니다. `available === true`이면 `cached` 값과
관계없이 `questions`를 표시합니다.

### Gemini 사용 불가: `200 OK`

키 누락, API 오류, timeout, 429 rate limit, 응답 검증 실패 또는 현재 다른 요청이 생성
중인 경우에도 HTTP 200으로 안전한 빈 결과를 반환할 수 있습니다.

```json
{
  "questions": [],
  "available": false,
  "cached": false,
  "message": "추가 학습 문제를 현재 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."
}
```

429 발생 시 메시지는 다음과 같을 수 있습니다.

```text
추가 학습 문제 요청이 잠시 많습니다. 기존 게임은 계속 이용할 수 있습니다.
```

프런트 처리 원칙:

- `available === false`: 추가 문제 영역을 숨기거나 `message`를 비차단 안내로 표시
- 기존 퀴즈 결과, 점수, 다음 문제 이동은 그대로 진행
- 프런트에서 즉시 반복 재시도하지 않음
- 서버가 일반 오류는 5분, 429는 15분 동안 재호출을 제한함

## 6. HTTP 오류 응답

| 상태 | 발생 조건 | 프런트 처리 |
|---:|---|---|
| `401` | 토큰 누락·만료·오류 | 토큰 삭제 후 로그인 화면 이동 |
| `404` | 존재하지 않는 `question_id` | 추가 문제 영역 숨김, 개발 로그 기록 |
| `409` | 현재 사용자에게 해당 문제의 오답 기록이 없음 | 추가 문제를 호출하지 않는 프런트 로직 점검 |
| `422` | 경로 또는 요청 형식 검증 실패 | 전달한 ID와 요청 형식 점검 |
| `500` | 예상하지 못한 서버 오류 | 게임 진행 유지, 추가 문제 영역만 실패 처리 |

FastAPI 오류 예시:

```json
{
  "detail": "Remedial questions require an incorrect answer"
}
```

## 7. TypeScript 타입

```typescript
export interface GeneratedRemedialQuestion {
  question: string;
  choices: [string, string, string, string];
  correct_answer: 0 | 1 | 2 | 3;
  explanation: string;
  topic: string;
}

export interface RemedialQuestionsResponse {
  questions: GeneratedRemedialQuestion[];
  available: boolean;
  cached: boolean;
  message: string | null;
}
```

런타임에서는 `available === true`일 때 `questions.length === 2`가 보장됩니다.

## 8. 권장 JavaScript 연동

기존 `Gameplay.js`의 `/answer` 성공 처리 이후에 연결합니다. 추가 문제 생성은 퀴즈
응답 화면을 막지 않도록 별도 함수에서 처리합니다.

```javascript
async function requestRemedialQuestions(questionId) {
  try {
    const response = await apiFetch(`/question/${questionId}/remedial`, {
      method: "POST",
    });

    if (!response.ok) {
      console.warn("추가 문제 요청 실패", response.status);
      return [];
    }

    const data = await response.json();

    if (!data.available) {
      console.info(data.message || "추가 문제를 현재 사용할 수 없습니다.");
      return [];
    }

    return data.questions;
  } catch (error) {
    console.error("추가 문제 네트워크 오류", error);
    return [];
  }
}
```

기존 답안 처리 코드에서는 다음과 같이 호출합니다.

```javascript
const result = await response.json();

if (!response.ok) {
  // 기존 오류 처리
  return;
}

if (!result.correct) {
  // 기존 오답 화면은 즉시 표시하고, 추가 문제는 별도로 불러옵니다.
  showWrong();
  const remedialQuestions = await requestRemedialQuestions(question.question_id);

  if (remedialQuestions.length === 2) {
    renderRemedialQuestions(remedialQuestions);
  }
}
```

`renderRemedialQuestions`는 프런트 팀이 결정한 UI에 맞춰 구현합니다. 생성 문제의 답을
프런트에서 판정할 경우 다음처럼 0 기반 인덱스를 비교합니다.

```javascript
const isCorrect = selectedChoiceIndex === question.correct_answer;
```

현재 생성 문제 풀이 결과를 서버 점수나 스테이지 진행도에 반영하는 별도 API는 없습니다.
추가 문제는 복습용이며 기존 `/answer` 또는 `/result`로 제출하지 않습니다.

## 9. 호출 제한 및 캐시 동작

- 성공 결과: 사용자+원본 문제 단위로 만료 없이 DB 재사용
- 동일 문제 동시 요청: 최초 요청만 생성권을 획득하고 나머지는 빈 결과를 받을 수 있음
- SDK 호출: 요청당 최대 1회, SDK 자동 재시도 사용 안 함
- 일반 실패: 기본 5분 쿨다운
- 429 rate limit: 기본 15분 쿨다운
- 페이지 새로고침: 성공 캐시가 있으면 추가 API 비용 없이 같은 문제 반환

프런트는 자체 반복 타이머나 자동 재시도 루프를 추가하지 않는 것을 권장합니다.

## 10. 프런트 확인 체크리스트

- [ ] `/answer`가 성공하고 `correct === false`일 때만 추가 API를 호출한다.
- [ ] 요청에 문제 본문·정답·Gemini API Key를 포함하지 않는다.
- [ ] 생성 문제의 정답 인덱스를 0~3으로 처리한다.
- [ ] `available === false`가 게임 진행을 막지 않는다.
- [ ] `cached === true`인 성공 응답도 정상 표시한다.
- [ ] `401`에서 기존 로그인 만료 처리를 적용한다.
- [ ] 429/일반 실패 응답을 프런트에서 자동 반복 호출하지 않는다.
- [ ] 추가 문제를 기존 `/answer` 또는 `/result`로 제출하지 않는다.
