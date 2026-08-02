from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.question import Question
from app.models.stage import Stage
from app.models.user import User

DEFAULT_USER_LOGIN_ID = "kim"
DEFAULT_USER_PASSWORD = "123456"

STAGES = [
    {
        "stage_id": 1,
        "title": "주식이란",
        "tag": "주식",
        "question": "주식이란 무엇을 의미할까요?",
        "choices": ["회사의 빚", "회사의 소유권 일부", "은행 예금", "회사의 매출"],
        "answer": 2,
        "explanation": "주식은 회사의 소유권 일부를 나타내는 증권이에요. 주식을 가지고 있으면 그 회사의 주인 중 한 명이 되는 거예요.",
    },
    {
        "stage_id": 2,
        "title": "배당금",
        "tag": "배당금",
        "question": "기업의 이익 일부를 주주에게 나누어 주는 것을 무엇이라고 할까요?",
        "choices": ["배당금", "증거금", "예수금", "액면가"],
        "answer": 1,
        "explanation": "배당금은 기업이 벌어들인 이익의 일부를 주주들에게 나누어 주는 돈이에요.",
    },
    {
        "stage_id": 3,
        "title": "ETF",
        "tag": "ETF",
        "question": "ETF에 대한 설명으로 가장 알맞은 것은?",
        "choices": ["한 회사의 주식만 사는 상품", "여러 종목을 묶어서 투자하는 상품", "채권만 투자하는 상품", "예금상품"],
        "answer": 2,
        "explanation": "ETF는 여러 종목을 묶어서 한 번에 투자할 수 있는 상품이에요. 한 종목만 사는 게 아니라 여러 종목에 나누어 투자할 수도 있다는 걸 알 수 있어요.",
    },
    {
        "stage_id": 4,
        "title": "코스피(KOSPI)",
        "tag": "코스피",
        "question": "코스피(KOSPI)에 대한 설명으로 가장 알맞은 것은?",
        "choices": ["벤처기업만 거래하는 시장", "국내 대표적인 유가증권시장", "해외 주식시장", "채권시장"],
        "answer": 2,
        "explanation": "코스피는 우리나라를 대표하는 유가증권시장으로, 많은 대기업들의 주식이 거래되는 곳이에요.",
    },
    {
        "stage_id": 5,
        "title": "상장(IPO)",
        "tag": "상장",
        "question": "기업이 처음으로 주식을 증권시장에 공개하여 거래를 시작하는 것을 무엇이라고 할까요?",
        "choices": ["상장(IPO)", "상장폐지", "감자", "액면분할"],
        "answer": 1,
        "explanation": "상장(IPO)은 기업이 처음으로 주식을 증권시장에 공개해서 누구나 거래할 수 있게 되는 것을 말해요.",
    },
    {
        "stage_id": 6,
        "title": "거래량",
        "tag": "거래량",
        "question": "하루 동안 거래된 주식의 총 수량을 무엇이라고 할까요?",
        "choices": ["거래량", "거래대금", "시가총액", "유동주식수"],
        "answer": 1,
        "explanation": "거래량은 하루 동안 사고 팔린 주식의 총 수량을 의미해요. 거래량이 많을수록 그 주식에 관심이 많다는 뜻이에요.",
    },
    {
        "stage_id": 7,
        "title": "시가총액",
        "tag": "시가총액",
        "question": "시가총액이란 무엇을 의미할까요?",
        "choices": ["회사의 전체 시장가치", "하루 동안 거래된 주식 수", "회사의 순이익", "회사가 가진 현금"],
        "answer": 1,
        "explanation": "시가총액은 주가에 발행 주식 수를 곱한 값으로, 회사 전체의 시장가치를 나타내요.",
    },
    {
        "stage_id": 8,
        "title": "분산투자",
        "tag": "분산투자",
        "question": "여러 종목에 나누어 투자하여 위험을 줄이는 투자 방법을 무엇이라고 할까요?",
        "choices": ["몰빵 투자", "분산투자", "단타", "공매도"],
        "answer": 2,
        "explanation": "분산투자는 여러 종목에 나누어 투자해서 한 종목이 떨어져도 손실 위험을 줄이는 투자 방법이에요.",
    },
    {
        "stage_id": 9,
        "title": "물타기",
        "tag": "물타기",
        "question": "주가가 하락했을 때 평균 매입 단가를 낮추기 위해 같은 종목을 추가 매수하는 것을 무엇이라고 할까요?",
        "choices": ["손절", "물타기", "분산투자", "공매도"],
        "answer": 2,
        "explanation": "물타기는 주가가 떨어졌을 때 같은 종목을 추가로 매수해서 평균 매입 단가를 낮추는 방법이에요.",
    },
    {
        "stage_id": 10,
        "title": "손절",
        "tag": "손절",
        "question": "손실이 더 커지는 것을 막기 위해 보유한 주식을 파는 것을 무엇이라고 할까요?",
        "choices": ["배당", "손절", "물타기", "시가총액"],
        "answer": 2,
        "explanation": "손절은 손실이 더 커지는 것을 막기 위해 손해를 감수하고 보유한 주식을 파는 것을 말해요.",
    },
    {
        "stage_id": 11,
        "title": "주가 상승 요인",
        "tag": "주가",
        "question": "다음 중 주가가 오를 가능성이 가장 높은 상황은 무엇일까요?",
        "choices": [
            "많은 사람들이 해당 주식을 사고 싶어 한다.",
            "회사 건물이 새로 지어진다.",
            "회사 직원 수가 줄어든다.",
            "은행 예금 금리가 오른다.",
        ],
        "answer": 1,
        "explanation": "주식을 사려는 사람이 많아질수록 수요가 늘어나 주가가 오를 가능성이 높아져요.",
    },
    {
        "stage_id": 12,
        "title": "기업 실적과 주가",
        "tag": "실적",
        "question": "어떤 기업이 좋은 실적을 발표했습니다. 가장 기대할 수 있는 변화는 무엇일까요?",
        "choices": [
            "주가가 오를 가능성이 있다.",
            "모든 투자자가 반드시 돈을 번다.",
            "회사가 바로 배당금을 지급한다.",
            "거래가 중단된다.",
        ],
        "answer": 1,
        "explanation": "좋은 실적은 회사의 가치를 높게 평가받게 해서 주가가 오를 가능성을 높여줘요. 다만 반드시 오른다고 보장하는 건 아니에요.",
    },
    {
        "stage_id": 13,
        "title": "올바른 투자 방법",
        "tag": "투자원칙",
        "question": "다음 중 가장 올바른 투자 방법은 무엇일까요?",
        "choices": [
            "한 종목에 모든 돈을 투자한다.",
            "소문만 듣고 바로 투자한다.",
            "여러 종목에 나누어 투자한다.",
            "빚을 내서 투자한다.",
        ],
        "answer": 3,
        "explanation": "여러 종목에 나누어 투자하면 한 종목의 손실이 전체에 미치는 영향을 줄일 수 있어 더 안전한 투자 방법이에요.",
    },
    {
        "stage_id": 14,
        "title": "투자 전 확인사항",
        "tag": "투자원칙",
        "question": "주식을 처음 시작하는 사람이 가장 먼저 해야 할 행동으로 알맞은 것은 무엇일까요?",
        "choices": [
            "친구 추천만 믿고 바로 투자한다.",
            "인터넷에서 가장 인기 있는 종목을 바로 산다.",
            "기업 정보를 확인하고 자신의 투자 목적에 맞게 신중하게 투자한다.",
            "한 종목에 모든 돈을 투자한다.",
        ],
        "answer": 3,
        "explanation": "투자를 시작하기 전에는 기업 정보를 확인하고 자신의 투자 목적에 맞게 신중히 결정하는 것이 중요해요.",
    },
]


def _difficulty_for_stage(stage_id: int) -> int:
    if stage_id <= 5:
        return 1
    if stage_id <= 10:
        return 2
    return 3


def seed_if_empty(db: Session) -> None:
    if db.query(Stage).first() is not None:
        return

    for item in STAGES:
        difficulty = _difficulty_for_stage(item["stage_id"])
        db.add(
            Stage(
                stage_id=item["stage_id"],
                title=item["title"],
                description=item["explanation"],
                difficulty=difficulty,
            )
        )
        db.add(
            Question(
                stage_id=item["stage_id"],
                question=item["question"],
                choice1=item["choices"][0],
                choice2=item["choices"][1],
                choice3=item["choices"][2],
                choice4=item["choices"][3],
                answer=item["answer"],
                explanation=item["explanation"],
                difficulty=difficulty,
                tag=item["tag"],
            )
        )

    db.commit()


def seed_default_user(db: Session) -> None:
    if db.query(User).filter(User.login_id == DEFAULT_USER_LOGIN_ID).first() is not None:
        return

    user = User(login_id=DEFAULT_USER_LOGIN_ID, password=hash_password(DEFAULT_USER_PASSWORD))
    db.add(user)
    db.commit()
