const signupButton = document.getElementById("signupButton");
const loginBackButton = document.getElementById("loginBackButton");
const userIdInput = document.getElementById("userId");
const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("passwordConfirm");
const passwordToggle = document.getElementById("passwordToggle");
const passwordConfirmToggle = document.getElementById("passwordConfirmToggle");
const passwordEye = document.getElementById("passwordEye");
const passwordConfirmEye = document.getElementById("passwordConfirmEye");
const signupError = document.getElementById("signupError");
const userIdMessage = document.getElementById("userIdMessage");

// 아이디 형식: 영문(대소문자) + 숫자, 3~16자, 영문 최소 1자 포함
const LOGIN_ID_PATTERN = /^(?=.*[A-Za-z])[A-Za-z0-9]{3,16}$/;
const LOGIN_ID_FORMAT_MESSAGE = "아이디는 영문, 숫자로 3~16자 입력해주세요. (영문 최소 1자 포함)";

/* 아이디 입력: 영문/숫자 외 문자는 즉시 제거하고, 형식에 맞는지 실시간으로 안내 */
userIdInput.addEventListener("input", () => {
    const filtered = userIdInput.value.replace(/[^A-Za-z0-9]/g, "");
    if (filtered !== userIdInput.value) {
        userIdInput.value = filtered;
    }

    if (!userIdInput.value) {
        userIdMessage.textContent = "영문, 숫자 3~16자 (영문 최소 1자 포함)";
        userIdMessage.classList.remove("success", "error");
        return;
    }

    const valid = LOGIN_ID_PATTERN.test(userIdInput.value);
    userIdMessage.textContent = valid ? "사용 가능한 형식이에요." : LOGIN_ID_FORMAT_MESSAGE;
    userIdMessage.classList.toggle("success", valid);
    userIdMessage.classList.toggle("error", !valid);
});


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
signupButton.addEventListener("click", async () => {
    signupError.style.display = "none";

    const login_id = userIdInput.value.trim();
    const password = passwordInput.value;
    const passwordConfirm = passwordConfirmInput.value;

    if (!login_id || !password || !passwordConfirm) {
        signupError.textContent = "모든 항목을 입력해주세요.";
        signupError.style.display = "block";
        return;
    }

    if (!LOGIN_ID_PATTERN.test(login_id)) {
        signupError.textContent = LOGIN_ID_FORMAT_MESSAGE;
        signupError.style.display = "block";
        return;
    }

    if (password !== passwordConfirm) {
        signupError.textContent = "비밀번호가 일치하지 않습니다.";
        signupError.style.display = "block";
        return;
    }

    try {
        const signupResponse = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ login_id, password }),
        });

        const signupData = await signupResponse.json();

        if (!signupResponse.ok) {
            signupError.textContent = signupData.detail || "회원가입에 실패했습니다.";
            signupError.style.display = "block";
            return;
        }

        // 가입 성공 시 바로 로그인 처리 후 게임 화면으로 이동
        const loginResponse = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ login_id, password }),
        });

        const loginData = await loginResponse.json();

        if (loginResponse.ok) {
            localStorage.setItem("accessToken", loginData.access_token);
            localStorage.setItem("userId", loginData.user_id);
            smoothNavigate("./Gameplay.html");
        } else {
            smoothNavigate("./Login.html");
        }

    } catch (error) {
        console.error(error);
        signupError.textContent = "서버와 연결할 수 없습니다.";
        signupError.style.display = "block";
    }
});


/* 로그인으로 돌아가기 버튼 */
loginBackButton.addEventListener("click", () => {
    smoothNavigate("./Login.html");
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
