# 03. 분석 방법론 상세

> **이 문서의 목적**: 시스템이 사용하는 멀티 레이어 분석 프레임워크와 투자 아이디어 검증 프로세스를 상세히 설명합니다.

---

## 목차

- [3.1 멀티 레이어 분석 프레임](#31-멀티-레이어-분석-프레임)
- [3.2 투자 아이디어 검증 프로세스](#32-투자-아이디어-검증-프로세스)
- [3.3 각 레이어별 상세 분석 방법](#33-각-레이어별-상세-분석-방법)
- [3.4 신호 교차 검증 매트릭스](#34-신호-교차-검증-매트릭스)
- [3.5 분석 결과물 형식](#35-분석-결과물-형식)

---

## 3.1 멀티 레이어 분석 프레임

시스템은 4개의 분석 레이어를 계층적으로 적용합니다. 상위 레이어에서 매크로 환경을 파악한 후, 하위 레이어에서 개별 종목을 분석합니다.

### 전체 구조

```
Layer 1: 매크로 환경  (Top-Down)
  → 금리, 환율, 원자재 가격, 글로벌 경기 사이클
  │
  ▼
Layer 2: 섹터 포지셔닝  (Sector Rotation)
  → 정책 수혜, 기술 사이클, 수급 변화
  │
  ▼
Layer 3: 기업 개별 신호  (Bottom-Up)
  → 대안 데이터 신호, 내부자 거래, 실적 모멘텀
  │
  ▼
Layer 4: 시장 수급  (Timing)
  → 기관/외인 방향성, 공매도 변화, 프로그램 매매
```

### 레이어 간 상호작용

각 레이어는 독립적으로 점수를 산출하지만, 최종 판단에서는 레이어 간 **정합성(Coherence)**을 검증합니다.

| 시나리오 | Layer1 | Layer2 | Layer3 | Layer4 | 판단 |
|---------|--------|--------|--------|--------|------|
| 이상적 Buy | 긍정 | 수혜 섹터 | 강한 신호 | 매수 유입 | **Strong Buy** |
| 혼합 신호 | 부정 | 수혜 섹터 | 강한 신호 | 중립 | 신중한 Buy (규모 축소) |
| 경고 | 긍정 | 수혜 섹터 | 강한 신호 | 대량 매도 | **보류** (수급 확인 필요) |
| 역발상 | 부정 | 비수혜 | 강한 신호 | 극단적 매도 | 역발상 Buy 검토 |

---

## 3.2 투자 아이디어 검증 프로세스

모든 투자 아이디어는 아래 5단계 프로세스를 거쳐 검증합니다. Claude에게 각 단계별 역할을 부여합니다.

### 5단계 검증 흐름

```
Step 1: 가설 설정
  "나라장터에서 A기업의 대형 계약이 발견됨"
  │
  ▼
Step 2: 반론 검토 (Claude: Devil's Advocate)
  "이 가설이 틀릴 수 있는 5가지 이유를 제시하라"
  │
  ▼
Step 3: 데이터 교차 검증
  "채용공고, 뉴스, 재무 데이터로 가설을 지지/반박"
  │
  ▼
Step 4: 리스크 사전 정의
  "이 포지션에서 손절할 조건은 무엇인가"
  │
  ▼
Step 5: 포지션 사이징
  "신호 강도에 따라 포트폴리오의 몇 %를 배분할 것인가"
```

### Step 1: 가설 설정

```python
class InvestmentHypothesis:
    """투자 가설을 구조화합니다."""

    def __init__(self, ticker: str, signal_source: str, description: str):
        self.ticker = ticker
        self.signal_source = signal_source      # 어떤 데이터 소스에서 발견
        self.description = description          # 가설 설명
        self.expected_catalyst = ""             # 예상 촉매 이벤트
        self.expected_timeframe = ""            # 실현 예상 기간
        self.confidence_level = 0.0             # 초기 신뢰도 (0~1)
```

### Step 2: 반론 검토

Claude에게 **Devil's Advocate** 역할을 부여하여 체계적으로 반론을 생성합니다.

```python
DEVILS_ADVOCATE_PROMPT = """
당신은 투자 가설의 약점을 찾는 전문 리스크 분석가입니다.
다음 투자 가설에 대해 반드시 5가지 이상의 반론을 제시하세요:

가설: {hypothesis}

반론 형식:
1. [반론 제목]: [설명] - 확률: [높음/중간/낮음] - 영향도: [높음/중간/낮음]
2. ...

특히 다음 관점에서 검토하세요:
- 이미 주가에 반영되었을 가능성
- 계약이 취소/축소될 수 있는 경우
- 마진율이 기대보다 낮을 가능성
- 경쟁사 동향
- 매크로 환경 변화 영향
"""
```

### Step 3: 데이터 교차 검증

최소 3개 이상의 독립적 데이터 소스에서 가설을 지지/반박하는 증거를 수집합니다.

```python
def cross_validate(hypothesis: InvestmentHypothesis) -> dict:
    """3개 이상의 데이터 소스로 가설을 교차 검증합니다."""
    evidence = {
        "supporting": [],     # 지지 증거
        "contradicting": [],  # 반박 증거
        "neutral": []         # 중립 증거
    }

    # 채용 데이터 확인
    hiring = check_hiring_signals(hypothesis.ticker)
    classify_evidence(evidence, hiring)

    # 뉴스 감성 확인
    news = check_news_sentiment(hypothesis.ticker)
    classify_evidence(evidence, news)

    # 재무 데이터 확인
    financial = check_financial_health(hypothesis.ticker)
    classify_evidence(evidence, financial)

    # 내부자 거래 확인
    insider = check_insider_trading(hypothesis.ticker)
    classify_evidence(evidence, insider)

    confidence = len(evidence["supporting"]) / (
        len(evidence["supporting"]) + len(evidence["contradicting"]) + 0.001
    )

    return {
        "evidence": evidence,
        "confidence": confidence,
        "recommendation": "PROCEED" if confidence > 0.6 else "REVIEW"
    }
```

### Step 4: 리스크 사전 정의

포지션 진입 전 반드시 손절 조건을 정의합니다.

```python
class RiskDefinition:
    """포지션의 리스크를 사전에 정의합니다."""

    def __init__(self, ticker: str, entry_price: float):
        self.ticker = ticker
        self.entry_price = entry_price
        self.stop_loss_price = 0.0           # 손절가
        self.stop_loss_reason = ""           # 손절 사유
        self.max_holding_period_days = 0     # 최대 보유 기간
        self.invalidation_events = []        # 가설 무효화 이벤트

    def set_stop_loss(self, percentage: float, reason: str):
        """손절 기준을 설정합니다."""
        self.stop_loss_price = self.entry_price * (1 - percentage)
        self.stop_loss_reason = reason
```

### Step 5: 포지션 사이징

신호 강도와 포트폴리오 상태에 따라 적정 배분 비율을 결정합니다.

```python
def calculate_position_size(
    signal_score: float,
    portfolio_value: float,
    current_positions: dict
) -> float:
    """신호 강도에 기반한 포지션 사이즈를 계산합니다."""

    # 기본 배분: 신호 점수에 비례
    base_allocation = signal_score / 100 * 0.10  # 최대 10%

    # 포트폴리오 집중도 조정
    total_invested = sum(current_positions.values())
    available = portfolio_value - total_invested

    # 최종 포지션 사이즈
    position_size = min(base_allocation * portfolio_value, available * 0.5)

    return position_size
```

---

## 3.3 각 레이어별 상세 분석 방법

### Layer 1: 매크로 환경 분석

| 지표 | 데이터 소스 | 해석 기준 |
|------|-----------|----------|
| 한국은행 기준금리 | 한국은행 API | 금리 인하기 = 성장주 유리, 금리 인상기 = 가치주 유리 |
| 원/달러 환율 | 한국은행 API | 원화 약세 = 수출주 유리, 원화 강세 = 내수주 유리 |
| 유가 (WTI) | 시장 데이터 | 유가 상승 = 정유/에너지, 유가 하락 = 항공/화학 |
| 글로벌 PMI | ISM, 마킷 | 50 이상 = 경기 확장, 50 이하 = 경기 수축 |
| VIX 지수 | CBOE | 20 이하 = 안정, 30 이상 = 공포 구간 |

### Layer 2: 섹터 포지셔닝

```python
class SectorAnalyzer:
    """섹터 로테이션 분석기"""

    SECTOR_CYCLE_MAP = {
        "경기 확장 초기": ["IT", "소비재", "산업재"],
        "경기 확장 후기": ["에너지", "소재", "금융"],
        "경기 수축 초기": ["헬스케어", "유틸리티", "필수소비재"],
        "경기 수축 후기": ["통신", "부동산", "채권"],
    }

    def get_recommended_sectors(self, macro_phase: str) -> list:
        """현재 매크로 국면에 맞는 추천 섹터를 반환합니다."""
        return self.SECTOR_CYCLE_MAP.get(macro_phase, [])
```

### Layer 3: 기업 개별 신호 분석

[02. 데이터 소스](./02_data_sources.md)에서 수집한 모든 대안 데이터를 개별 종목에 적용합니다.

### Layer 4: 시장 수급 분석

```python
def analyze_market_flow(ticker: str) -> dict:
    """기관/외인 수급 흐름을 분석합니다."""
    return {
        "foreign_net_buy_5d": get_foreign_flow(ticker, 5),      # 외인 5일 순매수
        "institution_net_buy_5d": get_institution_flow(ticker, 5), # 기관 5일 순매수
        "short_interest_ratio": get_short_interest(ticker),      # 공매도 비율
        "program_trading": get_program_flow(ticker),             # 프로그램 매매
        "volume_trend": calculate_volume_trend(ticker, 20),      # 거래량 추이
    }
```

---

## 3.4 신호 교차 검증 매트릭스

### 신호 조합별 신뢰도

| 조합 | 신호 A | 신호 B | 결합 신뢰도 | 비고 |
|------|--------|--------|-----------|------|
| 최강 | 나라장터 대형 계약 | 채용 급증 | 95% | 사업 확장 확실 |
| 강 | 컨퍼런스콜 톤 개선 | 내부자 매수 | 85% | 내부자도 낙관 |
| 중 | 검색량 급증 | 뉴스 긍정 | 65% | 단기 모멘텀 |
| 약 | 커뮤니티 낙관 | 거래량 급증 | 40% | 과열 주의 |
| 역발상 | 커뮤니티 극단적 비관 | 내부자 매수 | 80% | 역발상 매수 기회 |

### 상충 신호 처리 규칙

```python
def resolve_conflicting_signals(signals: dict) -> str:
    """상충하는 신호가 있을 때 처리 규칙을 적용합니다."""

    # 규칙 1: 내부자 행동 > 외부 감성
    if signals["insider"] == "BUY" and signals["community"] == "SELL":
        return "FOLLOW_INSIDER"  # 내부자를 따른다

    # 규칙 2: 정량 데이터 > 정성 데이터
    if signals["financial"] == "STRONG" and signals["sentiment"] == "NEGATIVE":
        return "FOLLOW_QUANTITATIVE"  # 숫자를 따른다

    # 규칙 3: 확인될 때까지 대기
    return "WAIT_FOR_CONFIRMATION"
```

---

## 3.5 분석 결과물 형식

### 표준 리포트 구조

```markdown
# [종목명] 분석 리포트
## 기본 정보
- 종목코드: XXXXXX
- 현재가: XX,XXX원
- 시가총액: X,XXX억원
- 섹터: XXXXX

## 투자의견
- **의견**: Buy / Hold / Sell
- **목표가**: XX,XXX원 (상승여력 XX%)
- **신호강도**: XX/100

## 핵심 근거 (최소 3가지)
1. [근거 1]: 구체적 데이터 수치
2. [근거 2]: 구체적 데이터 수치
3. [근거 3]: 구체적 데이터 수치

## 핵심 Catalyst
- [이벤트]: [예상 시점]

## 리스크 요인
1. [리스크 1]: 발생 확률 [X]%, 영향도 [높/중/낮]
2. [리스크 2]: 발생 확률 [X]%, 영향도 [높/중/낮]

## 손절 조건
- 가격 기준: XX,XXX원 이하 (현재가 대비 -X%)
- 이벤트 기준: [무효화 이벤트]

## 모니터링 지표
- [지표 1]: [현재값] → [주의 기준]
- [지표 2]: [현재값] → [주의 기준]

## 면책 고지
본 분석은 AI 기반 자동 분석이며 투자 조언이 아닙니다.
모든 투자 결정은 개인 책임입니다.
```

---

## 핵심 요약

```
1. 4개 분석 레이어 = 매크로 → 섹터 → 기업 → 수급
2. 5단계 검증 = 가설 → 반론 → 교차 검증 → 리스크 → 포지션 사이징
3. 교차 검증 = 최소 3개 독립 데이터 소스로 확인
4. 상충 신호 = 내부자 > 외부, 정량 > 정성, 불확실하면 대기
```

---

> **다음 문서**: [04. 기술 스택 및 아키텍처](./04_tech_stack.md)
