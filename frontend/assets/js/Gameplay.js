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

const correctText = document.getElementById("correctText");
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

let currentStage = 1;
let unlockedStage = 1;

// 퀴즈 데이터 (임시)
const quizData = {

    1: [
        {
            question: "Q. 다음 중 주식이란 무엇일까요?",
            options: [
                "회사의 소유권일까요 아닐까요 일까요 아닐까요 일까요 아닐까요",
                "은행 예금",
                "보험 상품",
                "대출 상품"
            ],
            answer: 1,
            explanation: "정답이에요!",
            conceptTitle: "주식",
            conceptContent:
                "주식은 회사의 소유권을 나타내는 증권입니다."
        },
    ],

    2: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    3: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    4: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    5: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    6: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    7: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    8: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    9: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    10: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    11: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    12: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    13: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ],

    14: [
        {
            question: "PER은 무엇을 의미할까요?",
            options: [
                "주가수익비율",
                "배당금",
                "이자율",
                "환율"
            ],
            answer: 1,
            explanation: "정답입니다!",
            conceptTitle: "PER",
            conceptContent:
                "PER은 주가수익비율을 의미합니다."
        }
    ]
};

// 화면 전환 함수
// 화면 전환 함수
function showQuiz() {
    // 문제 화면에서는 상단 진행바 보이기
    quizHeader.style.display = "flex";

    quizPage.style.display = "block";
    correctPage.style.display = "none";
    wrongPage.style.display = "none";
    conceptPage.style.display = "none";
}

function showCorrect() {
    // 정답 화면에서는 상단 진행바 숨기기
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "block";
    wrongPage.style.display = "none";
    conceptPage.style.display = "none";
}

function showWrong() {
    // 오답 화면에서도 상단 진행바 숨기기
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "none";
    wrongPage.style.display = "block";
    conceptPage.style.display = "none";
}

function showConcept() {
    // 개념 설명 화면에서도 상단 진행바 숨기기
    quizHeader.style.display = "none";

    quizPage.style.display = "none";
    correctPage.style.display = "none";
    wrongPage.style.display = "none";
    conceptPage.style.display = "flex";
}

// 퀴즈 불러오기
function loadQuiz(stageNum) {
    currentStage = stageNum;
    const quiz = quizData[currentStage]?.[0];
    if (!quiz) {
        alert("아직 준비되지 않은 문제입니다.");
        return;
    }

    quizQuestion.textContent = quiz.question;

    option1.textContent = quiz.options[0];
    option2.textContent = quiz.options[1];
    option3.textContent = quiz.options[2];
    option4.textContent = quiz.options[3];

    correctText.textContent = quiz.explanation;

    correctAnswer.textContent =
        quiz.options[quiz.answer - 1];

    conceptName.textContent =
        quiz.conceptTitle;

    conceptDescription.textContent =
        quiz.conceptContent;

    progressBar.style.width =
        `${(currentStage / 14) * 100}%`;

    showQuiz();

}

// 보기 클릭
options.forEach((button, index) => {
    button.addEventListener("click", () => {
        const quiz = quizData[currentStage][0];
        const selectedIndex = index + 1;

        // 사용자가 선택한 답 표시
        selectedAnswerText.textContent = quiz.options[selectedIndex - 1];
        if (selectedIndex === quiz.answer) {
            updateCorrectProgress(currentStage);
            showCorrect();
        } else {
            updateWrongProgress(currentStage);
            showWrong();

        }
    });
});

// 정답 화면 -> 다음 문제
nextQuestionBtn.addEventListener("click", () => {
    moveCharacter(currentStage);
    updateBuilding(currentStage);
    const nextStage = currentStage + 1;
    unlockedStage = Math.max(unlockedStage, nextStage);

    if (quizData[nextStage]) {
        loadQuiz(nextStage);
    } else {
        popup.classList.remove("active");
    }
});

// 오답 화면 -> 개념 설명
conceptBtn.addEventListener("click", () => {
    showConcept();
});

// 다시 풀기
retryStageBtn.addEventListener("click", () => {
    loadQuiz(currentStage);
});

// 다음 단계로
nextStageBtn.addEventListener("click", () => {
    moveCharacter(currentStage);
    updateBuilding(currentStage);
    const nextStage = currentStage + 1;
    unlockedStage = Math.max(unlockedStage, nextStage);

    if (quizData[nextStage]) {
        loadQuiz(nextStage);
    } else {
        popup.classList.remove("active");
    }
});

// 스테이지 클릭
stages.forEach(stage => {
    stage.addEventListener("click", () => {
        const stageNum = Number(stage.dataset.stage);

        if (stageNum > unlockedStage) return;
        loadQuiz(stageNum);
        popup.classList.add("active");
    });
});

// 캐릭터 이동
const player = document.getElementById("playerCharacter");
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

    // 기존 클래스 제거
    player.classList.remove("start", "stage");

    // start와 스테이지 구분
    if (stage === "start") {
        player.classList.add("start");
    } else {
        player.classList.add("stage");
    }

    player.style.display = "block";
    player.style.left = `${position.x}px`;
    player.style.top = `${position.y}px`;
}
moveCharacter("start");


popup.addEventListener("click", (e) => {

    if (e.target === popup) {
        popup.classList.remove("active");
    }
});

//
const building = document.getElementById("myBuilding");
const buildingLevel = document.getElementById("buildingLevel");

function updateBuilding(stage) {
    building.src = `../assets/img/building_${stage}.png`;
    buildingLevel.textContent = `Lv.${stage}`;
}

function updateCorrectProgress(stage) {
    buildingProgressBar.style.width = `${(stage / 14) * 100}%`;
    buildingProgressText.textContent = `${stage} / 14`;
}

moveCharacter("start");
updateBuilding(0);

function updateWrongProgress(stage) {

    wrongBuildingProgressBar.style.width =
        `${(stage / 14) * 100}%`;

    wrongBuildingProgressText.textContent =
        `${stage} / 14`;
}

// 하단 네비게이션
document.querySelector('[data-nav="home"]').addEventListener("click", () => {
    window.location.href = "./Gameplay.html";
});

document.querySelector('[data-nav="mypage"]').addEventListener("click", () => {
    window.location.href = "./mypage.html";
});

document.querySelector('[data-nav="ai-recommend"]').addEventListener("click", () => {
    window.location.href = "./ai.html";
});