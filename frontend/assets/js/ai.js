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

function renderRecommendation(slot, item) {
    slot.innerHTML = "";

    const title = document.createElement("p");
    title.className = "rec-title";
    title.textContent = item.title;
    slot.appendChild(title);

    const desc = document.createElement("p");
    desc.className = "rec-desc";
    desc.textContent = item.content || "곧 학습 콘텐츠가 추가될 예정이에요.";
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

        if (!items.length) {
            todaySlot.textContent = "아직 추천할 학습이 없어요. 문제를 풀어보세요!";
            if (todayCard) {
                const startBtn = todayCard.querySelector('[data-action="start-today"]');
                if (startBtn) startBtn.style.display = "none";
            }
            if (listCard) listCard.style.display = "none";
            return;
        }

        renderRecommendation(todaySlot, items[0]);
        if (todayCard) todayCard.dataset.stageId = items[0].stage_id;
        if (todayCard) todayCard.dataset.recommendationId = items[0].recommendation_id;

        const restItems = items.slice(1);
        listRows.forEach((row, index) => {
            const item = restItems[index];
            const slot = row.querySelector(".card-content");
            const btn = row.querySelector('[data-action="start-item"]');

            if (!item) {
                row.style.display = "none";
                return;
            }

            row.style.display = "";
            renderRecommendation(slot, item);
            if (btn) btn.dataset.stageId = item.stage_id;
            row.dataset.stageId = item.stage_id;
            row.dataset.recommendationId = item.recommendation_id;
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
    const stageId = Number(container?.dataset.stageId);
    const recommendationId = Number(container?.dataset.recommendationId);
    if (!stageId) return;

    if (recommendationId) {
        try {
            await apiFetch(`/learning/recommendations/${recommendationId}`, {
                method: "PATCH",
                body: JSON.stringify({ clicked: true }),
            });
        } catch (error) {
            // 클릭 이력 저장 실패가 학습 시작 자체를 막지는 않는다.
            console.error(error);
        }
    }

    sessionStorage.setItem("recommendedStageId", String(stageId));
    smoothNavigate("./Gameplay.html");
}

document.querySelector('[data-action="start-today"]').addEventListener("click", () => {
    startRecommendation(todayCard);
});

document.querySelectorAll('[data-action="start-item"]').forEach((button) => {
    button.addEventListener("click", () => startRecommendation(button.closest(".list-row")));
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
