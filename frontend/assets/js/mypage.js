const editIdBtn = document.getElementById('editIdBtn');
const editIdModal = document.getElementById('editIdModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalCancelBtn = document.getElementById('modalCancelBtn');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');
const newIdInput = document.getElementById('newIdInput');
const charCount = document.getElementById('charCount');
const userId = document.getElementById('userId');

// 로그인한 사용자 정보 불러오기
async function loadProfile() {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    window.location.href = './Login.html';
    return;
  }

  try {
    const response = await fetch('/user', {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      localStorage.removeItem('accessToken');
      window.location.href = './Login.html';
      return;
    }

    const data = await response.json();
    userId.textContent = data.login_id;
  } catch (error) {
    console.error(error);
  }
}

loadProfile();

// 경제 뉴스 불러오기
async function loadNews() {
  const adPlaceholder = document.getElementById('adPlaceholder');
  const token = localStorage.getItem('accessToken');
  if (!adPlaceholder || !token) return;

  try {
    const response = await fetch('/news', {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) return;

    const items = await response.json();
    adPlaceholder.innerHTML = '';

    if (!items.length) {
      const empty = document.createElement('p');
      empty.className = 'news-empty';
      empty.textContent = '지금은 불러올 뉴스가 없어요.';
      adPlaceholder.appendChild(empty);
      return;
    }

    items.forEach((item) => {
      const link = document.createElement('a');
      link.className = 'news-item';
      link.href = item.link;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      const title = document.createElement('span');
      title.textContent = item.title;
      link.appendChild(title);

      const date = document.createElement('span');
      date.className = 'news-date';
      const parsed = new Date(item.published);
      date.textContent = Number.isNaN(parsed.getTime())
        ? item.published
        : parsed.toLocaleString('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
      link.appendChild(date);

      adPlaceholder.appendChild(link);
    });
  } catch (error) {
    console.error(error);
  }
}

loadNews();

function openModal() {
  editIdModal.classList.add('is-open');
  replayMotion(editIdModal.querySelector('.modal-box'));
  newIdInput.value = '';
  charCount.textContent = '0 / 16';
  newIdInput.focus();
}

function closeModal() {
  editIdModal.classList.remove('is-open');
}

editIdBtn.addEventListener('click', openModal);
modalCloseBtn.addEventListener('click', closeModal);
modalCancelBtn.addEventListener('click', closeModal);

// 오버레이 바깥(어두운 영역) 클릭 시 닫기
editIdModal.addEventListener('click', (e) => {
  if (e.target === editIdModal) closeModal();
});

newIdInput.addEventListener('input', () => {
  charCount.textContent = `${newIdInput.value.length} / 16`;
});

modalConfirmBtn.addEventListener('click', async () => {
  const value = newIdInput.value.trim();
  if (value.length < 2) {
    alert('아이디는 2자 이상 입력해주세요.');
    return;
  }

  const token = localStorage.getItem('accessToken');

  try {
    const response = await fetch('/user', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ login_id: value }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || '아이디 변경에 실패했습니다.');
      return;
    }

    userId.textContent = data.login_id;
    closeModal();
  } catch (error) {
    console.error(error);
    alert('서버와 연결할 수 없습니다.');
  }
});

//뒤로가기
document.querySelector('.back-btn').addEventListener('click', () => {
  smoothBack();
});

//로그아웃
const logoutBtn = document.getElementById('logoutBtn');

logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('userId');
  smoothNavigate('./Login.html');
});
