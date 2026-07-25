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
loginButton.addEventListener("click", () => {
    window.location.href = "./Gameplay.html";
});


/* 회원가입 버튼 */
signupButton.addEventListener("click", () => {
    window.location.href = "./Signup.html";
});