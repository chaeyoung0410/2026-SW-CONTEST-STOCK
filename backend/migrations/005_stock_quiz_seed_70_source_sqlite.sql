-- stock_quiz_seed.sql
-- 14 stages x 5 quizzes = 70 quizzes

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS quizzes;

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage INTEGER NOT NULL CHECK(stage BETWEEN 1 AND 14),
    topic TEXT NOT NULL,
    concept TEXT NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
    explanation TEXT NOT NULL,
    difficulty INTEGER NOT NULL DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 3)
);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(1, '주식의 기초', '주식의 의미', '주식을 보유한다는 의미로 가장 알맞은 것은?', '기업에 돈을 빌려준다는 뜻', '기업의 일부를 소유한다는 뜻', '정부에 세금을 낸다는 뜻', '은행 예금에 가입한다는 뜻', 'B', '주식은 기업의 소유권을 일정 부분 나타내는 증권입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(1, '주식의 기초', '주주', '주식을 보유한 사람을 무엇이라고 하나요?', '채권자', '예금자', '주주', '감사인', 'C', '기업의 주식을 보유한 사람을 주주라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(1, '주식의 기초', '증권회사', '개인이 주식을 사고팔기 위해 일반적으로 이용하는 곳은?', '증권회사', '우체국', '세무서', '보험회사', 'A', '주식 거래는 보통 증권회사의 계좌와 거래 시스템을 통해 이루어집니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(1, '주식의 기초', '주식시장', '주식시장의 주요 기능으로 가장 적절한 것은?', '기업과 투자자가 주식을 거래할 수 있게 한다', '모든 주식의 가격을 동일하게 정한다', '기업의 세금을 대신 납부한다', '예금 금리를 결정한다', 'A', '주식시장은 기업의 자금 조달과 투자자의 주식 거래를 가능하게 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(1, '주식의 기초', '투자수익', '주식 투자에서 수익을 얻는 대표적인 방법은?', '주가 상승에 따른 차익과 배당', '은행 이자만 받기', '세금 환급만 받기', '보험금을 받기', 'A', '주식 투자 수익은 대표적으로 매매차익과 배당에서 발생할 수 있습니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(2, '주식 거래 기본', '매수', '주식 거래에서 ''매수''의 의미는?', '주식을 사는 것', '주식을 파는 것', '주식을 빌리는 것', '주식을 소각하는 것', 'A', '매수는 주식을 사는 거래입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(2, '주식 거래 기본', '매도', '주식 거래에서 ''매도''의 의미는?', '주식을 사는 것', '주식을 파는 것', '주식을 증여하는 것', '배당을 받는 것', 'B', '매도는 보유한 주식을 파는 거래입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(2, '주식 거래 기본', '지정가 주문', '원하는 가격을 직접 정해 주문하는 방식은?', '시장가 주문', '지정가 주문', '예약이체', '자동이체', 'B', '지정가 주문은 투자자가 원하는 매수 또는 매도 가격을 정해서 내는 주문입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(2, '주식 거래 기본', '시장가 주문', '가격을 지정하지 않고 현재 시장에서 가능한 가격으로 빠르게 거래하는 주문은?', '시장가 주문', '지정가 주문', '정기예금', '공매도', 'A', '시장가 주문은 가격을 지정하지 않고 시장에서 가능한 가격으로 체결을 우선합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(2, '주식 거래 기본', '체결', '주문한 주식 거래가 실제로 성사되는 것을 무엇이라고 하나요?', '상장', '체결', '배당', '분할', 'B', '매수 주문과 매도 주문의 조건이 맞아 실제 거래가 성사되는 것을 체결이라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(3, '주가와 수익률', '수익률 계산', '10,000원에 산 주식을 12,000원에 팔았다면 수수료와 세금을 제외한 수익률은?', '10%', '20%', '25%', '30%', 'B', '수익률은 (12,000-10,000)/10,000 × 100 = 20%입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(3, '주가와 수익률', '손실률 계산', '20,000원에 산 주식의 가격이 18,000원이 되었다면 수익률은?', '-5%', '-10%', '10%', '20%', 'B', '(18,000-20,000)/20,000 × 100 = -10%입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(3, '주가와 수익률', '평가손익', '주식을 아직 팔지 않았지만 현재 가격 기준으로 발생한 이익이나 손실을 무엇이라고 하나요?', '배당금', '평가손익', '예수금', '이자소득', 'B', '보유 중인 자산을 현재 가격으로 평가한 이익과 손실을 평가손익이라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(3, '주가와 수익률', '실현손익', '주식을 실제로 매도하여 확정된 이익이나 손실은?', '실현손익', '평가손익', '시가총액', '배당성향', 'A', '매도 등으로 거래가 종료되어 실제로 확정된 손익을 실현손익이라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(3, '주가와 수익률', '복리', '투자 수익이 다시 원금에 더해져 이후 수익에도 영향을 주는 효과는?', '분산효과', '복리효과', '환율효과', '레버리지효과', 'B', '수익을 재투자하여 원금이 커지고 그 위에 다시 수익이 발생하는 것을 복리효과라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(4, '증권시장과 지수', '코스피', '대한민국의 대표적인 유가증권시장 지수는?', 'NASDAQ', 'KOSPI', 'Nikkei 225', 'DAX', 'B', 'KOSPI는 한국 유가증권시장을 대표하는 지수입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(4, '증권시장과 지수', '코스닥', '코스닥 시장의 특징으로 가장 적절한 것은?', '성장형·중소기업이 많이 상장되어 있다', '미국 기업만 거래된다', '채권만 거래된다', '정부기관만 참여한다', 'A', '코스닥은 상대적으로 성장성이 높은 중소·벤처기업 비중이 큰 시장입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(4, '증권시장과 지수', 'S&P500', 'S&P 500 지수는 주로 어느 나라 기업을 대상으로 하나요?', '대한민국', '일본', '미국', '독일', 'C', 'S&P 500은 미국의 대표적인 대형 상장기업 500개를 중심으로 구성된 지수입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(4, '증권시장과 지수', '주가지수', '주가지수가 상승했다는 말의 의미로 가장 적절한 것은?', '시장 내 대표 종목들의 전반적인 가격 수준이 상승했다', '모든 종목이 반드시 상승했다', '모든 기업의 이익이 증가했다', '환율이 반드시 하락했다', 'A', '지수 상승은 구성 종목의 전체적인 가격 수준이 오른 것을 의미하지만 모든 종목 상승을 뜻하지는 않습니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(4, '증권시장과 지수', '시장대표성', '주가지수를 활용하는 이유로 가장 적절한 것은?', '시장 전체 흐름을 파악하기 위해', '개별 기업의 정확한 미래 주가를 알기 위해', '세금을 없애기 위해', '주식 거래를 중단하기 위해', 'A', '주가지수는 개별 종목이 아니라 시장이나 특정 집단의 전반적인 움직임을 파악하는 데 사용됩니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(5, '기업과 주식', '상장', '기업이 발행한 주식이 거래소에서 공개적으로 거래될 수 있도록 하는 것을 무엇이라고 하나요?', '상장', '배당', '감자', '예금', 'A', '상장은 기업의 주식이 거래소에서 거래될 수 있도록 등록되는 것을 의미합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(5, '기업과 주식', 'IPO', '기업이 처음으로 일반 투자자에게 주식을 공개하여 자금을 조달하는 것을 무엇이라고 하나요?', 'ETF', 'IPO', 'PER', 'ROE', 'B', 'IPO는 Initial Public Offering의 약자로 기업공개를 뜻합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(5, '기업과 주식', '시가총액', '주가가 50,000원이고 발행주식 수가 1,000만 주라면 시가총액은?', '500억원', '5,000억원', '5조원', '50조원', 'B', '50,000원 × 10,000,000주 = 500,000,000,000원으로 5,000억원입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(5, '기업과 주식', '액면분할', '1주를 여러 주로 나누어 주식 수를 늘리고 1주당 가격을 낮추는 것은?', '액면분할', '상장폐지', '배당락', '유상증자', 'A', '액면분할은 기업가치 자체를 바꾸지 않으면서 주식 수를 늘리고 1주당 가격을 낮추는 방식입니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(5, '기업과 주식', '증자', '기업이 새로운 주식을 발행하여 자본금을 늘리는 행위를 무엇이라고 하나요?', '감자', '증자', '배당', '상환', 'B', '새로운 주식을 발행해 자본금을 늘리는 것을 증자라고 합니다.', 1);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(6, '배당과 주주 권리', '배당', '기업이 이익의 일부를 주주에게 나누어 주는 것을 무엇이라고 하나요?', '배당', '상장', '매수', '분할', 'A', '기업은 이익의 일부를 현금이나 주식 등의 형태로 주주에게 배당할 수 있습니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(6, '배당과 주주 권리', '배당수익률', '주가가 40,000원이고 1주당 연간 배당금이 2,000원이라면 배당수익률은?', '2%', '5%', '10%', '20%', 'B', '배당수익률은 2,000/40,000 × 100 = 5%입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(6, '배당과 주주 권리', '의결권', '주주가 기업의 주요 의사결정에 참여할 수 있는 대표적인 권리는?', '의결권', '예금보호권', '환불권', '보험청구권', 'A', '보통주 주주는 주주총회 등을 통해 의결권을 행사할 수 있습니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(6, '배당과 주주 권리', '배당락', '배당을 받을 권리가 사라진 이후 주가가 배당금 등을 반영해 조정되는 현상을 무엇이라고 하나요?', '배당락', '상장폐지', '액면분할', '관리종목', 'A', '배당락은 배당받을 권리가 없어진 이후 주가가 배당가치를 반영하여 조정되는 현상입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(6, '배당과 주주 권리', '배당정책', '배당을 많이 지급하는 기업에 대한 설명으로 반드시 옳은 것은?', '항상 주가가 상승한다', '항상 성장성이 높다', '주주에게 현금을 많이 환원하는 편일 수 있다', '절대로 손실이 나지 않는다', 'C', '높은 배당은 주주환원이 적극적일 수 있음을 의미하지만 주가 상승이나 성장성을 보장하지는 않습니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(7, '재무제표 기초', '매출액', '기업이 상품이나 서비스를 판매하여 얻은 총 수입을 나타내는 대표적인 항목은?', '매출액', '부채', '자본금', '배당금', 'A', '매출액은 기업의 영업활동을 통해 발생한 판매 수익의 총액을 나타냅니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(7, '재무제표 기초', '영업이익', '기업의 본업에서 벌어들인 이익을 가장 직접적으로 나타내는 항목은?', '영업이익', '자본금', '배당금', '시가총액', 'A', '영업이익은 매출에서 본업과 관련된 비용을 차감한 이익입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(7, '재무제표 기초', '순이익', '기업의 여러 비용과 세금 등을 반영한 뒤 최종적으로 남는 이익은?', '매출총이익', '영업이익', '당기순이익', '자본금', 'C', '당기순이익은 일정 기간 동안 비용과 세금 등을 모두 반영한 최종 이익입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(7, '재무제표 기초', '자산과 부채', '회계에서 ''자산 = 부채 + ( )''의 빈칸에 들어갈 것은?', '매출', '자본', '배당', '비용', 'B', '기본 회계등식은 자산 = 부채 + 자본입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(7, '재무제표 기초', '현금흐름', '기업의 실제 현금 유입과 유출을 확인하는 재무제표는?', '손익계산서', '재무상태표', '현금흐름표', '주주명부', 'C', '현금흐름표는 영업·투자·재무활동에서 실제 현금이 어떻게 들어오고 나갔는지 보여줍니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(8, '기업가치 지표', 'PER', '주가가 30,000원이고 EPS가 3,000원이라면 PER은?', '5배', '10배', '15배', '30배', 'B', 'PER = 주가 / EPS이므로 30,000 / 3,000 = 10배입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(8, '기업가치 지표', 'EPS', 'EPS의 의미로 옳은 것은?', '주당순이익', '주당매출액', '주당배당률', '주가변동률', 'A', 'EPS는 Earnings Per Share로 주당순이익을 뜻합니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(8, '기업가치 지표', 'PBR', 'PBR은 일반적으로 주가를 무엇과 비교하는 지표인가요?', '주당순자산', '주당매출', '배당금', '영업이익률', 'A', 'PBR은 주가를 주당순자산(BPS)과 비교한 지표입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(8, '기업가치 지표', 'ROE', 'ROE가 의미하는 것은?', '자기자본이익률', '배당수익률', '매출증가율', '부채비율', 'A', 'ROE는 기업이 자기자본을 활용해 얼마나 효율적으로 이익을 냈는지를 보여주는 지표입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(8, '기업가치 지표', '지표해석', 'PER이 낮은 기업은 무조건 저평가된 좋은 주식이라고 할 수 있을까요?', '그렇다', '아니다', '배당을 할 때만 그렇다', '코스피 기업만 그렇다', 'B', 'PER이 낮아도 성장성, 산업 전망, 일시적 이익 증가 등 다양한 요인을 함께 살펴야 합니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(9, '차트의 기초', '캔들차트', '양봉과 음봉을 통해 주가 움직임을 표현하는 대표적인 차트는?', '원형차트', '캔들차트', '막대그래프', '산점도', 'B', '캔들차트는 시가·고가·저가·종가를 이용해 일정 기간의 주가 움직임을 보여줍니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(9, '차트의 기초', '시가', '하루 거래가 시작될 때 최초로 형성된 가격은?', '시가', '종가', '고가', '저가', 'A', '시가는 해당 거래일에 처음 체결된 가격입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(9, '차트의 기초', '종가', '하루 거래가 끝날 때 마지막으로 형성된 가격은?', '시가', '종가', '고가', '평균가', 'B', '종가는 해당 거래일의 마지막 체결 가격입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(9, '차트의 기초', '고가와 저가', '하루 중 가장 높은 거래 가격과 가장 낮은 거래 가격을 각각 무엇이라 하나요?', '시가와 종가', '고가와 저가', '매수와 매도', '상한가와 하한가', 'B', '해당 기간 중 가장 높은 가격을 고가, 가장 낮은 가격을 저가라고 합니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(9, '차트의 기초', '양봉', '일반적인 캔들차트에서 종가가 시가보다 높은 경우를 무엇이라고 하나요?', '양봉', '음봉', '배당락', '갭하락', 'A', '종가가 시가보다 높은 상승형 캔들을 일반적으로 양봉이라고 합니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(10, '기술적 분석', '이동평균선', '최근 일정 기간의 주가 평균을 선으로 연결한 것은?', '이동평균선', '배당수익률', 'PER', '시가총액', 'A', '이동평균선은 일정 기간의 주가 평균값을 연결한 선으로 추세 확인에 활용됩니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(10, '기술적 분석', '거래량', '특정 기간 동안 실제로 거래된 주식의 수를 의미하는 것은?', '거래량', '시가총액', '자본금', 'EPS', 'A', '거래량은 일정 기간 동안 사고팔린 주식 수를 나타냅니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(10, '기술적 분석', '지지선', '주가가 하락할 때 매수세가 유입되어 하락이 멈추거나 반등할 가능성이 있다고 보는 가격대는?', '저항선', '지지선', '배당선', '평균선', 'B', '지지선은 주가 하락 시 매수세가 강해질 수 있다고 보는 가격 영역입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(10, '기술적 분석', '저항선', '주가가 상승할 때 매도세가 강해져 추가 상승이 제한될 수 있다고 보는 가격대는?', '지지선', '저항선', '손절선', '액면가', 'B', '저항선은 주가 상승 과정에서 매도 압력이 커질 수 있다고 보는 가격 영역입니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(10, '기술적 분석', '기술적분석 한계', '차트 분석만으로 미래 주가를 항상 정확히 예측할 수 있을까요?', '그렇다', '아니다', '대형주만 가능하다', '거래량이 많으면 항상 가능하다', 'B', '기술적 분석은 참고 도구이며 미래 주가를 확실하게 보장하지 않습니다.', 2);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(11, '경제와 주식시장', '금리', '일반적으로 금리가 크게 오르면 기업에 나타날 수 있는 영향은?', '이자 부담이 늘 수 있다', '대출 비용이 항상 줄어든다', '매출이 반드시 두 배가 된다', '세금이 사라진다', 'A', '금리 상승은 기업의 차입 비용과 이자 부담을 높일 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(11, '경제와 주식시장', '물가', '물가가 지속적으로 전반적으로 상승하는 현상은?', '디플레이션', '인플레이션', '스태그플레이션', '리밸런싱', 'B', '전반적인 물가 수준이 지속적으로 상승하는 현상을 인플레이션이라고 합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(11, '경제와 주식시장', '환율', '원/달러 환율이 상승했다는 의미로 가장 적절한 것은?', '일반적으로 원화 가치가 달러 대비 하락했다', '원화 가치가 반드시 상승했다', '미국 금리가 반드시 하락했다', '모든 수출기업 주가가 하락했다', 'A', '원/달러 환율 상승은 같은 1달러를 사는 데 더 많은 원화가 필요하다는 뜻으로 원화 가치 하락을 의미합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(11, '경제와 주식시장', '경기', '경기 침체기에 일반적으로 나타날 가능성이 있는 현상은?', '기업 매출과 이익이 압박받을 수 있다', '모든 주식이 반드시 상승한다', '실업률이 항상 0%가 된다', '물가가 반드시 2배가 된다', 'A', '경기 침체는 소비와 투자를 둔화시켜 기업 실적에 부담이 될 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(11, '경제와 주식시장', '거시경제', '주식 투자 시 금리·환율·물가 같은 경제지표를 살펴보는 이유는?', '기업 실적과 투자심리에 영향을 줄 수 있기 때문', '주식 거래 수수료를 없애기 위해', '기업명을 바꾸기 위해', '주식 수를 자동으로 늘리기 위해', 'A', '거시경제 변수는 자금조달 비용, 수요, 환산 실적, 투자심리 등에 영향을 줄 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(12, '투자 위험 관리', '분산투자', '투자 위험을 줄이기 위한 대표적인 방법은?', '한 종목에 전액 투자', '분산투자', '대출을 최대한 활용', '소문만 보고 투자', 'B', '여러 자산이나 종목에 나누어 투자하면 특정 자산의 부진이 전체에 미치는 영향을 줄일 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(12, '투자 위험 관리', '변동성', '주가가 짧은 기간에 크게 오르내리는 정도를 나타내는 개념은?', '변동성', '배당률', '액면가', '시가총액', 'A', '변동성은 자산 가격이 얼마나 크게 흔들리는지를 나타내는 위험 관련 지표입니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(12, '투자 위험 관리', '손절', '예상과 달리 손실이 커질 때 추가 손실을 제한하기 위해 매도하는 전략은?', '손절', '물타기', '배당', '분할', 'A', '손절은 미리 정한 기준 등에 따라 손실을 감수하고 매도해 위험을 제한하는 방식입니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(12, '투자 위험 관리', '레버리지', '대출이나 파생상품 등을 활용해 자기자본보다 큰 규모로 투자하는 것은?', '분산투자', '레버리지 투자', '적립식 투자', '배당투자', 'B', '레버리지는 수익을 확대할 수 있지만 손실도 크게 확대할 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(12, '투자 위험 관리', '위험과 수익', '투자에서 일반적으로 기대수익률이 높을수록 함께 고려해야 하는 것은?', '위험이 커질 가능성', '세금이 반드시 없어짐', '원금이 반드시 보장됨', '손실 가능성이 0이 됨', 'A', '높은 기대수익은 일반적으로 더 높은 위험을 동반할 수 있으므로 함께 평가해야 합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(13, '투자 전략', '가치투자', '기업의 본질적 가치보다 시장가격이 낮다고 판단되는 주식을 찾는 전략은?', '가치투자', '초단타매매', '레버리지 투자', '공매도', 'A', '가치투자는 기업의 내재가치와 시장가격을 비교해 저평가되었다고 판단되는 종목을 찾는 방식입니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(13, '투자 전략', '성장주', '현재보다 미래의 매출과 이익 성장 가능성이 크게 기대되는 기업의 주식을 무엇이라고 하나요?', '성장주', '우선주', '관리종목', '채권', 'A', '성장주는 미래의 높은 성장 가능성이 기대되는 기업의 주식을 말합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(13, '투자 전략', '장기투자', '장기투자의 장점으로 가장 적절한 것은?', '단기 가격 변동의 영향을 상대적으로 줄이고 기업 성장에 참여할 수 있다', '항상 손실이 발생하지 않는다', '매일 매매해야 한다', '모든 종목에서 배당을 받을 수 있다', 'A', '장기투자는 기업의 장기 성장에 참여하면서 단기 변동의 영향을 상대적으로 줄일 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(13, '투자 전략', 'ETF', '여러 종목이나 자산을 하나의 상품처럼 묶어 거래소에서 사고팔 수 있는 상품은?', 'ETF', '정기예금', '보험', '회사채만', 'A', 'ETF는 특정 지수나 자산군 등을 추종하도록 설계된 상장지수펀드입니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(13, '투자 전략', '리밸런싱', '투자 후 변한 자산 비중을 목표 비중에 맞게 다시 조정하는 것을 무엇이라고 하나요?', '리밸런싱', '배당락', '상장폐지', '액면분할', 'A', '리밸런싱은 시장 변동으로 달라진 포트폴리오 비중을 원래 목표에 맞게 조정하는 과정입니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(14, '종합 투자 판단', '기업분석', '매출과 영업이익은 증가하지만 부채가 빠르게 늘고 있다면 가장 적절한 판단은?', '성장성과 재무위험을 함께 살펴봐야 한다', '무조건 매수해야 한다', '무조건 상장폐지된다', '부채는 투자와 관계없다', 'A', '성장 지표가 좋아도 부채 증가에 따른 이자 부담과 재무안정성을 함께 확인해야 합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(14, '종합 투자 판단', '금리와 성장주', '금리가 빠르게 상승하는 환경에서 성장주가 압박받을 수 있는 이유로 적절한 것은?', '미래 이익의 현재가치가 낮아지고 자금조달 비용이 커질 수 있어서', '기업의 주식 수가 자동으로 사라져서', '배당이 법적으로 금지되어서', '주식 거래가 중단되어서', 'A', '금리 상승은 할인율과 자금조달 비용을 높여 미래 성장 기대가 큰 기업의 가치평가에 부담이 될 수 있습니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(14, '종합 투자 판단', '분산과 위험', '한 기업의 전망이 매우 좋아 보여도 전 재산을 한 종목에 투자하지 않는 것이 좋은 이유는?', '예상하지 못한 기업 고유 위험을 줄이기 위해', '수익을 무조건 낮추기 위해', '주가가 항상 오르기 때문에', '세금을 더 내기 위해', 'A', '기업별 예상치 못한 악재가 발생할 수 있어 분산을 통해 특정 종목 위험을 줄이는 것이 중요합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(14, '종합 투자 판단', '재무와 밸류에이션', '기업의 이익은 감소하고 있는데 PER도 낮아졌다면 가장 먼저 확인할 점은?', 'PER 하락이 주가 하락 때문인지 이익 구조 변화 때문인지', '배당일만 확인한다', '기업 이름이 바뀌었는지', '주식 액면가만 확인한다', 'A', '낮은 PER이 저평가를 의미하는지 판단하려면 주가와 이익 변화의 원인을 함께 분석해야 합니다.', 3);

INSERT INTO quizzes (stage, topic, concept, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty) VALUES
(14, '종합 투자 판단', '종합판단', '투자 결정을 내릴 때 가장 바람직한 방법은?', '기업 실적, 가치평가, 시장환경, 위험을 종합적으로 본다', '인터넷 소문 하나만 믿는다', '최근 주가 상승 여부만 본다', '친구의 추천만 따른다', 'A', '투자 판단은 한 가지 정보가 아니라 기업의 펀더멘털, 밸류에이션, 시장환경, 위험 등을 종합적으로 고려해야 합니다.', 3);

-- 확인용
SELECT stage, COUNT(*) AS quiz_count
FROM quizzes
GROUP BY stage
ORDER BY stage;
