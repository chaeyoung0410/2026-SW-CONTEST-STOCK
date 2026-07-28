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
});