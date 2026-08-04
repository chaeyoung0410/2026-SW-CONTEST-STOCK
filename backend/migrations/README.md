# Database migrations

새 데이터베이스는 애플리케이션 시작 시 SQLAlchemy `create_all()`로 신규 테이블을 생성합니다.
기존 운영 데이터베이스에는 사용하는 DB에 맞는 SQL을 한 번 적용하세요.

## SQLite

```bash
cd backend
sqlite3 local.db < migrations/001_ai_recommendation_sqlite.sql
```

## MySQL

```bash
cd backend
mysql -u USER -p DB_NAME < migrations/001_ai_recommendation_mysql.sql
```

두 마이그레이션은 기존 `wrong_answer`를 삭제하지 않습니다. 추천 집계는 새
`answer_attempt`가 있는 stage에서는 이를 우선 사용하고, 없는 stage에 한해 기존
`result`, `wrong_answer` 순서로 읽어 중복 합산을 방지합니다.
