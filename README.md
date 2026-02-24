# Stock Analyst - Claude 기반 증권 애널리스트 시스템

> 대형 기관이 주목하지 않는 틈새에서 정보 비대칭성을 활용하여 알파를 발굴하는 AI 애널리스트 시스템

---

## 핵심 컨셉

```
일반 애널리스트:  재무제표 → EPS 추정 → PER 비교 → 목표주가
이 시스템:       숨겨진 공개 데이터 → 선행 신호 발굴 → 시장보다 빠른 판단
```

### 3가지 알파 원천

| 구분 | 설명 | 선행성 |
|------|------|--------|
| **정보 비대칭** | 공개됐지만 아무도 안 보는 데이터 | 1~4주 |
| **해석 비대칭** | 데이터는 있지만 잘못 해석되는 경우 | 1~2분기 |
| **속도 비대칭** | 시장이 반응하기 전 먼저 포지션 | 수일~수주 |

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                   데이터 수집 레이어                    │
│  나라장터  DART  HIRA  KIPRIS  크롤러  AIS  위성     │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│                   데이터 저장 레이어                    │
│    PostgreSQL (정형)  +  ChromaDB (비정형/벡터)      │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│                   AI 분석 레이어                        │
│              Claude API (Tool Use + RAG)              │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│                   출력 레이어                           │
│     Next.js 대시보드  +  텔레그램 봇  +  이메일      │
└─────────────────────────────────────────────────────┘
```

---

## 빠른 시작

### 1. 의존성 설치

```bash
# Python 3.11+ 필요
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 기본 의존성
pip install -r requirements.txt

# 개발 의존성 포함
pip install -e ".[dev]"
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 설정
```

필수 API 키:
- `ANTHROPIC_API_KEY`: Claude API (https://console.anthropic.com)
- `DART_API_KEY`: DART 전자공시 (https://opendart.fss.or.kr)
- `DATA_GO_KR_API_KEY`: 공공데이터포털 (https://www.data.go.kr)

### 3. 테스트 실행

```bash
# 전체 테스트 (61개)
pytest tests/ -v

# 모듈별 테스트
pytest tests/test_config.py -v
pytest tests/test_scoring/ -v
pytest tests/test_analysis/ -v
pytest tests/test_data_sources/ -v
```

### 4. 개발 서버 실행

```bash
uvicorn src.stock_analyst.main:app --reload --port 8000
```

---

## 프로젝트 구조

```
stock_analyst/
├── docs/                          # 상세 설계 문서 (10개 챕터)
│   ├── 00_index.md               # 문서 목차
│   ├── 01_core_philosophy.md     # 핵심 철학 및 전략 방향
│   ├── 02_data_sources.md        # 차별화된 데이터 소스 전략
│   ├── 03_analysis_methodology.md # 분석 방법론 상세
│   ├── 04_tech_stack.md          # 기술 스택 및 아키텍처
│   ├── 05_claude_integration.md  # Claude 연동 설계
│   ├── 06_scoring_system.md      # 통합 스코어링 시스템
│   ├── 07_development_roadmap.md # 개발 로드맵
│   ├── 08_backtesting.md         # 백테스팅 및 검증
│   ├── 09_risk_management.md     # 리스크 관리 및 법적 주의사항
│   └── 10_execution_plan.md      # 우선순위 실행 계획
├── src/stock_analyst/             # 소스 코드
│   ├── config.py                 # 설정 관리
│   ├── main.py                   # FastAPI 앱
│   ├── data_sources/             # 데이터 수집기
│   │   ├── base.py              # BaseCollector (추상 클래스)
│   │   ├── dart_collector.py    # DART 전자공시
│   │   └── procurement_collector.py # 나라장터
│   ├── analysis/                 # 분석 엔진
│   │   └── sentiment_analyzer.py # 감성 분석
│   ├── scoring/                  # 스코어링
│   │   └── alpha_scorer.py      # AlphaScorer
│   ├── agents/                   # Claude 에이전트
│   ├── notifications/            # 알림 (텔레그램 등)
│   ├── models/                   # 데이터 모델
│   ├── api/                      # API 라우터
│   ├── tasks/                    # Celery 태스크
│   └── utils/                    # 유틸리티
├── tests/                         # 유닛 테스트 (61개)
│   ├── test_config.py
│   ├── test_data_sources/
│   ├── test_analysis/
│   └── test_scoring/
├── pyproject.toml                 # 프로젝트 설정
├── requirements.txt               # 의존성
├── .env.example                   # 환경 변수 템플릿
└── .gitignore
```

---

## 핵심 모듈

### AlphaScorer - 통합 스코어링

6개 데이터 소스의 신호를 가중 평균하여 0~100 점수를 산출합니다.

```python
from stock_analyst.scoring import AlphaScorer

