const loginButton = document.getElementById("loginButton");
const signupButton = document.getElementById("signupButton");

const passwordInput = document.getElementById("password");
const passwordToggle = document.getElementById("passwordToggle");
const passwordEye = document.getElementById("passwordEye");


/* 비밀번호 보기/숨기기 */
passwordToggle.addEventListener("click", () => {

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        passwordEye.src = "../assets/img/eye_open.svg";
        passwordEye.alt = "비밀번호 숨기기";
        passwordToggle.setAttribute(
            "aria-label",
            "비밀번호 숨기기"
        );

    } else {
        passwordInput.type = "password";
        passwordEye.src = "../assets/img/eye_closed.svg";
        passwordEye.alt = "비밀번호 표시";
        passwordToggle.setAttribute(
            "aria-label",
            "비밀번호 표시"
        );
    }

});


/* 로그인 버튼 */
const loginError = document.getElementById("loginError");

loginButton.addEventListener("click", async () => {
    loginError.style.display = "none";

    const user_id = userIdInput.value.trim();
    const password = passwordInput.value;

    if (!user_id || !password) {
        loginError.textContent = "아이디와 비밀번호를 입력해주세요.";
        loginError.style.display = "block";
        return;
    }

    try {

        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id,
                password,
            }),
        });

        const data = await response.json();

        if (response.ok) {

            // JWT 저장
            localStorage.setItem("accessToken", data.access_token);

            // 게임 화면 이동
            window.location.href = "./Gameplay.html";

        } else {
            loginError.textContent = data.detail;
            loginError.style.display = "block";
        }

    } catch (error) {
        console.error(error);
        loginError.textContent = "서버와 연결할 수 없습니다.";
        loginError.style.display = "block";
    }

});


/* 회원가입 버튼 */
signupButton.addEventListener("click", () => {
    window.location.href = "./Signup.html";
});