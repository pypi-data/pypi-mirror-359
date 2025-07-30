# AI Agent Manager

AI 에이전트를 관리하는 웹 서비스입니다.

## 🚀 시작하기

### 1. 의존성 설치
```bash
poetry install
```

### 2. 가상환경 활성화
```bash
poetry shell
```

### 3. 서비스 실행
```bash
# 방법 1: 자동으로 Poetry 가상환경 사용 (추천)
python run.py

# 방법 2: Poetry 명령어로 직접 실행
poetry run uvicorn ai_agent_manager.main:app --reload --host 0.0.0.0 --port 8000

# 방법 3: Poetry shell 진입 후 실행
poetry shell
uvicorn ai_agent_manager.main:app --reload
```

### 4. API 문서 확인
서비스 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📦 라이브러리 추가

```bash
# 일반 의존성 추가
poetry add 라이브러리명

# 개발용 의존성 추가
poetry add --group dev 라이브러리명

# 예시
poetry add requests pydantic
poetry add --group dev pytest black flake8
```

## 🛠️ 개발

### 프로젝트 구조
```
ai-agent-manager/
├── src/
│   └── ai_agent_manager/
│       ├── __init__.py
│       └── main.py
├── tests/
├── pyproject.toml
└── README.md
```

### 개발 모드 실행
```bash
uvicorn ai_agent_manager.main:app --reload
```

## 📝 API 엔드포인트

- `GET /` - 기본 환영 메시지
- `GET /health` - 서비스 상태 확인
- `GET /agents` - 에이전트 목록 조회

## cursor에서 venv 선택하기
 - cmd + shift + p
 - Python: select interpreter 선택
 - Python 3.12.10('.venv': Poetry) 선택
 - cmd + , (setting) -> venv 검색 -> path에 ./venv 등록???

