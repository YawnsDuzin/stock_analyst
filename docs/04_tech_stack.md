# 04. 기술 스택 및 아키텍처

> **이 문서의 목적**: 시스템의 전체 아키텍처 구성, 각 레이어별 기술 스택, 데이터 흐름을 상세히 설명합니다.

---

## 목차

- [4.1 전체 시스템 아키텍처](#41-전체-시스템-아키텍처)
- [4.2 데이터 수집 레이어](#42-데이터-수집-레이어)
- [4.3 데이터 저장 레이어](#43-데이터-저장-레이어)
- [4.4 AI 분석 레이어](#44-ai-분석-레이어)
- [4.5 출력 레이어](#45-출력-레이어)
- [4.6 백엔드 기술 스택 상세](#46-백엔드-기술-스택-상세)
- [4.7 AI/분석 기술 스택](#47-ai분석-기술-스택)
- [4.8 프론트엔드 기술 스택](#48-프론트엔드-기술-스택)
- [4.9 인프라 및 배포](#49-인프라-및-배포)
- [4.10 데이터 흐름 다이어그램](#410-데이터-흐름-다이어그램)

---

## 4.1 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                   데이터 수집 레이어                    │
│  나라장터  DART  HIRA  KIPRIS  크롤러  AIS  위성     │
└──────────────────────┬──────────────────────────────┘
                       │ (Raw Data)
                       ▼
┌─────────────────────────────────────────────────────┐
│                   데이터 저장 레이어                    │
│    PostgreSQL (정형)  +  ChromaDB (비정형/벡터)      │
│              Redis (시세 캐싱)                        │
└──────────────────────┬──────────────────────────────┘
                       │ (Structured / Vectorized)
                       ▼
┌─────────────────────────────────────────────────────┐
│                   AI 분석 레이어                        │
│              Claude API (Tool Use + RAG)              │
│  ┌──────────┬──────────┬──────────┬──────────────┐  │
│  │ 데이터   │ 감성     │ 신호     │ 리포트       │  │
│  │ 조회     │ 분석     │ 스코어링 │ 생성         │  │
│  └──────────┴──────────┴──────────┴──────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ (Analysis Results)
                       ▼
┌─────────────────────────────────────────────────────┐
│                   출력 레이어                           │
│     Next.js 대시보드  +  텔레그램 봇  +  이메일      │
└─────────────────────────────────────────────────────┘
```

---

## 4.2 데이터 수집 레이어

### 수집기(Collector) 설계 원칙

1. **모듈화**: 각 데이터 소스별 독립적인 수집기 클래스
2. **재시도**: 네트워크 오류 시 지수 백오프(exponential backoff)
3. **속도 제한**: API rate limit 준수를 위한 throttling
4. **로깅**: 모든 수집 이벤트를 기록하여 디버깅 용이

### 수집기 기본 인터페이스

```python
from abc import ABC, abstractmethod
from datetime import datetime

class BaseCollector(ABC):
    """모든 데이터 수집기의 기본 클래스"""

    def __init__(self, name: str, api_key: str | None = None):
        self.name = name
        self.api_key = api_key
        self.last_collected_at: datetime | None = None

    @abstractmethod
    async def collect(self, **kwargs) -> list[dict]:
        """데이터를 수집합니다."""
        pass

    @abstractmethod
    def validate(self, data: dict) -> bool:
        """수집된 데이터의 유효성을 검증합니다."""
        pass

    async def collect_with_retry(self, max_retries: int = 3, **kwargs) -> list[dict]:
        """재시도 로직이 포함된 수집"""
        for attempt in range(max_retries):
            try:
                data = await self.collect(**kwargs)
                self.last_collected_at = datetime.now()
                return data
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # 지수 백오프
                await asyncio.sleep(wait_time)
```

### 수집기 목록

| 수집기 | 소스 | 주기 | 우선순위 |
|--------|------|------|---------|
| `DartCollector` | DART 전자공시 | 실시간 | ⭐⭐⭐ |
| `ProcurementCollector` | 나라장터 | 일간 | ⭐⭐⭐ |
| `HiringCollector` | 채용사이트 | 주간 | ⭐⭐⭐ |
| `NewsCollector` | 뉴스 사이트 | 실시간 | ⭐⭐ |
| `HIRACollector` | 건강보험심사평가원 | 분기 | ⭐⭐⭐ |
| `PatentCollector` | KIPRIS | 월간 | ⭐⭐ |
| `SECCollector` | SEC EDGAR | 일간 | ⭐⭐ |
| `SentimentCollector` | 커뮤니티/SNS | 일간 | ⭐⭐ |

---

## 4.3 데이터 저장 레이어

### PostgreSQL (정형 데이터)

주요 테이블 설계:

```sql
-- 기업 기본 정보
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 신호 이벤트
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    signal_type VARCHAR(50) NOT NULL,       -- procurement, hiring, sentiment 등
    signal_source VARCHAR(100) NOT NULL,    -- 데이터 소스
    score FLOAT NOT NULL,                   -- 0~100 점수
    raw_data JSONB,                         -- 원본 데이터
    description TEXT,                       -- 신호 설명
    detected_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP                    -- 신호 유효 기간
);

-- 분석 리포트
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    report_type VARCHAR(20) NOT NULL,       -- daily, weekly, alert
    content TEXT NOT NULL,
    total_score FLOAT,
    recommendation VARCHAR(20),             -- STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    created_at TIMESTAMP DEFAULT NOW()
);

-- 나라장터 낙찰 데이터
CREATE TABLE procurement_contracts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    contract_name TEXT NOT NULL,
    contract_amount BIGINT,
    awarding_agency VARCHAR(200),
    contract_date DATE,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 채용공고 스냅샷
CREATE TABLE hiring_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    snapshot_date DATE NOT NULL,
    total_openings INTEGER,
    categories JSONB,                       -- {"AI": 5, "영업": 3, ...}
    new_categories TEXT[],                  -- 새로 등장한 카테고리
    created_at TIMESTAMP DEFAULT NOW()
);
```

### ChromaDB (벡터 데이터)

비정형 텍스트 데이터를 벡터로 변환하여 저장합니다. RAG(Retrieval Augmented Generation)에 활용됩니다.

```python
import chromadb
from chromadb.config import Settings

# ChromaDB 초기화
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"
))

# 컬렉션 생성
collections = {
    "dart_reports": chroma_client.create_collection("dart_reports"),
    "news_articles": chroma_client.create_collection("news_articles"),
    "conference_calls": chroma_client.create_collection("conference_calls"),
    "analyst_reports": chroma_client.create_collection("analyst_reports"),
}
```

### Redis (캐싱)

실시간 시세, API 응답 캐싱, 세션 관리에 사용합니다.

```python
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

# 시세 캐싱 (TTL 5분)
redis_client.setex(f"price:{ticker}", 300, current_price)

# API 응답 캐싱 (TTL 1시간)
redis_client.setex(f"api:dart:{corp_code}", 3600, json.dumps(response))
```

---

## 4.4 AI 분석 레이어

Claude API를 중심으로 4가지 분석 기능을 제공합니다.

| 기능 | 설명 | Claude 활용 |
|------|------|-----------|
| **데이터 조회** | Tool Use로 실시간 데이터 접근 | Tool Use |
| **감성 분석** | 텍스트 톤/감성 변화 감지 | 프롬프트 + NLP |
| **신호 스코어링** | 복합 신호 통합 점수화 | Tool Use + 추론 |
| **리포트 생성** | 구조화된 분석 리포트 작성 | 프롬프트 |

상세 설계는 [05. Claude 연동 설계](./05_claude_integration.md)에서 다룹니다.

---

## 4.5 출력 레이어

### 텔레그램 봇

즉시 알림이 필요한 신호를 텔레그램으로 전송합니다.

```python
from telegram import Bot

async def send_alert(ticker: str, signal: dict):
    """중요 신호 발견 시 텔레그램 알림을 전송합니다."""
    bot = Bot(token="YOUR_BOT_TOKEN")
    message = f"""
🔔 신호 감지: {ticker}
📊 신호 유형: {signal['type']}
💯 점수: {signal['score']}/100
📝 요약: {signal['summary']}
⏰ 감지 시각: {signal['detected_at']}
    """
    await bot.send_message(chat_id="YOUR_CHAT_ID", text=message)
```

### Next.js 대시보드

실시간 모니터링 대시보드의 주요 화면:

1. **메인 대시보드**: 전체 종목 신호 요약
2. **종목 상세**: 개별 종목의 신호 분해
3. **신호 타임라인**: 시간순 신호 이력
4. **백테스팅 결과**: 과거 신호 성과

---

## 4.6 백엔드 기술 스택 상세

### 핵심 라이브러리

```python
# requirements.txt 주요 항목

# 웹 프레임워크
fastapi>=0.104.0
uvicorn>=0.24.0

# 비동기 작업
celery>=5.3.0
redis>=5.0.0

# 데이터베이스
sqlalchemy>=2.0.0
alembic>=1.12.0           # DB 마이그레이션
asyncpg>=0.29.0           # PostgreSQL 비동기 드라이버

# 데이터 검증
pydantic>=2.5.0
pydantic-settings>=2.1.0  # 설정 관리

# HTTP 클라이언트
httpx>=0.25.0             # 비동기 HTTP

# 크롤링
playwright>=1.40.0        # 동적 웹 크롤링
beautifulsoup4>=4.12.0    # HTML 파싱

# 벡터 DB
chromadb>=0.4.0
```

### FastAPI 프로젝트 구조

```
src/stock_analyst/
├── __init__.py
├── main.py                    # FastAPI 앱 엔트리포인트
├── config.py                  # 환경 설정
├── models/                    # SQLAlchemy 모델
│   ├── __init__.py
│   ├── company.py
│   ├── signal.py
│   └── report.py
├── schemas/                   # Pydantic 스키마
│   ├── __init__.py
│   ├── company.py
│   ├── signal.py
│   └── report.py
├── data_sources/              # 데이터 수집기
│   ├── __init__.py
│   ├── base.py               # BaseCollector
│   ├── dart_collector.py
│   ├── procurement_collector.py
│   ├── hiring_collector.py
│   └── news_collector.py
├── analysis/                  # 분석 엔진
│   ├── __init__.py
│   ├── nlp_analyzer.py
│   ├── sentiment_analyzer.py
│   └── cross_validator.py
├── scoring/                   # 스코어링
│   ├── __init__.py
│   └── alpha_scorer.py
├── agents/                    # Claude 에이전트
│   ├── __init__.py
│   ├── analyst_agent.py
│   └── risk_agent.py
├── api/                       # API 라우터
│   ├── __init__.py
│   ├── companies.py
│   ├── signals.py
│   └── reports.py
├── tasks/                     # Celery 태스크
│   ├── __init__.py
│   ├── collection_tasks.py
│   └── analysis_tasks.py
└── utils/                     # 유틸리티
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

---

## 4.7 AI/분석 기술 스택

```python
# AI/분석 관련 라이브러리

anthropic>=0.39.0              # Claude API
sentence-transformers>=2.2.0   # 텍스트 임베딩
kiwipiepy>=0.17.0              # 한국어 형태소 분석기 (Kiwi)
pandas>=2.1.0                  # 데이터 처리
numpy>=1.26.0                  # 수치 계산
scikit-learn>=1.3.0            # 머신러닝 (스코어링)
optuna>=3.4.0                  # 하이퍼파라미터 최적화
```

### 한국어 NLP 파이프라인

```python
from kiwipiepy import Kiwi

kiwi = Kiwi()

def analyze_korean_text(text: str) -> dict:
    """한국어 텍스트의 형태소 분석 및 감성 점수를 산출합니다."""
    tokens = kiwi.tokenize(text)
    nouns = [t.form for t in tokens if t.tag.startswith('NN')]
    verbs = [t.form for t in tokens if t.tag.startswith('VV')]

    return {
        "tokens": tokens,
        "nouns": nouns,
        "verbs": verbs,
        "noun_count": len(nouns),
    }
```

---

## 4.8 프론트엔드 기술 스택

```
# 프론트엔드 기술 스택

Next.js 14+         # React 프레임워크 (App Router)
TypeScript           # 타입 안전성
Tailwind CSS         # 유틸리티 CSS
Recharts             # 차트 라이브러리
TradingView LWC      # 주가 차트 (TradingView Lightweight Charts)
Supabase             # 실시간 DB + 인증
```

### 주요 화면 구성

| 화면 | 경로 | 기능 |
|------|------|------|
| 대시보드 | `/` | 전체 신호 요약, 상위 종목 |
| 종목 상세 | `/stock/[ticker]` | 개별 종목 분석 결과 |
| 신호 목록 | `/signals` | 전체 신호 타임라인 |
| 리포트 | `/reports` | 생성된 분석 리포트 목록 |
| 백테스팅 | `/backtest` | 과거 신호 성과 |
| 설정 | `/settings` | API 키, 알림 설정 |

---

## 4.9 인프라 및 배포

### Docker 구성

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/stock_analyst
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis

  celery_worker:
    build: .
    command: celery -A src.stock_analyst.tasks worker -l info
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A src.stock_analyst.tasks beat -l info
    depends_on:
      - redis

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=stock_analyst
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"

volumes:
  pgdata:
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

---

## 4.10 데이터 흐름 다이어그램

### 일간 자동 수집 흐름

```
[매일 새벽 5시 - Celery Beat]
         │
         ▼
┌─────────────────┐
│  수집 태스크 시작  │
└────────┬────────┘
         │
    ┌────┼────┬────────┬──────────┐
    ▼    ▼    ▼        ▼          ▼
  DART 나라장터 뉴스  채용사이트   해외공시
    │    │    │        │          │
    ▼    ▼    ▼        ▼          ▼
┌─────────────────────────────────────┐
│           PostgreSQL 저장            │
│    + ChromaDB 벡터 인덱싱            │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│     Claude AI 분석 (Tool Use)        │
│  신호 스코어링 + 리포트 생성          │
└────────────────┬────────────────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
       대시보드  텔레그램  이메일
       업데이트   알림     리포트
```

### 실시간 알림 흐름

```
[공시 감지 / 이상 거래량]
         │
         ▼
┌─────────────────────┐
│  임계값 초과 판단     │  score >= 80 ?
└────────┬────────────┘
         │ Yes
         ▼
┌─────────────────────┐
│  Claude 긴급 분석    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  텔레그램 즉시 알림   │
└─────────────────────┘
```

---

## 핵심 요약

```
1. 4개 레이어 아키텍처 = 수집 → 저장 → AI 분석 → 출력
2. 백엔드 = FastAPI + Celery + SQLAlchemy + httpx
3. AI = Claude API (Tool Use + RAG) + 한국어 NLP (Kiwi)
4. 프론트엔드 = Next.js + Tailwind + Recharts + Supabase
5. 인프라 = Docker Compose + GitHub Actions CI/CD
```

---

> **다음 문서**: [05. Claude 연동 설계](./05_claude_integration.md)
