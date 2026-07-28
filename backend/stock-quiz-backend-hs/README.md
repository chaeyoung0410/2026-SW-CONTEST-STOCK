# 주식 학습 게임 API v2

API 명세서(1~8번 화면)를 그대로 구현한 백엔드입니다. MySQL을 사용합니다.

## 실행 방법

```bash
# 1. MySQL에 DB/계정 준비 (한 번만)
mysql -u root -e "
CREATE DATABASE stock_learning_v2 CHARACTER SET utf8mb4;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY '원하는비밀번호';
GRANT ALL PRIVILEGES ON stock_learning_v2.* TO 'appuser'@'localhost';
"

# 2. app/database.py 에서 DB_PASSWORD를 위에서 정한 비밀번호로 수정

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 15단계 데모 데이터 넣기 (단계별 학습내용 + 문제 1~2개씩)
python -m app.seed_data

# 5. 서버 실행
uvicorn app.main:app --reload
```

`http://localhost:8000/docs` 에서 API 문서를 보고 바로 테스트할 수 있습니다.

## API 명세서와의 매핑

| 화면 | 엔드포인트 |
|---|---|
| 2. 회원가입 | `GET /auth/check-id`, `POST /auth/signup` |
| 3. 로그인 | `POST /auth/login` |
| 4. 게임 화면 | `GET /game/board`, `GET /learning/{step}/summary` |
| 5. 문제 풀이 | `GET /learning/{step}/content`, `GET /learning/{step}/questions`, `POST /learning/{step}/questions/{question_id}/submit` |
| 7. 결과 화면 | `GET /learning/{step}/result`, `POST /learning/{step}/complete` |
| 8. 마이페이지 | `GET /users/me`, `GET /users/me/buildings`, `GET /users/me/history`, `POST /auth/logout` |

## 주요 설계 포인트

- **재도전 지원**: 같은 문제를 다시 풀면 이전 기록을 덮어씁니다 (`question_attempts` 테이블에 유저+문제 조합당 1행만 유지).
- **레벨업 중복 방지**: `complete` 호출 시, 그 단계가 "현재 진행 중인 단계(progress.level)"일 때만 레벨업합니다. 이미 깬 단계를 복습 삼아 다시 풀어도 레벨이 중복으로 오르지 않습니다.
- **점수 계산**: 단계 완료 시 `맞춘 문제 수 × 10점`이 총점에 더해집니다. 필요하면 `app/routers/learning.py`의 `complete_stage` 함수에서 점수 공식을 바꾸시면 됩니다.
