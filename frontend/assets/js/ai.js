//뒤로가기
document.querySelector('.back-btn').addEventListener('click', () => {
  window.history.back();
});

//  하단 네비게이션 
document.querySelector('[data-nav="mypage"]').addEventListener('click', () => {
  window.location.href = '../pages/mypage.html'; 
});

document.querySelector('[data-nav="home"]').addEventListener('click', () => {
  window.location.href = 'frontend/pages/Gameplay.html'; // 실제 주소로 바꾸기
});