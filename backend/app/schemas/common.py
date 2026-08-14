import re

# 아이디 형식: 영문(대소문자) + 숫자, 3~16자, 영문 최소 1자 포함
LOGIN_ID_PATTERN = re.compile(r"^(?=.*[A-Za-z])[A-Za-z0-9]{3,16}$")
LOGIN_ID_FORMAT_MESSAGE = "아이디는 영문, 숫자로 3~16자 입력해주세요. (영문 최소 1자 포함)"


# 아이디 형식(영문/숫자, 3~16자, 영문 최소 1자) 검증. 스키마의 field_validator에서 공용으로 사용
def validate_login_id_format(value: str) -> str:
    if not LOGIN_ID_PATTERN.match(value):
        raise ValueError(LOGIN_ID_FORMAT_MESSAGE)
    return value
