# Database migrations

새 데이터베이스는 애플리케이션 시작 시 SQLAlchemy `create_all()`로 신규 테이블을 생성합니다.
기존 운영 데이터베이스에는 사용하는 DB에 맞는 SQL을 한 번 적용하세요.

## SQLite

```bash
cd backend
sqlite3 local.db < migrations/001_ai_recommendation_sqlite.sql
sqlite3 local.db < migrations/002_result_integrity_sqlite.sql
sqlite3 local.db < migrations/003_recommendation_statistics_sqlite.sql
```

## MySQL

```bash
cd backend
mysql -u USER -p DB_NAME < migrations/001_ai_recommendation_mysql.sql
mysql -u USER -p DB_NAME < migrations/002_result_integrity_mysql.sql
mysql -u USER -p DB_NAME < migrations/003_recommendation_statistics_mysql.sql
```

마이그레이션은 기존 `wrong_answer`, `result`, `history`를 삭제하지 않습니다.
`002`부터 새 결과와 문제별 답안을 연결하고, 연결되지 않은 기존 `result`도 추천
통계에 합산해 배포 전 학습 기록을 보존합니다.
