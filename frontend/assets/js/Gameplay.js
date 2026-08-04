const token = localStorage.getItem("accessToken");
const userId = localStorage.getItem("userId");

if (!token || !userId) {
    window.location.href = "./Login.html";
}

const API_BASE = "http://127.0.0.1:8000";

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            ...(options.headers || {}),
        },
    });

    if (response.status === 401) {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("userId");
        window.location.href = "./Login.html";
        throw new Error("Unauthorized");
    }

    return response;
}

const popup = document.getElementById("quizPopup");

const quizPage = document.getElementById("quizPage");
const correctPage = document.getElementById("correctPage");
const wrongPage = document.getElementById("wrongPage");
const conceptPage = document.getElementById("conceptPage");

const quizQuestion = document.getElementById("quizQuestion");

const option1 = document.getElementById("option1");
const option2 = document.getElementById("option2");
const option3 = document.getElementById("option3");
const option4 = document.getElementById("option4");
const options = [option1, option2, option3, option4];

const progressBar = document.getElementById("progressBar");
const quizHeader = document.querySelector(".quiz_header");

const stages = document.querySelectorAll(".gameplay_stage");

const correctDesc = document.getElementById("correctDesc");
const correctAnswer = document.getElementById("correctAnswer");

const conceptName = document.getElementById("conceptName");
const conceptDescription = document.getElementById("conceptDescription");

const nextQuestionBtn = document.getElementById("nextQuestionBtn");
const retryStageBtn = document.getElementById("retryStageBtn");
const nextStageBtn = document.getElementById("nextStageBtn");
const conceptBtn = document.getElementById("conceptBtn");

const buildingProgressBar = document.getElementById("buildingProgressBar");
const buildingProgressText = document.getElementById("buildingProgressText");
const selectedAnswerText = document.getElementById("selectedAnswer");

const wrongBuildingProgressBar = document.getElementById("wrongBuildingProgressBar");
const wrongBuildingProgressText = document.getElementById("wrongBuildingProgressText");

const player = document.getElementById("playerCharacter");
const building = document.getElementById("myBuilding");
const buildingLevel = document.getElementById("buildingLevel");

const buildingProgressFill =
    document.getElementById("buildingProgressFill");

const buildingPercent =
    document.getElementById("buildingPercent");

const nextLevelList =
    document.getElementById("nextLevelList");

const TOTAL_STAGES = 14;

let stagesInfo = [];
let currentStageId = null;
let currentStageTitle = "";
let currentQuestions = [];
let currentQuestionIndex = 0;
let correctCount = 0;
let stageScore = 0;
let lastExplanation = "";
let lastConceptTag = "";

// 화면 전환 함수
function showQuiz() {
    quizHeader.style.display = "flex";

    quizPage.style.display = "block";
    correctPage.style.display = "none";
    wrongPage.style.display = "none";
    conceptPage.style.display = "none";
    replayMotion(quizPage);
}

function showCorrect() {
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "block";
    wrongPage.style.display = "none";
    conceptPage.style.display = "none";
    replayMotion(correctPage);
}

function showWrong() {
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "none";
    wrongPage.style.display = "block";
    conceptPage.style.display = "none";
    replayMotion(wrongPage);
}

function showConcept() {
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "none";
    wrongPage.style.display = "none";
    conceptPage.style.display = "flex";
    replayMotion(conceptPage);
}

// 캐릭터 이동
const stagePosition = {
    start: { x: -10, y: 570 },
    1: { x: 330, y: 565 },
    2: { x: 488, y: 567 },
    3: { x: 645, y: 577 },
    4: { x: 802, y: 581 },
    5: { x: 922, y: 515 },
    6: { x: 803, y: 425 },
    7: { x: 760, y: 310 },
    8: { x: 872, y: 225 },
    9: { x: 928, y: 110 },
    10: { x: 804, y: 27 },
    11: { x: 635, y: 25 },
    12: { x: 482, y: 27 },
    13: { x: 319, y: 34 },
    14: { x: 160, y: 0 }
};

function moveCharacter(stage) {
    const position = stagePosition[stage];

    if (!player || !position) return;

    player.classList.remove("start", "stage");

    if (stage === "start") {
        player.classList.add("start");
    } else {
        player.classList.add("stage");
    }

    player.style.display = "block";
    player.style.left = `${position.x}px`;
    player.style.top = `${position.y}px`;
}

function setOptionsEnabled(enabled) {
    options.forEach((btn) => {
        btn.disabled = !enabled;
    });
}

// 스테이지 잠금/클리어 상태 반영
function renderStageLocks() {
    stages.forEach((stageEl) => {
        const stageNum = Number(stageEl.dataset.stage);
        const info = stagesInfo.find((s) => s.stage_id === stageNum);

        stageEl.classList.toggle("locked", Boolean(info && info.locked));
        stageEl.classList.toggle("cleared", Boolean(info && info.cleared));
    });
}

async function loadStages() {
    try {
        const response = await apiFetch("/stage");
        if (!response.ok) return;

        stagesInfo = await response.json();
        renderStageLocks();

        const clearedStageIds = stagesInfo.filter((s) => s.cleared).map((s) => s.stage_id);
        const furthestCleared = clearedStageIds.length ? Math.max(...clearedStageIds) : 0;

        moveCharacter(furthestCleared > 0 ? furthestCleared : "start");
    } catch (error) {
        console.error(error);
    }
}

