# restaurant-data-tool

서울특별시 금천구 일반음식점 데이터를 조회해서 PostgreSQL에 저장하는 도구입니다.

## 준비

1. Python 3.14 이상
2. PostgreSQL
3. 데이터 포털 서비스 키

## 설치

```bash
uv sync
```

## 환경 변수

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 설정하세요.

```env
DATA_GO_KR_SERVICE_KEY=your_service_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurant_data
DB_USER=postgres
DB_PASSWORD=postgres
```

## 실행

패키지 스크립트로 실행:

```bash
uv run restaurant-data-tool
```

직접 실행하려면:

```bash
uv run python -m restaurant_data_tool.main
```

## 동작

- `main.py`가 공공 API에서 식당 목록을 가져옵니다.
- 영업 상태가 `영업/정상`인 항목만 저장합니다.
- `management_no` 기준으로 중복은 upsert 처리합니다.
- DB 연결은 `database.py`의 `get_connection()`을 사용합니다.

## 파일 구조

```text
src/restaurant_data_tool/
  __init__.py
  database.py
  main.py
```
