# 2026-SW-CONTEST-STOCK

## 자수정가

> 게임과 생성형 AI를 활용한 주식·금융 기초 학습 서비스

## 프로젝트 소개

자수정가는 주식 투자를 처음 접하는 사용자가 게임을 진행하면서 금융 및 주식 기초 지식을 학습할 수 있도록 개발한 게임형 금융 학습 서비스입니다.

총 14개의 스테이지와 총 70개의 퀴즈로 구성되어 있으며, 사용자의 문제 풀이 데이터를 분석하여 취약한 학습 주제를 추천하고 Google Gemini API를 활용해 맞춤형 추가 문제를 생성합니다.

## 프로젝트 목적

* 금융·주식 학습의 진입장벽 완화
* 게임을 통한 금융 기초 지식 학습
* 사용자의 학습 결과를 기반으로 취약 주제 분석
* 생성형 AI를 활용한 개인 맞춤형 문제 제공

## 주요 기능

### 1. 게임 기반 금융 학습

총 14개의 스테이지를 통해 주식, 배당, ETF, 코스피, 분산투자 등의 금융 기초 개념을 학습합니다.

### 2. 퀴즈 및 해설

각 스테이지마다 5개의 객관식 문제가 제공되며, 문제 풀이 후 정답과 해설을 확인할 수 있습니다.

### 3. 취약 주제 분석

사용자의 문제 풀이 결과를 분석하여 오답률이 높은 취약 주제를 최대 4개까지 추천합니다.

### 4. AI 맞춤형 문제 생성

사용자가 취약 주제를 선택하면 Google Gemini API를 활용하여 해당 주제의 4지선다형 문제 3개를 생성합니다.

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

```text
2026-SW-CONTEST-STOCK/
├── backend/                 # FastAPI 서버
│   ├── app/
│   │   ├── main.py          # 앱 진입점
│   │   ├── core/            # 설정, 보안
│   │   ├── db/              # DB 세션, 초기화, 시드 데이터
│   │   ├── models/          # SQLAlchemy 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   └── api/routes/      # API 엔드포인트
│   ├── migrations/          # SQL 마이그레이션
│   └── tests/               # pytest 테스트
└── frontend/                # 정적 프론트엔드
    ├── pages/               # HTML 화면
    └── assets/              # JavaScript / CSS / 이미지
```

## 기술 스택

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite

### AI

* Google Gemini API

### Collaboration

* Git
* GitHub

## 실행 방법

### 1. 프로젝트 열기

Visual Studio Code에서 프로젝트 폴더를 열어줍니다.

### 2. 백엔드 폴더로 이동

```bash
cd backend
```

### 3. 가상환경 생성 및 활성화

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 5. 환경변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### macOS / Linux

```bash
cp .env.example .env
```

생성한 `.env` 파일에 발급받은 Gemini API Key를 입력합니다.

```env
GEMINI_API_KEY=발급받은_API_KEY
```

> `.env` 파일과 실제 API Key는 GitHub에 업로드하지 않습니다.

### 6. 서버 실행

```bash
python -m uvicorn app.main:app --reload
```

### 7. 서비스 접속

웹 브라우저에서 아래 주소로 접속합니다.

* http://127.0.0.1:8000

## 향후 발전 방향

### 1. 학습 추천 정확도 향상

더 많은 학습 데이터를 축적하여 사용자별 취약 주제 분석 및 추천의 정확도를 향상시킬 수 있습니다.

### 2. 개인별 문제 난이도 조절

사용자의 정답률과 학습 수준을 분석하여 사용자에게 적합한 난이도의 문제를 제공하는 기능으로 확장할 수 있습니다.

### 3. 학습 통계 기능 강화

사용자의 학습 이력과 성취도를 시각화하여 자신의 학습 진행 상황과 성장 정도를 확인할 수 있도록 발전시킬 수 있습니다.

## 팀원 및 역할

| 이름  | 담당       | 주요 역할               |
| --- | -------- | ------------------- |
| 김민진 | Frontend | AI 추천 학습 및 마이페이지 화면 구현  |
| 김서윤 | Frontend | 온보딩 및 게임 플레이 화면 구현  |
| 김한슬 | Backend  | 담당 API 및 기능을 입력해주세요 |
| 박채영 | Backend  | 담당 API 및 기능을 입력해주세요 |
