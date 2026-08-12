// ============================================================
// AI 추천 퀴즈 팝업 (ai.html 전용)
// ============================================================
// 게임플레이 화면(Gameplay.js)의 퀴즈 로직과는 완전히 별개입니다.
// 이 팝업은 건물 성장(집 업그레이드)과 무관하게, 문제 하나를 풀고
// 결과를 확인하는 용도로만 씁니다.
//
// 사용법: <script src="../assets/js/quiz.js"></script> 로 불러온 뒤
//   Quiz.open({ stageId, recommendationId })
//
// ------------------------------------------------------------
// 백엔드 확인된 사항 (test_recommendation.py, 001_ai_recommendation_*.sql 기준)
// - 정답 선택지는 1~4로 인덱싱됨 (0~3 아님). answer_attempt.selected_answer
//   컬럼에 CHECK (selected_answer BETWEEN 1 AND 4) 제약이 걸려있음.
// - POST /answer 로 문제 하나를 채점하면 attempt_id가 생기고,
//   그 attempt_id를 POST /result 에 answer_attempt_ids로 실어 보내면
//   서버가 점수를 검증하고, recommendation_id가 있으면 같은 트랜잭션에서
//   추천을 완료 처리한다 (test_result_is_server_verified_idempotent_and_completes_recommendation).
//   -> 그래서 이 팝업은 완료 시 /learning/recommendations/{id}/complete 를
//      따로 부르지 않고 /result 하나로 끝낸다.
// - 진도가 안 된(잠긴) 스테이지에 답을 제출하면 403이 온다
//   (test_locked_stage_answer_and_result_are_rejected).
// ------------------------------------------------------------
// [TODO] 아직 확인 안 된 것 - quiz_service.py(또는 라우터 파일) 받으면 확정 필요
// 1) 문제 조회 엔드포인트의 정확한 경로/응답 필드명
//    (지금은 GET /stages/{stageId}/question 이라고 가정)
// 2) POST /answer 응답의 정확한 필드명
//    (지금은 attempt_id, correct, correct_answer, explanation, tag 라고 가정.
//     tag는 Question.tag를 개념명(concept_name)으로 사용한다고 가정)
// 3) score를 몇 점으로 보낼지의 정확한 규칙
//    (지금은 테스트 데이터의 예시값을 따라 정답 10점 / 오답 0점으로 가정)
// ------------------------------------------------------------
// 문제 조회: GET /stages/{stageId}/question
// {
//   "question_id": 12,
//   "question": "다음 중 주식의 정의로 옳은 것은?",
//   "options": [
//     "회사에 대한 소유권을 나타내는 증서",
//     "정부가 발행하는 채권",
//     "은행 예금 상품",
//     "부동산 등기 서류"
//   ]
// }
// ------------------------------------------------------------
// 정답 제출: POST /answer
// { "user_id": 1, "question_id": 12, "answer": 1, "submission_id": "uuid" }
// (answer는 1~4 중 하나)
//
// 응답 예시(가정):
// {
//   "attempt_id": 42,
//   "correct": true,
//   "correct_answer": 1,
//   "explanation": "주식은 주식회사에 대한 소유 지분을 나타내는 증서입니다.",
//   "tag": "주식"
// }
// ------------------------------------------------------------
// 결과 확정: POST /result
// {
//   "user_id": 1, "stage_id": 4, "score": 10,
//   "correct_count": 1, "total_question": 1,
//   "answer_attempt_ids": [42], "submission_id": "uuid",
//   "recommendation_id": 31
// }
// ============================================================

