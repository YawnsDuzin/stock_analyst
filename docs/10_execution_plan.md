# 10. 우선순위 실행 계획

> **이 문서의 목적**: 데이터 접근성, 구현 난이도, 차별화 가치를 종합한 우선순위 실행 계획과 참고 자료를 제공합니다.

---

## 목차

- [10.1 우선순위 매트릭스](#101-우선순위-매트릭스)
- [10.2 주차별 실행 계획](#102-주차별-실행-계획)
- [10.3 마일스톤 정의](#103-마일스톤-정의)
- [10.4 API 및 데이터 소스 참고](#104-api-및-데이터-소스-참고)
- [10.5 개발 환경 초기 설정 가이드](#105-개발-환경-초기-설정-가이드)

---

## 10.1 우선순위 매트릭스

데이터 접근성, 구현 난이도, 차별화 가치를 종합한 우선순위입니다.

| 순위 | 항목 | 난이도 | 차별화 | API 비용 | 설명 |
|------|------|--------|--------|---------|------|
| ⭐1 | 나라장터 낙찰 데이터 | 낮음 | 매우 높음 | 무료 | 공공API, 강력한 선행지표 |
| ⭐2 | DART 컨퍼런스콜 NLP | 중간 | 높음 | 무료 | DART API + Claude NLP |
| ⭐3 | 채용공고 크롤러 | 중간 | 높음 | 무료 | 웹크롤링, 주간 분석 |
| 4 | 해외 공시 연계 분석 | 중간 | 높음 | 무료 | SEC EDGAR, ClinicalTrials |
| 5 | 규제 변화 추적 | 낮음 | 중간 | 무료 | 국회 의안, 행정예고 |
| 6 | 소셜 역발상 전략 | 중간 | 중간 | 무료 | 커뮤니티 감성분석 |
| 7 | 공급망 역추적 | 높음 | 높음 | 무료 | DART 사업보고서 파싱 |
| 8 | 위성/AIS 데이터 | 높음 | 매우 높음 | 유료 | 고급 데이터, 고비용 |

---

## 10.2 주차별 실행 계획

### Week 1-2: MVP 핵심 (나라장터 + DART + Claude + 텔레그램)

```
Week 1:
  Day 1-2: 프로젝트 구조 설정, 의존성 설치
  Day 3-4: DART API 연동 (공시 조회, 사업보고서)
  Day 5:   Claude API 기본 연동 (분석 프롬프트)

Week 2:
  Day 1-2: 나라장터 API 연동 (낙찰 데이터 수집)
  Day 3:   Claude Tool Use 구현 (DART + 나라장터)
  Day 4:   텔레그램 봇 알림 구현
  Day 5:   통합 테스트 및 MVP 완성
```

**완료 기준**: `/analyze 005930` → 분석 리포트 → 텔레그램 수신

### Week 3-4: 채용공고 + NLP 감성 분석

```
Week 3:
  Day 1-2: 채용사이트 크롤러 구현 (사람인, 원티드)
  Day 3:   채용 변화 분석 로직
  Day 4-5: 뉴스 크롤러 + Claude 감성 분석

Week 4:
  Day 1-2: DART 사업보고서 YoY 비교 NLP
  Day 3:   ChromaDB RAG 기본 구성
  Day 4-5: 신호 통합 및 알림 고도화
```

**완료 기준**: 4개 데이터 소스 자동 수집 + 일간 신호 리포트

### Week 5-6: AlphaScorer 통합 + 대시보드

```
Week 5:
  Day 1-2: AlphaScorer 모듈 구현
  Day 3:   Celery 스케줄러 설정 (자동 수집)
  Day 4-5: PostgreSQL 마이그레이션 (SQLite → PostgreSQL)

Week 6:
  Day 1-3: Next.js 대시보드 (메인 + 상세)
  Day 4:   Supabase 실시간 연동
  Day 5:   대시보드 배포 (Vercel/Docker)
```

**완료 기준**: 실시간 대시보드 + 자동 스케줄링 + 통합 스코어

### Week 7-8: 백테스팅 + 가중치 최적화

```
Week 7:
  Day 1-2: 과거 데이터 수집 (3년치 주가 + 신호)
  Day 3-4: BackTester 구현 및 개별 신호 검증
  Day 5:   Walk-Forward 분석 구현

Week 8:
  Day 1-2: Optuna 가중치 최적화
  Day 3:   Paper Trading 시뮬레이터
  Day 4:   멀티 에이전트 구조 전환
  Day 5:   최종 통합 테스트 및 문서화
```

**완료 기준**: 검증된 가중치 + 백테스팅 리포트 + Paper Trading 시작

---

## 10.3 마일스톤 정의

### M1: MVP 완성

```
□ DART API 연동 정상 작동
□ 나라장터 API 연동 정상 작동
□ Claude Tool Use 분석 리포트 생성
□ 텔레그램 알림 수신 확인
□ SQLite 데이터 저장 확인
□ 유닛 테스트 통과 (핵심 모듈)
```

### M2: 데이터 파이프라인 완성

```
□ 채용공고 크롤러 정상 작동 (주간)
□ 뉴스 크롤러 정상 작동 (일간)
□ NLP 감성 분석 기능 작동
□ ChromaDB RAG 검색 정상
□ 4개 데이터 소스 자동 수집
```

### M3: 자동화 + 대시보드

```
□ Celery 스케줄러 자동 실행
□ AlphaScorer 통합 점수 계산
□ Next.js 대시보드 배포
□ 실시간 알림 시스템 작동
□ PostgreSQL 마이그레이션 완료
```

### M4: 검증 + 고도화

```
□ 백테스팅 완료 (3년, IC > 0.05)
□ Walk-Forward 분석 통과
□ 가중치 최적화 완료
□ Paper Trading 시작
□ 멀티 에이전트 구조 작동
```

---

## 10.4 API 및 데이터 소스 참고

### 무료 API 목록

| 데이터 소스 | URL | API 키 | 일일 한도 |
|------------|-----|--------|----------|
| 나라장터 API | https://www.data.go.kr | 발급 필요 | 1,000건 |
| DART 전자공시 | https://opendart.fss.or.kr | 발급 필요 | 10,000건 |
| HIRA 의약품 | https://opendata.hira.or.kr | 조건부 | 제한적 |
| KIPRIS 특허 | https://plus.kipris.or.kr | 발급 필요 | 제한적 |
| 네이버 데이터랩 | https://datalab.naver.com | API 키 | 제한적 |
| 구글 트렌드 | pytrends 라이브러리 | 불필요 | 자체 제한 |
| ClinicalTrials | https://clinicaltrials.gov/api | 불필요 | 자체 제한 |
| SEC EDGAR | https://www.sec.gov/edgar | 불필요 | 10req/sec |

### 유료 API 목록

| 데이터 소스 | URL | 예상 비용 |
|------------|-----|----------|
| MarineTraffic AIS | https://www.marinetraffic.com | 월 $100~ |
| Planet 위성 | https://www.planet.com | 월 $100~ |
| KRX 시세 | 한국거래소 | 조건부 무료 |

### Python 라이브러리 참고

| 라이브러리 | 용도 | 설치 |
|-----------|------|------|
| `anthropic` | Claude API | `pip install anthropic` |
| `dart-fss` | DART API | `pip install dart-fss` |
| `pykrx` | KRX 주가 데이터 | `pip install pykrx` |
| `pytrends` | 구글 트렌드 | `pip install pytrends` |
| `kiwipiepy` | 한국어 NLP | `pip install kiwipiepy` |
| `playwright` | 웹 크롤링 | `pip install playwright` |
| `chromadb` | 벡터 DB | `pip install chromadb` |

---

## 10.5 개발 환경 초기 설정 가이드

### 1단계: Python 환경 설정

```bash
# Python 3.12+ 필요
python --version

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 필수 API 키 설정
# ANTHROPIC_API_KEY=sk-ant-...
# DART_API_KEY=...
# DATA_GO_KR_API_KEY=...
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_CHAT_ID=...
```

### 3단계: 데이터베이스 설정

```bash
# 개발 환경: SQLite (설정 불필요)
# 프로덕션: PostgreSQL
docker run -d --name stock_analyst_db \
  -e POSTGRES_DB=stock_analyst \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16
```

### 4단계: 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 특정 모듈 테스트
pytest tests/test_config.py -v
pytest tests/test_scoring/ -v
```

### 5단계: 개발 서버 실행

```bash
# FastAPI 개발 서버
uvicorn src.stock_analyst.main:app --reload --port 8000

# Celery 워커 (별도 터미널)
celery -A src.stock_analyst.tasks worker -l info
```

---

## 핵심 요약

```
우선순위: 나라장터 > DART NLP > 채용공고 > 해외공시 > 나머지
실행 순서: MVP(2주) → 파이프라인(2주) → 대시보드(2주) → 백테스팅(2주)
필수 API: DART(무료), 나라장터(무료), Anthropic(유료), KRX(무료/조건부)
초기 설정: Python 3.12 + venv + .env + SQLite → 점진적 확장
```

---

> **면책 고지**: 본 문서는 시스템 구축 참고용이며 투자 조언이 아닙니다.
> 모든 투자 결정은 개인 책임이며, 반드시 백테스팅과 소액 실험 후 점진적으로 확대하시기 바랍니다.

---

*작성일: 2025년 1월 | Claude AI 기반 증권 애널리스트 시스템 설계 문서 v1.0*

> **처음으로**: [00. 문서 목차](./00_index.md)
