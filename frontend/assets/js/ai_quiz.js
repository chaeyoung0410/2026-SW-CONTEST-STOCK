// Gemini가 생성한 오답 복습 문제를 별도 팝업에서 풉니다.
// 문제 생성은 백엔드만 담당하며 API key나 원본 문제 내용은 브라우저로 보내지 않습니다.
const RemedialQuiz = (() => {
    let popup = null;
    let preparedQuestionId = null;
    let questions = [];
    let currentIndex = 0;
    let answered = false;
    let prepareSequence = 0;

    function ensurePopup() {
        if (popup) return popup;

        popup = document.createElement("div");
        popup.className = "remedial_popup";
        popup.setAttribute("role", "dialog");
        popup.setAttribute("aria-modal", "true");
        popup.setAttribute("aria-labelledby", "remedialQuestion");
        popup.innerHTML = `
            <div class="remedial_container">
                <button class="remedial_close" type="button" aria-label="닫기">&times;</button>

                <div class="remedial_header">
                    <span class="remedial_badge">AI 추가 학습</span>
                    <span id="remedialCounter">1 / 2</span>
                </div>
                <div class="remedial_progress_bg" aria-hidden="true">
                    <div class="remedial_progress_bar" id="remedialProgressBar"></div>
                </div>

                <section class="remedial_question_page">
                    <img class="remedial_character" src="../assets/img/quiz_character.png" alt="">
                    <p class="remedial_topic" id="remedialTopic"></p>
                    <h2 class="remedial_question" id="remedialQuestion"></h2>
                    <div class="remedial_options" id="remedialOptions"></div>
                </section>

                <section class="remedial_feedback" id="remedialFeedback" hidden>
                    <strong id="remedialFeedbackTitle"></strong>
                    <p id="remedialExplanation"></p>
                    <button class="remedial_next" id="remedialNextBtn" type="button"></button>
                </section>
            </div>
        `;
        document.body.appendChild(popup);

        popup.querySelector(".remedial_close").addEventListener("click", close);
        popup.querySelector("#remedialNextBtn").addEventListener("click", next);
        popup.addEventListener("click", (event) => {
            if (event.target === popup) close();
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && popup.classList.contains("is-open")) close();
        });

        return popup;
    }

    function isValidQuestion(item) {
        return item
            && typeof item.question === "string"
            && Array.isArray(item.choices)
            && item.choices.length === 4
            && Number.isInteger(item.correct_answer)
            && item.correct_answer >= 0
            && item.correct_answer <= 3;
    }

    async function prepare(questionId) {
        const requestSequence = ++prepareSequence;
        preparedQuestionId = Number(questionId);
        questions = [];

        try {
            const response = await apiFetch(`/question/${preparedQuestionId}/remedial`, {
                method: "POST",
            });
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                console.warn("AI 추가 문제 요청 실패", response.status, data.detail || "");
                return {
                    available: false,
                    message: "AI 추가 문제를 불러오지 못했습니다. 기존 학습은 계속할 수 있어요.",
                };
            }

            const received = Array.isArray(data.questions) ? data.questions : [];
            if (!data.available || received.length !== 2 || !received.every(isValidQuestion)) {
                return {
                    available: false,
                    message: data.message || "AI 추가 문제를 현재 사용할 수 없습니다.",
                };
            }

            if (requestSequence !== prepareSequence) {
                return { available: false, stale: true, message: "" };
            }
            questions = received;
            return { available: true, cached: Boolean(data.cached), message: data.message || null };
        } catch (error) {
            console.error("AI 추가 문제 네트워크 오류", error);
            return {
                available: false,
                message: "네트워크 문제로 AI 추가 문제를 불러오지 못했습니다.",
            };
        }
    }

    function open() {
        if (questions.length !== 2) return false;

        ensurePopup();
        currentIndex = 0;
        popup.classList.add("is-open");
        document.body.classList.add("remedial-open");
        renderQuestion();
        return true;
    }

    function close() {
        if (!popup) return;
        popup.classList.remove("is-open");
        document.body.classList.remove("remedial-open");
    }

    function reset() {
        prepareSequence += 1;
        preparedQuestionId = null;
        questions = [];
        currentIndex = 0;
        answered = false;
        close();
    }

    function renderQuestion() {
        const question = questions[currentIndex];
        answered = false;

        popup.querySelector("#remedialCounter").textContent = `${currentIndex + 1} / ${questions.length}`;
        popup.querySelector("#remedialProgressBar").style.width = `${((currentIndex + 1) / questions.length) * 100}%`;
        popup.querySelector("#remedialTopic").textContent = question.topic || "추가 학습";
        popup.querySelector("#remedialQuestion").textContent = question.question;
        popup.querySelector("#remedialFeedback").hidden = true;

        const optionsElement = popup.querySelector("#remedialOptions");
        optionsElement.innerHTML = "";
        question.choices.forEach((choice, choiceIndex) => {
            const button = document.createElement("button");
            button.className = "remedial_option";
            button.type = "button";
            button.textContent = choice;
            button.addEventListener("click", () => selectChoice(choiceIndex));
            optionsElement.appendChild(button);
        });
    }

    function selectChoice(selectedIndex) {
        if (answered) return;
        answered = true;

        const question = questions[currentIndex];
        const isCorrect = selectedIndex === question.correct_answer;
        const optionButtons = popup.querySelectorAll(".remedial_option");

        optionButtons.forEach((button, index) => {
            button.disabled = true;
            if (index === question.correct_answer) button.classList.add("is-correct");
            if (index === selectedIndex && !isCorrect) button.classList.add("is-wrong");
        });

        const feedback = popup.querySelector("#remedialFeedback");
        feedback.classList.toggle("is-correct", isCorrect);
        feedback.classList.toggle("is-wrong", !isCorrect);
        popup.querySelector("#remedialFeedbackTitle").textContent = isCorrect
            ? "정답이에요!"
            : "아쉬워요. 정답을 확인해 보세요.";
        popup.querySelector("#remedialExplanation").textContent = question.explanation || "";
        popup.querySelector("#remedialNextBtn").textContent = currentIndex + 1 < questions.length
            ? "다음 문제"
            : "추가 학습 완료";
        feedback.hidden = false;
    }

    function next() {
        if (!answered) return;
        if (currentIndex + 1 < questions.length) {
            currentIndex += 1;
            renderQuestion();
            return;
        }
        close();
        document.dispatchEvent(new CustomEvent("remedial:completed", {
            detail: { sourceQuestionId: preparedQuestionId },
        }));
    }

    return { prepare, open, reset };
})();