const Quiz = (() => {
  const QUESTION_API = (stageId) => `/stages/${stageId}/question`; // TODO: 실제 경로로 교체
  const ANSWER_API = "/answer";
  const RESULT_API = "/result";

  let popupEl = null;
  let ctx = {}; // 현재 세션 상태 (stageId, recommendationId, question, selectedAnswer, attemptId 등)

  function getUserId() {
    const id = localStorage.getItem("userId");
    return id ? Number(id) : null;
  }

  // ---------------- DOM 생성 ----------------
  function ensurePopup() {
    if (popupEl) return popupEl;

    popupEl = document.createElement("div");
    popupEl.className = "quiz_popup";
    popupEl.id = "quizPopup";
    popupEl.innerHTML = `
      <div class="quiz_container">

        <button class="quiz_popup_close" type="button" aria-label="닫기">&times;</button>

        <div class="quiz_header">
          <div class="quiz_progress_bg">
            <div class="quiz_progress_bar" id="progressBar"></div>
          </div>
        </div>

        <!-- 문제 화면 -->
        <div class="quiz_page" id="quizPage">
          <div class="quiz_character">
            <img src="../assets/img/quiz_character.png" alt="캐릭터">
          </div>
          <div class="quiz_content">
            <div class="quiz_question" id="quizQuestion">문제를 불러오는 중...</div>
            <div class="quiz_options">
              <button class="quiz_option" id="option1"></button>
              <button class="quiz_option" id="option2"></button>
              <button class="quiz_option" id="option3"></button>
              <button class="quiz_option" id="option4"></button>
            </div>
          </div>
        </div>

        <!-- 정답 화면 -->
        <div class="correct_page" id="correctPage">
          <div class="correct_ribbon">정답!</div>
          <div class="correct_card">
            <div class="result_character">
              <img src="../assets/img/correct_character.png" alt="정답 캐릭터">
            </div>
            <h2 class="result_title" id="correctText">정답이에요!</h2>
            <p class="result_desc" id="correctDesc"></p>
            <button class="result_btn" id="nextQuestionBtn">확인</button>
          </div>
        </div>

        <!-- 오답 화면 -->
        <div class="wrong_page" id="wrongPage">
          <div class="wrong_ribbon">아쉽게도 오답이에요!</div>
          <div class="wrong_card">
            <div class="wrong_character">
              <img src="../assets/img/wrong_character.png">
            </div>
            <div class="selected_answer">
              <span>선택한 답 : <span class="wrong" id="selectedAnswer"></span></span> ❌
            </div>
            <div class="correct_answer_box">
              정답은 <span class="correct" id="correctAnswer"></span> 입니다.
            </div>
            <button class="wrong_btn" id="conceptBtn">개념 설명 보기</button>
          </div>
        </div>

        <!-- 개념 설명 화면 -->
        <div class="concept_page" id="conceptPage">
          <div class="concept_character"></div>
          <h2 class="concept_title">개념 설명</h2>
          <div class="concept_box">
            <h3 id="conceptName"></h3>
            <p id="conceptDescription"></p>
          </div>

          <button type="button" class="result_btn" id="nextStageBtn">완료</button>

          <div class="concept_tip">
            <span class="tip_icon">💡</span>
            <div class="tip_content">
              <strong>TIP</strong>
              <p>처음 틀려도 괜찮아요!<br>많이 풀수록 더 많이 배울 수 있어요.</p>
            </div>
          </div>
        </div>

      </div>
    `;
    document.body.appendChild(popupEl);

    popupEl.querySelector(".quiz_popup_close").addEventListener("click", () => close());
    popupEl.querySelector("#nextStageBtn").addEventListener("click", finishAndClose);
    popupEl.querySelector("#nextQuestionBtn").addEventListener("click", finishAndClose);
    popupEl.querySelector("#conceptBtn").addEventListener("click", showConceptPage);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && popupEl.classList.contains("is-open")) close();
    });

    return popupEl;
  }

  // ---------------- 화면 전환 ----------------
  function showPage(pageId) {
    ["quizPage", "correctPage", "wrongPage", "conceptPage"].forEach((id) => {
      popupEl.querySelector(`#${id}`).classList.toggle("is-active", id === pageId);
    });
  }

  // ---------------- 열기/닫기 ----------------
  async function open({ stageId, recommendationId }) {
    ctx = {
      stageId,
      recommendationId,
      question: null,
      selectedAnswer: null, // 1~4
      attemptId: null,
      correct: null,
    };

    const popup = ensurePopup();
    popup.classList.add("is-open");
    document.body.style.overflow = "hidden";
    showPage("quizPage");
    setProgress(0);

    // 추천 학습 상태를 '시작됨'으로 기록 (추천 API 문서 기준)
    if (recommendationId) {
      apiFetchSafe(`/learning/recommendations/${recommendationId}/start`, { method: "POST" });
    }

    await loadQuestion(stageId);
  }

  function close() {
    if (!popupEl) return;
    popupEl.classList.remove("is-open");
    document.body.style.overflow = "";
    document.dispatchEvent(new CustomEvent("quiz:closed"));
  }

  // 문제를 끝까지 풀고 닫을 때: /result 로 결과를 확정하면서
  // recommendation_id가 있으면 서버가 같은 트랜잭션에서 추천을 완료 처리한다.
  async function finishAndClose() {
    await submitResult();
    close();
  }

  function showConceptPage() {
    const q = ctx.question;
    popupEl.querySelector("#conceptName").textContent = q?.concept_name || "";
    popupEl.querySelector("#conceptDescription").textContent = q?.concept_description || "";
    showPage("conceptPage");
  }

  function setProgress(percent) {
    popupEl.querySelector("#progressBar").style.width = `${percent}%`;
  }

  // ---------------- 문제 로드 ----------------
  async function loadQuestion(stageId) {
    const qEl = popupEl.querySelector("#quizQuestion");
    qEl.textContent = "문제를 불러오는 중...";
    [1, 2, 3, 4].forEach((n) => {
      popupEl.querySelector(`#option${n}`).textContent = "";
      popupEl.querySelector(`#option${n}`).disabled = true;
    });

    try {
      const res = await apiFetch(QUESTION_API(stageId));
      if (res.status === 403) {
        qEl.textContent = "아직 열리지 않은 단계예요. 이전 단계를 먼저 완료해주세요.";
        return;
      }
      if (!res.ok) throw new Error("문제 조회 실패");
      const data = await res.json();
      ctx.question = data;
      renderQuestion(data);
    } catch (err) {
      console.error(err);
      qEl.textContent = "문제를 불러오지 못했어요. 잠시 후 다시 시도해주세요.";
    }
  }

  function renderQuestion(data) {
    popupEl.querySelector("#quizQuestion").textContent = data.question;

    // options 배열은 0~3 인덱스지만, 서버로 보낼 answer 값은 1~4이다.
    data.options.forEach((text, i) => {
      const answerNumber = i + 1;
      const btn = popupEl.querySelector(`#option${answerNumber}`);
      btn.textContent = text;
      btn.disabled = false;
      btn.classList.remove("is-selected");
      btn.onclick = () => selectOption(answerNumber, btn);
    });
  }

  function selectOption(answerNumber, btn) {
    ctx.selectedAnswer = answerNumber; // 1~4
    popupEl.querySelectorAll(".quiz_option").forEach((b) => b.classList.remove("is-selected"));
    btn.classList.add("is-selected");
    submitAnswer();
  }

  // options 배열(0-indexed)에서 answer 번호(1~4)에 해당하는 텍스트를 찾는다.
  function optionText(answerNumber) {
    return ctx.question?.options?.[answerNumber - 1] ?? "";
  }

  // ---------------- 정답 제출 (POST /answer) ----------------
  async function submitAnswer() {
    const submissionId = crypto.randomUUID();

    try {
      const res = await apiFetch(ANSWER_API, {
        method: "POST",
        body: JSON.stringify({
          user_id: getUserId(),
          question_id: ctx.question.question_id,
          answer: ctx.selectedAnswer, // 1~4
          submission_id: submissionId,
        }),
      });
      if (res.status === 403) {
        alert("아직 열리지 않은 단계예요.");
        return;
      }
      if (!res.ok) throw new Error("제출 실패");
      const result = await res.json();

      ctx.attemptId = result.attempt_id;
      ctx.correct = result.correct;
      setProgress(100);

      if (result.correct) {
        popupEl.querySelector("#correctDesc").textContent = result.explanation || "";
        showPage("correctPage");
      } else {
        popupEl.querySelector("#selectedAnswer").textContent = optionText(ctx.selectedAnswer);
        popupEl.querySelector("#correctAnswer").textContent = optionText(result.correct_answer);
        // Question.tag를 개념명으로, explanation을 개념 설명으로 사용한다고 가정.
        ctx.question.concept_name = result.tag || "";
        ctx.question.concept_description = result.explanation || "";
        showPage("wrongPage");
      }
    } catch (err) {
      console.error(err);
      alert("제출에 실패했어요. 다시 시도해주세요.");
    }
  }

  // ---------------- 결과 확정 (POST /result) ----------------
  // recommendation_id를 같이 보내면 서버가 같은 트랜잭션에서 추천을 완료 처리한다.
  async function submitResult() {
    if (ctx.attemptId == null) return; // 문제를 아예 못 불러온 경우 등

    const submissionId = crypto.randomUUID();

    try {
      await apiFetch(RESULT_API, {
        method: "POST",
        body: JSON.stringify({
          user_id: getUserId(),
          stage_id: ctx.stageId,
          score: ctx.correct ? 10 : 0, // TODO: 정확한 점수 규칙 확인 필요
          correct_count: ctx.correct ? 1 : 0,
          total_question: 1,
          answer_attempt_ids: [ctx.attemptId],
          submission_id: submissionId,
          recommendation_id: ctx.recommendationId ?? undefined,
        }),
      });
    } catch (err) {
      // 결과 확정 실패가 팝업을 닫는 것 자체를 막지는 않는다.
      console.error(err);
    }
  }

  // ---------------- 공통 fetch 유틸 ----------------
  // ai.js에 이미 정의된 apiFetch(토큰 헤더 포함)를 그대로 재사용한다.
  async function apiFetchSafe(path, options) {
    try {
      return await apiFetch(path, options);
    } catch (err) {
      console.error(err);
      return null;
    }
  }

  return { open, close };
})();