async function loadBuilding() {
    try {
        const response = await apiFetch("/building");
        if (!response.ok) return;

        const data = await response.json();
        building.src = `../assets/img/${data.image}`;
        buildingLevel.textContent = `Lv.${data.level}`;
        buildingProgressFill.style.width = `${data.progress}%`;
        buildingPercent.textContent = `${data.progress}%`;

        nextLevelList.innerHTML = "";

        data.next_features.forEach(feature => {
            nextLevelList.innerHTML += `<li>${feature}</li>`;
        });
    } catch (error) {
        console.error(error);
    }
}

async function startStage(stageId, stageTitle) {
    try {
        const response = await apiFetch(`/question/${stageId}`);

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            alert(data.detail || "문제를 불러올 수 없습니다.");
            return;
        }

        const questions = await response.json();
        if (!questions.length) {
            alert("아직 준비되지 않은 문제입니다.");
            return;
        }

        currentStageId = stageId;
        currentStageTitle = stageTitle;
        currentQuestions = questions;
        currentQuestionIndex = 0;
        correctCount = 0;
        stageScore = 0;

        popup.classList.add("active");
        loadQuestion();
    } catch (error) {
        console.error(error);
    }
}

function loadQuestion() {
    const question = currentQuestions[currentQuestionIndex];

    quizQuestion.textContent = question.question;
    options.forEach((btn, index) => {
        btn.textContent = question.choices[index];
    });
    setOptionsEnabled(true);

    progressBar.style.width = `${((currentQuestionIndex + 1) / currentQuestions.length) * 100}%`;

    showQuiz();
}

// 보기 클릭
options.forEach((button, index) => {
    button.addEventListener("click", async () => {
        const question = currentQuestions[currentQuestionIndex];
        const selectedIndex = index + 1;

        setOptionsEnabled(false);
        selectedAnswerText.textContent = question.choices[index];

        try {
            const response = await apiFetch("/answer", {
                method: "POST",
                body: JSON.stringify({
                    user_id: Number(userId),
                    question_id: question.question_id,
                    answer: selectedIndex,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.detail || "답안 제출에 실패했습니다.");
                setOptionsEnabled(true);
                return;
            }

            stageScore += result.score;
            lastExplanation = result.explanation;
            lastConceptTag = question.tag;

            if (result.correct) {
                correctCount += 1;
                correctDesc.textContent = result.explanation;
                updateCorrectProgress();
                showCorrect();
            } else {
                correctAnswer.textContent = result.correct_answer;
                updateWrongProgress();
                showWrong();
            }
        } catch (error) {
            console.error(error);
            setOptionsEnabled(true);
        }
    });
});

// 스테이지 내 다음 문제로, 마지막 문제면 결과 제출
async function advance() {
    if (currentQuestionIndex + 1 < currentQuestions.length) {
        currentQuestionIndex += 1;
        loadQuestion();
        return;
    }

    try {
        const response = await apiFetch("/result", {
            method: "POST",
            body: JSON.stringify({
                user_id: Number(userId),
                stage_id: currentStageId,
                score: stageScore,
                correct_count: correctCount,
                total_question: currentQuestions.length,
            }),
        });

        const result = await response.json();

        if (response.ok) {
            moveCharacter(currentStageId);
            await loadBuilding();
            await loadStages();

            if (result.stage_clear && currentStageId >= TOTAL_STAGES) {
                popup.classList.remove("active");
                smoothNavigate("./final.html");
                return;
            }
        } else {
            alert(result.detail || "결과 저장에 실패했습니다.");
        }
    } catch (error) {
        console.error(error);
    }

    popup.classList.remove("active");
}

// 정답 화면 -> 다음 문제/결과 제출
nextQuestionBtn.addEventListener("click", () => {
    advance();
});

// 오답 화면 -> 개념 설명
conceptBtn.addEventListener("click", () => {
    conceptName.textContent = lastConceptTag || currentStageTitle;
    conceptDescription.textContent = lastExplanation;
    showConcept();
});

// 다시 풀기 (현재 스테이지 처음부터)
retryStageBtn.addEventListener("click", () => {
    currentQuestionIndex = 0;
    correctCount = 0;
    stageScore = 0;
    loadQuestion();
});

// 다음 단계로 (다음 문제 또는 결과 제출)
nextStageBtn.addEventListener("click", () => {
    advance();
});

// 스테이지 클릭
stages.forEach((stageEl) => {
    stageEl.addEventListener("click", () => {
        const stageNum = Number(stageEl.dataset.stage);
        const info = stagesInfo.find((s) => s.stage_id === stageNum);

        if (info && info.locked) {
            alert("이전 단계를 먼저 클리어해주세요.");
            return;
        }

        startStage(stageNum, info ? info.title : `Stage ${stageNum}`);
    });
});

function updateCorrectProgress() {
    buildingProgressBar.style.width = `${(currentStageId / TOTAL_STAGES) * 100}%`;
    buildingProgressText.textContent = `${currentStageId} / ${TOTAL_STAGES}`;
}

function updateWrongProgress() {
    wrongBuildingProgressBar.style.width = `${(currentStageId / TOTAL_STAGES) * 100}%`;
    wrongBuildingProgressText.textContent = `${currentStageId} / ${TOTAL_STAGES}`;
}

popup.addEventListener("click", (e) => {
    if (e.target === popup) {
        popup.classList.remove("active");
    }
});

// 하단 네비게이션
document.querySelector('[data-nav="home"]').addEventListener("click", () => {
    smoothNavigate("./Gameplay.html");
});

document.querySelector('[data-nav="mypage"]').addEventListener("click", () => {
    smoothNavigate("./mypage.html");
});

document.querySelector('[data-nav="ai-recommend"]').addEventListener("click", () => {
    smoothNavigate("./ai.html");
});

moveCharacter("start");
loadStages();
loadBuilding();
