# 2026-SW-CONTEST-STOCK
# 자수정가

> 게임과 생성형 AI를 활용한 주식·금융 기초 학습 서비스

## 프로젝트 소개

자수정가는 주식 투자를 처음 접하는 사용자가 게임을 진행하면서
금융 및 주식 기초 지식을 학습할 수 있도록 개발한 게임형 금융 학습 서비스입니다.

총 14개의 스테이지와 스테이지별 70개의 퀴즈로 구성되어 있으며,
사용자의 문제 풀이 데이터를 분석하여 취약한 학습 주제를 추천하고
Gemini API를 활용해 맞춤형 추가 문제를 생성합니다.


## 프로젝트 목적

- 금융·주식 학습의 진입장벽 완화
- 게임을 통한 금융 기초 지식 학습
- 사용자의 학습 결과를 기반으로 취약 주제 분석
- 생성형 AI를 활용한 개인 맞춤형 문제 제공


## 주요 기능

### 1. 게임 기반 금융 학습

총 14개의 스테이지를 통해 주식, 배당, ETF,
코스피, 분산투자 등의 금융 기초 개념을 학습합니다.

### 2. 퀴즈 및 해설

각 스테이지마다 5개의 객관식 문제가 제공되며,
문제 풀이 후 정답과 해설을 확인할 수 있습니다.

### 3. 취약 주제 분석

사용자의 문제 풀이 결과를 분석하여
오답률이 높은 취약 주제를 최대 4개까지 추천합니다.

### 4. AI 맞춤형 문제 생성

사용자가 취약 주제를 선택하면 Gemini API를 활용하여
해당 주제의 4지선다형 문제 3개를 생성합니다.


## 학습 과정

```text
기본 학습
   ↓
문제 풀이
   ↓
학습 데이터 축적
   ↓
취약 주제 분석
   ↓
맞춤형 학습 추천
   ↓
Gemini API
   ↓
AI 맞춤 문제 생성
   ↓
추가 학습
```


## 프로젝트 구조

├── backend/                        FastAPI 서버 (Python)
│   ├── app/
│   │   ├── main.py                 앱 진입점 (라우터 등록, 정적 파일 서빙, 시작 시 DB 시딩)
│   │   ├── core/
│   │   │   ├── config.py           환경설정 (DB URL, JWT secret, Gemini API 설정)
│   │   │   └── security.py         비밀번호 해시, JWT 처리
│   │   ├── db/
│   │   │   ├── session.py          SQLAlchemy 엔진/세션
│   │   │   ├── init_db.py          테이블 생성
│   │   │   └── seed_data.py        스테이지 14개 + 문제 70개, 기본 유저(kim) 시드
│   │   ├── models/                 SQLAlchemy ORM 모델
│   │   │   ├── user, stage, question, progress, result, history
│   │   │   ├── answer_attempt, wrong_answer
│   │   │   └── recommendation_history, remedial_question_cache
│   │   ├── schemas/                Pydantic 요청/응답 스키마
│   │   │   ├── auth, user, common(아이디 형식 검증)
│   │   │   ├── quiz, stage, result, history, building, news, statistics
│   │   │   └── recommendation_quiz
│   │   ├── crud/                   DB 직접 접근 헬퍼 (user.py)
│   │   ├── services/                비즈니스 로직
│   │   │   ├── auth_service, quiz_service, result_service, stage_service
│   │   │   ├── building_service(건물 레벨), history_service, learning_service
│   │   │   ├── recommend_service / recommendation_quiz_service / recommendation_scoring
│   │   │   ├── gemini_service(AI 연동), news_service, statistics_service
│   │   └── api/routes/              FastAPI 라우터 (엔드포인트)
│   │       ├── auth, user, stage, quiz, result, learning
│   │       ├── building, history, news, statistics
│   ├── migrations/                  SQL 마이그레이션 (mysql/sqlite 쌍)
│   ├── tests/                       pytest 테스트 (추천 퀴즈, 통계)
│   ├── local.db                     로컬 SQLite DB (자동 생성)
│   └── requirements.txt
│
├── frontend/                        정적 프론트엔드
│   ├── pages/                       HTML 화면
│   │   ├── index.html, Login.html, Signup.html
│   │   ├── Gameplay.html(퀴즈/게임 진행), mypage.html, ai.html, final.html
│   ├── assets/
│   │   ├── js/                      화면별 스크립트 (Login, Signup, Gameplay, ai, ai_quiz, mypage, motion)
│   │   ├── css/                     화면별 스타일 + motion.css(공통 애니메이션)
│   │   └── img/                     캐릭터/아이콘 이미지
│
└── README.md / .gitignore


## 실행 방법

```text
1. Visual Studio Code로 폴더를 열어줍니다.
2. 프로젝트의 backend 폴더로 이동합니다.
   - cd backend
3. 가상환경을 생성하고 실행합니다.
   macOS / Linux)
   - python3 -m venv .venv
   - source .venv/bin/activate
   Windows)
   - python -m venv .venv
   - .venv\Scripts\activate
4. 필요한 라이브러리를 설치합니다.
   - pip install -r requirements.txt
5. .env.example 파일을 복사하여 .env 파일을 생성한 뒤 Gemini API Key를 입력합니다.
   - GEMINI_API_KEY=발급받은_API_KEY
6. 서버를 실행합니다.
   - uvicorn app.main:app --reload
7. 웹 브라우저에서 다음 주소로 접속합니다.
   - http://127.0.0.1:8000
```


## 향후 발전 방향

### 1. 학습 추천 정확도 향상
더 많은 학습 데이터를 축적하여 사용자별 취약 주제 분석 및 추천의 정확도를 향상시킬 수 있습니다.

### 2. 개인별 문제 난이도 조절
사용자의 정답률과 학습 수준을 분석하여 사용자에게 적합한 난이도의 문제를 제공하는 기능으로 확장할 수 있습니다

### 3. 학습 통계 기능 강화
사용자의 학습 이력과 성취도를 시각화하여 자신의 학습 진행 상황과 성장 정도를 확인할 수 있도록 발전시킬 수 있습니다.
