<<<<<<< HEAD
const editIdBtn = document.getElementById('editIdBtn');
const editIdModal = document.getElementById('editIdModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalCancelBtn = document.getElementById('modalCancelBtn');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');
const newIdInput = document.getElementById('newIdInput');
const charCount = document.getElementById('charCount');
const userId = document.getElementById('userId');
 
function openModal() {
  editIdModal.classList.add('is-open');
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
 
modalConfirmBtn.addEventListener('click', () => {
  const value = newIdInput.value.trim();
  if (value.length < 4) {
    alert('아이디는 4자 이상 입력해주세요.');
    return;
  }
  userId.textContent = value; 
  closeModal();
});
 
//뒤로가기
document.querySelector('.back-btn').addEventListener('click', () => {
  window.history.back();
});

//로그아웃
const logoutBtn = document.getElementById('logoutBtn');

logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('accessToken');
  window.location.href = './Login.html';
=======
const editIdBtn = document.getElementById('editIdBtn');
const editIdModal = document.getElementById('editIdModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalCancelBtn = document.getElementById('modalCancelBtn');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');
const newIdInput = document.getElementById('newIdInput');
const charCount = document.getElementById('charCount');
const userId = document.getElementById('userId');
const API_BASE = "http://127.0.0.1:8000";

// 로그인한 사용자 정보 불러오기
async function loadProfile() {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    window.location.href = './Login.html';
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/user`, {
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
    const response = await fetch(`${API_BASE}/user`, {
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
>>>>>>> origin/pre-develop
});