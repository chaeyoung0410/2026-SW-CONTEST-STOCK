const signupButton = document.getElementById("signupButton");
const loginBackButton = document.getElementById("loginBackButton");
const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("passwordConfirm");
const passwordToggle = document.getElementById("passwordToggle");
const passwordConfirmToggle = document.getElementById("passwordConfirmToggle");
const passwordEye = document.getElementById("passwordEye");
const passwordConfirmEye = document.getElementById("passwordConfirmEye");


/* 비밀번호 보기/숨기기 */
passwordToggle.addEventListener("click", () => {
    togglePassword(passwordInput, passwordEye, passwordToggle);
});

passwordConfirmToggle.addEventListener("click", () => {
    togglePassword(passwordConfirmInput, passwordConfirmEye, passwordConfirmToggle);
});


function togglePassword(input, eye, toggleButton) {

    if (input.type === "password") {

        input.type = "text";
        eye.src = "../assets/img/eye_open.svg";

        toggleButton.setAttribute(
            "aria-label",
            "비밀번호 숨기기"
        );

    } else {

        input.type = "password";
        eye.src = "../assets/img/eye_closed.svg";

        toggleButton.setAttribute(
            "aria-label",
            "비밀번호 표시"
        );

    }

}


/* 가입하기 버튼 */
signupButton.addEventListener("click", () => {
    window.location.href = "./Login.html";
});


/* 로그인으로 돌아가기 버튼 */
loginBackButton.addEventListener("click", () => {
    window.location.href = "./Login.html";
});

/* 입력창 전체 클릭 시 포커스 */
document.querySelectorAll(".input_box").forEach(box => {
    box.addEventListener("click", (e) => {

        // 눈 아이콘 클릭은 제외
        if (e.target.closest(".password_toggle")) return;

        const input = box.querySelector("input");
        if (input) {
            input.focus();
        }
    });
});