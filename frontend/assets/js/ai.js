const token = localStorage.getItem("accessToken");

if (!token) {
    window.location.href = "./Login.html";
}

async function apiFetch(path, options = {}) {
    const response = await fetch(path, {
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

const todaySlot = document.querySelector('[data-slot="today-recommendation"]');
const todayCard = document.querySelector(".today-card");
const listCard = document.querySelector(".list-card");
const listRows = document.querySelectorAll(".list-row");
let recommendations = [];

function renderRecommendation(slot, item) {
    slot.innerHTML = "";

    const title = document.createElement("p");
    title.className = "rec-title";
    title.textContent = item.title;
    slot.appendChild(title);

    const desc = document.createElement("p");
    desc.className = "rec-desc";
    desc.textContent = `누적 오답률 ${item.wrong_rate}% · 오답 ${item.wrong_count}회 / 총 ${item.total_attempts}회`;
    slot.appendChild(desc);

    const reason = document.createElement("p");
    reason.className = "rec-reason";
    reason.textContent = item.recommendation_reason || "현재 학습 진도에 맞춰 추천했어요.";
    slot.appendChild(reason);
}

async function loadRecommendations() {
    try {
        const response = await apiFetch("/learning/recommend");
        if (!response.ok) return;

        const items = await response.json();
        recommendations = items;

        const todayButton = todayCard.querySelector('[data-action="start-today"]');
        todayCard.style.display = "";
        todayButton.style.display = "";
        listCard.style.display = "";
        listRows.forEach((row) => { row.style.display = ""; });

        if (!items.length) {
            todaySlot.textContent = "아직 추천할 학습이 없어요. 문제를 풀어보세요!";
            todayButton.style.display = "none";
            if (listCard) listCard.style.display = "none";
            return;
        }

        renderRecommendation(todaySlot, items[0]);
        todayCard.dataset.recommendationIndex = "0";

        const restItems = items.slice(1);
        listRows.forEach((row, index) => {
            const item = restItems[index];
            const slot = row.querySelector(".card-content");

            if (!item) {
                row.style.display = "none";
                return;
            }

            row.style.display = "";
            renderRecommendation(slot, item);
            row.dataset.recommendationIndex = String(index + 1);
        });

        if (!restItems.length && listCard) {
            listCard.style.display = "none";
        }
    } catch (error) {
        console.error(error);
    }
}

loadRecommendations();

async function startRecommendation(container) {
    const index = Number(container?.dataset.recommendationIndex);
    const item = recommendations[index];
    if (!item) return;
    RecommendationQuiz.open(item);
}

document.querySelector('[data-action="start-today"]').addEventListener("click", () => {
    startRecommendation(todayCard);
});

document.querySelectorAll('[data-action="start-item"]').forEach((button) => {
    button.addEventListener("click", () => startRecommendation(button.closest(".list-row")));
});

document.addEventListener("recommendation-quiz:finished", (event) => {
    if (event.detail?.passed) loadRecommendations();
});

//뒤로가기
document.querySelector('.back-btn').addEventListener('click', () => {
  smoothBack();
});

//  하단 네비게이션
document.querySelector('[data-nav="mypage"]').addEventListener('click', () => {
  smoothNavigate('../pages/mypage.html');
});

document.querySelector('[data-nav="home"]').addEventListener('click', () => {
  smoothNavigate('./Gameplay.html');
});
