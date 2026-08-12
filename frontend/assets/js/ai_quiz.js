// AI 추천학습 탭 전용 Gemini 퀴즈. 생성 문제는 브라우저 메모리에만 유지합니다.
const RecommendationQuiz = (() => {
    let popup = null;
    let recommendationId = null;
    let topic = "";
    let questions = [];
    let currentIndex = 0;
    let correctCount = 0;
    let answered = false;

    function ensurePopup() {
        if (popup) return popup;
        popup = document.createElement("div");
        popup.className = "remedial_popup";
        popup.setAttribute("role", "dialog");
        popup.setAttribute("aria-modal", "true");
        popup.innerHTML = `
            <div class="remedial_container">
                <button class="remedial_close" type="button" aria-label="닫기">&times;</button>
                <div class="remedial_loading" id="quizLoading">
                    <strong>AI가 맞춤 문제 3개를 만들고 있어요.</strong>
                    <p>잠시만 기다려 주세요.</p>
                </div>
                <div id="quizContent" hidden>
                    <div class="remedial_header">
                        <span class="remedial_badge" id="remedialTopic">AI 추천학습</span>
                        <span id="remedialCounter"></span>
                    </div>
                    <div class="remedial_progress_bg" aria-hidden="true">
                        <div class="remedial_progress_bar" id="remedialProgressBar"></div>
                    </div>
                    <section class="remedial_question_page">
                        <img class="remedial_character" src="../assets/img/quiz_character.png" alt="">
                        <h2 class="remedial_question" id="remedialQuestion"></h2>
                        <div class="remedial_options" id="remedialOptions"></div>
                    </section>
                    <section class="remedial_feedback" id="remedialFeedback" hidden>
                        <strong id="remedialFeedbackTitle"></strong>
                        <p id="remedialExplanation"></p>
                        <button class="remedial_next" id="remedialNextBtn" type="button"></button>
                    </section>
                </div>
                <section class="remedial_result" id="quizResult" hidden>
                    <h2 id="quizResultTitle"></h2>
                    <p id="quizResultDescription"></p>
                    <button class="remedial_next" id="quizResultBtn" type="button">확인</button>
                </section>
                <section class="remedial_error" id="quizError" hidden>
                    <strong>문제를 생성하지 못했어요.</strong>
                    <p id="quizErrorMessage"></p>
                    <button class="remedial_next" id="quizErrorBtn" type="button">닫기</button>
                </section>
            </div>
        `;
        document.body.appendChild(popup);
        popup.querySelector(".remedial_close").addEventListener("click", close);
        popup.querySelector("#quizErrorBtn").addEventListener("click", close);
        popup.querySelector("#quizResultBtn").addEventListener("click", close);
        popup.querySelector("#remedialNextBtn").addEventListener("click", next);
        popup.addEventListener("click", (event) => {
            if (event.target === popup) close();
        });
        return popup;
    }

    async function open(item) {
        ensurePopup();
        recommendationId = item.recommendation_id;
        topic = item.weak_topic || item.title;
        questions = [];
        currentIndex = 0;
        correctCount = 0;
        showOnly("quizLoading");
        popup.classList.add("is-open");
        document.body.classList.add("remedial-open");

        try {
            const response = await apiFetch(`/learning/recommendations/${recommendationId}/quiz`, {
                method: "POST",
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || "AI 문제를 생성하지 못했습니다.");
            if (!Array.isArray(data.questions) || data.questions.length !== 3) {
                throw new Error("생성된 문제 형식이 올바르지 않습니다.");
            }
            questions = data.questions;
            topic = data.topic || topic;
            showOnly("quizContent");
            renderQuestion();
        } catch (error) {
            popup.querySelector("#quizErrorMessage").textContent = error.message;
            showOnly("quizError");
        }
    }

    function showOnly(id) {
        ["quizLoading", "quizContent", "quizResult", "quizError"].forEach((target) => {
            popup.querySelector(`#${target}`).hidden = target !== id;
        });
    }

    function renderQuestion() {
        const question = questions[currentIndex];
        answered = false;
        popup.querySelector("#remedialTopic").textContent = topic;
        popup.querySelector("#remedialCounter").textContent = `${currentIndex + 1} / 3`;
        popup.querySelector("#remedialProgressBar").style.width = `${((currentIndex + 1) / 3) * 100}%`;
        popup.querySelector("#remedialQuestion").textContent = question.question;
        popup.querySelector("#remedialFeedback").hidden = true;

        const options = popup.querySelector("#remedialOptions");
        options.innerHTML = "";
        question.choices.forEach((choice, index) => {
            const button = document.createElement("button");
            button.className = "remedial_option";
            button.type = "button";
            button.textContent = choice;
            button.addEventListener("click", () => selectChoice(index));
            options.appendChild(button);
        });
    }

    function selectChoice(selectedIndex) {
        if (answered) return;
        answered = true;
        const question = questions[currentIndex];
        const correct = selectedIndex === question.correct_answer;
        if (correct) correctCount += 1;

        popup.querySelectorAll(".remedial_option").forEach((button, index) => {
            button.disabled = true;
            if (index === question.correct_answer) button.classList.add("is-correct");
            if (index === selectedIndex && !correct) button.classList.add("is-wrong");
        });
        popup.querySelector("#remedialFeedbackTitle").textContent = correct
            ? "정답이에요!"
            : "아쉬워요. 정답을 확인해 보세요.";
        popup.querySelector("#remedialExplanation").textContent = question.explanation;
        popup.querySelector("#remedialNextBtn").textContent = currentIndex < 2 ? "다음 문제" : "결과 보기";
        popup.querySelector("#remedialFeedback").hidden = false;
    }

    async function next() {
        if (!answered) return;
        if (currentIndex < 2) {
            currentIndex += 1;
            renderQuestion();
            return;
        }
        await submitResult();
    }

    async function submitResult() {
        try {
            const response = await apiFetch(
                `/learning/recommendations/${recommendationId}/quiz/complete`,
                {
                    method: "POST",
                    body: JSON.stringify({ correct_count: correctCount, total_questions: 3 }),
                },
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || "학습 결과를 저장하지 못했습니다.");

            popup.querySelector("#quizResultTitle").textContent = data.passed
                ? "추천학습 완료!"
                : "조금 더 복습해 볼까요?";
            popup.querySelector("#quizResultDescription").textContent = data.passed
                ? `3문제 중 ${correctCount}문제를 맞혔어요. 추천 목록을 새로 불러옵니다.`
                : `3문제 중 ${correctCount}문제를 맞혔어요. 2문제 이상 맞히면 완료됩니다.`;
            showOnly("quizResult");
            document.dispatchEvent(new CustomEvent("recommendation-quiz:finished", {
                detail: { passed: data.passed },
            }));
        } catch (error) {
            popup.querySelector("#quizErrorMessage").textContent = error.message;
            showOnly("quizError");
        }
    }

    function close() {
        if (!popup) return;
        popup.classList.remove("is-open");
        document.body.classList.remove("remedial-open");
    }

    return { open };
})();