scorer = AlphaScorer()
result = scorer.calculate_score({
    "government_contract": 90,  # 나라장터 대형 계약 감지
    "hiring_signal": 75,        # AI 채용 급증
    "language_change": 70,      # 컨퍼런스콜 톤 개선
    "alternative_data": 60,     # 검색 트렌드 상승
    "sentiment_extreme": 50,    # 중립
    "supply_chain": 65,         # 고객사 전망 긍정
})

print(result["total_score"])  # 74.25
print(result["signal"])       # "BUY"
```

### SentimentAnalyzer - 한국어 감성 분석

```python
from stock_analyst.analysis.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze("올해 실적이 사상 최대를 기록하며 시장 점유율 확대가 가시적입니다.")
print(result["overall"])  # "POSITIVE"
```

### BaseCollector - 데이터 수집 기반

```python
from stock_analyst.data_sources.base import BaseCollector

# 재시도 로직이 내장된 비동기 수집
data = await collector.collect_with_retry(max_retries=3)
```

---

## 데이터 소스

| 데이터 소스 | 차별화 | 비용 | 상태 |
|------------|--------|------|------|
| 나라장터 낙찰 데이터 | 매우 높음 | 무료 | 구현 완료 |
| DART 전자공시 | 매우 높음 | 무료 | 구현 완료 |
| 채용공고 크롤러 | 높음 | 무료 | 예정 (Phase 2) |
| HIRA 의약품 데이터 | 높음 | 무료 | 예정 (Phase 2) |
| 해외 공시 (SEC, FDA) | 높음 | 무료 | 예정 (Phase 2) |
| 컨퍼런스콜 NLP | 높음 | 무료 | 감성분석 구현 |
| 규제/정책 추적 | 중간 | 무료 | 예정 |
| 위성/AIS 데이터 | 매우 높음 | 유료 | 예정 (Phase 4) |

---

## 개발 로드맵

| Phase | 목표 | 핵심 산출물 |
|-------|------|-----------|
| **Phase 1** (MVP) | DART + Claude + 텔레그램 | 기본 분석 리포트 |
| **Phase 2** (파이프라인) | 대안 데이터 3~4개 연결 | 자동 신호 스캐너 |
| **Phase 3** (자동화) | Celery + 대시보드 | 실시간 모니터링 |
| **Phase 4** (검증) | 백테스팅 + 최적화 | 검증된 알파 전략 |

상세 로드맵은 [docs/07_development_roadmap.md](./docs/07_development_roadmap.md) 참조.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **백엔드** | Python 3.11+, FastAPI, SQLAlchemy, Celery |
| **AI** | Claude API (Anthropic), Sentence Transformers, Kiwi NLP |
| **데이터** | PostgreSQL, ChromaDB, Redis |
| **프론트엔드** | Next.js, Tailwind CSS, Recharts |
| **인프라** | Docker, GitHub Actions |

---

## 문서

전체 설계 문서는 `docs/` 폴더에 10개 챕터로 정리되어 있습니다.

| 챕터 | 문서 | 내용 |
|------|------|------|
| 01 | [핵심 철학](./docs/01_core_philosophy.md) | 틈새 전략, 알파 원천, 핵심 원칙 |
| 02 | [데이터 소스](./docs/02_data_sources.md) | 9가지 대안 데이터 소스 상세 |
| 03 | [분석 방법론](./docs/03_analysis_methodology.md) | 멀티 레이어 분석, 5단계 검증 |
| 04 | [기술 스택](./docs/04_tech_stack.md) | 아키텍처, DB 설계, 인프라 |
| 05 | [Claude 연동](./docs/05_claude_integration.md) | Tool Use, RAG, 멀티 에이전트 |
| 06 | [스코어링](./docs/06_scoring_system.md) | AlphaScorer, 가중치, 대시보드 |
| 07 | [개발 로드맵](./docs/07_development_roadmap.md) | Phase 1~4, PRD 템플릿 |
| 08 | [백테스팅](./docs/08_backtesting.md) | 검증 방법, Walk-Forward, 편향 |
| 09 | [리스크 관리](./docs/09_risk_management.md) | 법적 준수, 포지션 관리 |
| 10 | [실행 계획](./docs/10_execution_plan.md) | 우선순위, 주차별 계획, API 참고 |

---

## 면책 고지

본 프로젝트는 시스템 구축 참고용이며 투자 조언이 아닙니다.
모든 투자 결정은 개인 책임이며, 반드시 백테스팅과 소액 실험 후 점진적으로 확대하시기 바랍니다.
공개된 데이터만 활용하며, 미공개 중요 정보(MNPI)는 절대 사용하지 않습니다.

---

## 라이선스

MIT License
