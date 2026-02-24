# 06. 통합 스코어링 시스템

> **이 문서의 목적**: AlphaScorer의 상세 설계, 각 신호별 점수 산출 방법, 가중치 시스템, 대시보드 설계를 설명합니다.

---

## 목차

- [6.1 AlphaScorer 개요](#61-alphascorer-개요)
- [6.2 개별 신호 스코어링](#62-개별-신호-스코어링)
- [6.3 가중치 시스템](#63-가중치-시스템)
- [6.4 통합 점수 계산](#64-통합-점수-계산)
- [6.5 점수 해석 기준](#65-점수-해석-기준)
- [6.6 신호 대시보드 설계](#66-신호-대시보드-설계)
- [6.7 가중치 최적화 (Optuna)](#67-가중치-최적화-optuna)

---

## 6.1 AlphaScorer 개요

AlphaScorer는 여러 데이터 소스에서 수집된 신호를 **0~100점** 사이의 단일 점수로 통합하는 시스템입니다.

### 설계 원칙

1. **재현성**: 동일 입력에 대해 항상 동일 점수 산출
2. **투명성**: 점수의 각 구성요소를 분해하여 확인 가능
3. **조정 가능**: 가중치를 사용자가 조정하거나 자동 최적화 가능
4. **시계열 추적**: 시간에 따른 점수 변화 추이 모니터링

### 핵심 구현

```python
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SignalScore:
    """개별 신호의 점수를 담는 데이터 클래스"""
    source: str          # 신호 출처
    raw_value: float     # 원시 값
    normalized: float    # 0~100 정규화 값
    confidence: float    # 0~1 신뢰도
    timestamp: datetime  # 측정 시각


class AlphaScorer:
    """모든 신호를 통합하여 투자 알파 스코어를 계산합니다."""

    DEFAULT_WEIGHTS = {
        "government_contract": 0.25,   # 나라장터 신호
        "hiring_signal":       0.20,   # 채용공고 신호
        "language_change":     0.20,   # NLP 언어 변화
        "alternative_data":    0.15,   # 위성/AIS/전력
        "sentiment_extreme":   0.10,   # 커뮤니티 역발상
        "supply_chain":        0.10,   # 공급망 신호
    }

    def __init__(self, weights: dict | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def calculate_score(self, ticker: str) -> dict:
        """종목의 통합 알파 스코어를 계산합니다."""
        scores = {
            "government_contract": self.score_procurement(ticker),
            "hiring_signal":       self.score_job_postings(ticker),
            "language_change":     self.score_text_nlp(ticker),
            "alternative_data":    self.score_satellite_ais(ticker),
            "sentiment_extreme":   self.score_community_sentiment(ticker),
            "supply_chain":        self.score_supply_chain(ticker),
        }

        total = sum(
            scores[k] * self.weights[k]
            for k in scores
        )

        return {
            "ticker": ticker,
            "total_score": round(total, 2),
            "breakdown": scores,
            "signal": self.interpret_score(total),
            "timestamp": datetime.now().isoformat()
        }

    def interpret_score(self, score: float) -> str:
        """점수를 투자 신호로 변환합니다."""
        if score >= 80:
            return "STRONG_BUY"
        if score >= 65:
            return "BUY"
        if score >= 40:
            return "HOLD"
        if score >= 25:
            return "SELL"
        return "STRONG_SELL"
```

---

## 6.2 개별 신호 스코어링

각 데이터 소스별로 0~100점 사이의 정규화된 점수를 산출합니다.

### 6.2.1 나라장터 신호 (government_contract)

```python
def score_procurement(self, ticker: str) -> float:
    """나라장터 낙찰 데이터 기반 점수"""
    contracts = self.get_recent_contracts(ticker, days=90)

    if not contracts:
        return 50  # 중립 (데이터 없음)

    total_amount = sum(c["amount"] for c in contracts)
    market_cap = self.get_market_cap(ticker)
    ratio = total_amount / market_cap if market_cap > 0 else 0

    # 계약금액/시가총액 비율 기반 점수
    if ratio >= 0.15:    return 95   # 시총 15% 이상 = 매우 강한 신호
    elif ratio >= 0.10:  return 85   # 시총 10% 이상
    elif ratio >= 0.05:  return 70   # 시총 5% 이상
    elif ratio >= 0.02:  return 60   # 시총 2% 이상
    else:                return 50   # 영향 미미
```

### 6.2.2 채용 신호 (hiring_signal)

```python
def score_job_postings(self, ticker: str) -> float:
    """채용공고 변화 기반 점수"""
    current_snapshot = self.get_hiring_snapshot(ticker, "current")
    prev_snapshot = self.get_hiring_snapshot(ticker, "4_weeks_ago")

    if not current_snapshot or not prev_snapshot:
        return 50

    # 채용 증감률
    change_rate = (
        (current_snapshot["total"] - prev_snapshot["total"])
        / max(prev_snapshot["total"], 1)
    )

    # 새 직무 카테고리 등장
    new_categories = set(current_snapshot["categories"]) - set(prev_snapshot["categories"])
    has_strategic_hire = any(
        cat in new_categories
        for cat in ["AI", "해외영업", "임상", "데이터"]
    )

    score = 50  # 기본 중립

    # 채용 증가 = 긍정
    if change_rate > 0.5:   score += 25
    elif change_rate > 0.2: score += 15
    elif change_rate > 0:   score += 5

    # 채용 감소 = 부정
    if change_rate < -0.3:  score -= 25
    elif change_rate < -0.1: score -= 10

    # 전략적 채용 = 추가 가점
    if has_strategic_hire:   score += 15

    return max(0, min(100, score))
```

### 6.2.3 NLP 언어 변화 (language_change)

```python
def score_text_nlp(self, ticker: str) -> float:
    """컨퍼런스콜/사업보고서 NLP 분석 기반 점수"""
    sentiment_delta = self.get_sentiment_change(ticker)
    evasion_detected = self.detect_evasion_patterns(ticker)
    keyword_shift = self.get_keyword_frequency_change(ticker)

    score = 50  # 기본 중립

    # 감성 변화
    if sentiment_delta > 0.2:   score += 20   # 크게 긍정적으로 변화
    elif sentiment_delta > 0.1: score += 10
    elif sentiment_delta < -0.2: score -= 20  # 크게 부정적으로 변화
    elif sentiment_delta < -0.1: score -= 10

    # 회피 패턴 감지
    if evasion_detected:  score -= 15  # 경고 신호

    # 긍정 키워드 증가
    if keyword_shift.get("positive_increase", 0) > 5:
        score += 10

    return max(0, min(100, score))
```

### 6.2.4 대안 데이터 (alternative_data)

```python
def score_satellite_ais(self, ticker: str) -> float:
    """위성/AIS/전력/검색 트렌드 기반 점수"""
    search_trend = self.get_search_trend_score(ticker)
    power_consumption = self.get_power_consumption_change(ticker)

    score = 50

    # 검색 트렌드 (계절성 조정 후 YoY)
    if search_trend > 30:    score += 20
    elif search_trend > 15:  score += 10
    elif search_trend < -15: score -= 10

    # 전력 소비 변화 (제조업)
    if power_consumption > 0.1:  score += 15
    elif power_consumption < -0.1: score -= 10

    return max(0, min(100, score))
```

### 6.2.5 커뮤니티 역발상 (sentiment_extreme)

```python
def score_community_sentiment(self, ticker: str) -> float:
    """커뮤니티 감성 극단치 역발상 점수"""
    bullish_ratio = self.get_community_bullish_ratio(ticker)
    volume_anomaly = self.detect_volume_anomaly(ticker)

    # 역발상 로직: 극단적 낙관 = 부정, 극단적 비관 = 긍정
    if bullish_ratio > 0.92 and volume_anomaly:
        return 20   # 과열 경고 (역발상 매도)
    elif bullish_ratio > 0.85:
        return 35   # 과열 주의
    elif bullish_ratio < 0.08:
        return 85   # 극단적 비관 (역발상 매수)
    elif bullish_ratio < 0.20:
        return 70   # 과도한 비관
    else:
        return 50   # 중립
```

### 6.2.6 공급망 신호 (supply_chain)

```python
def score_supply_chain(self, ticker: str) -> float:
    """공급망 분석 기반 점수"""
    customer_signals = self.get_major_customer_outlook(ticker)
    supplier_changes = self.get_supplier_changes(ticker)

    score = 50

    # 주요 고객사 실적/전망 개선
    if customer_signals.get("outlook") == "positive":
        score += 20
    elif customer_signals.get("outlook") == "negative":
        score -= 20

    # 공급망 변화 (새 고객 확보 등)
    if supplier_changes.get("new_customers", 0) > 0:
        score += 15

    return max(0, min(100, score))
```

---

## 6.3 가중치 시스템

### 기본 가중치

```python
DEFAULT_WEIGHTS = {
    "government_contract": 0.25,   # 가장 신뢰도 높은 선행지표
    "hiring_signal":       0.20,   # 중장기 방향 예측력
    "language_change":     0.20,   # 내부자 시각 반영
    "alternative_data":    0.15,   # 보조 확인용
    "sentiment_extreme":   0.10,   # 역발상 신호
    "supply_chain":        0.10,   # 밸류체인 연동
}
# 합계: 1.00
```

### 섹터별 가중치 조정

```python
SECTOR_WEIGHT_ADJUSTMENTS = {
    "IT_서비스": {
        "government_contract": 0.35,  # IT 서비스는 관급 비중 높음
        "hiring_signal": 0.25,
        "language_change": 0.15,
        "alternative_data": 0.10,
        "sentiment_extreme": 0.05,
        "supply_chain": 0.10,
    },
    "바이오": {
        "government_contract": 0.05,
        "hiring_signal": 0.20,
        "language_change": 0.25,  # 임상 결과 언어 변화 중요
        "alternative_data": 0.25, # FDA/임상 데이터
        "sentiment_extreme": 0.15,
        "supply_chain": 0.10,
    },
    "반도체": {
        "government_contract": 0.05,
        "hiring_signal": 0.15,
        "language_change": 0.20,
        "alternative_data": 0.25, # 해외 고객사 데이터
        "sentiment_extreme": 0.10,
        "supply_chain": 0.25,    # 밸류체인 매우 중요
    },
}
```

---

## 6.4 통합 점수 계산

### 가중 평균 + 신뢰도 보정

```python
def calculate_weighted_score(self, scores: dict, weights: dict) -> float:
    """가중 평균 점수를 계산합니다. 신뢰도가 낮은 신호는 가중치를 줄입니다."""
    weighted_sum = 0
    weight_sum = 0

    for key, score_obj in scores.items():
        if isinstance(score_obj, SignalScore):
            effective_weight = weights[key] * score_obj.confidence
            weighted_sum += score_obj.normalized * effective_weight
            weight_sum += effective_weight
        else:
            # 단순 숫자인 경우
            weighted_sum += score_obj * weights[key]
            weight_sum += weights[key]

    return weighted_sum / weight_sum if weight_sum > 0 else 50
```

---

## 6.5 점수 해석 기준

### 점수 ↔ 투자 신호 매핑

| 점수 범위 | 신호 | 설명 | 행동 |
|----------|------|------|------|
| 80~100 | **STRONG_BUY** | 다수의 강한 긍정 신호 | 적극 매수 검토 |
| 65~79 | **BUY** | 긍정 신호 우세 | 매수 검토 |
| 40~64 | **HOLD** | 혼합 신호 또는 중립 | 관망 |
| 25~39 | **SELL** | 부정 신호 우세 | 보유 시 매도 검토 |
| 0~24 | **STRONG_SELL** | 다수의 강한 부정 신호 | 즉시 매도 검토 |

### 추가 해석 규칙

```python
def get_detailed_interpretation(self, result: dict) -> dict:
    """점수에 대한 상세 해석을 제공합니다."""
    score = result["total_score"]
    breakdown = result["breakdown"]

    # 신호 일관성 체크
    high_signals = [k for k, v in breakdown.items() if v >= 70]
    low_signals = [k for k, v in breakdown.items() if v <= 30]

    consistency = "일관" if len(high_signals) >= 3 or len(low_signals) >= 3 else "혼합"

    # 핵심 드라이버 식별
    top_driver = max(breakdown, key=lambda k: abs(breakdown[k] - 50))

    return {
        "score": score,
        "consistency": consistency,
        "top_driver": top_driver,
        "strong_signals": high_signals,
        "weak_signals": low_signals,
        "interpretation": f"핵심 드라이버: {top_driver}, 신호 일관성: {consistency}"
    }
```

---

## 6.6 신호 대시보드 설계

### 메인 대시보드 레이아웃

```
┌────────────────────────────────────────────────────────┐
│  AlphaSignal Dashboard                    2025-01-15   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  📊 오늘의 Top Signal                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  TICKER  │  SCORE  │  SIGNAL     │  TOP CATALYST │  │
│  ├──────────┼─────────┼─────────────┼───────────────┤  │
│  │  A기업   │  87/100 │  STRONG_BUY │  나라장터 450억│  │
│  │  B기업   │  72/100 │  BUY        │  AI 채용 3배  │  │
│  │  C기업   │  31/100 │  SELL       │  임원 매도 급증│  │
│  │  D기업   │  15/100 │  STRONG_SELL│  CFO 퇴사     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  📈 신호 추이 차트 (최근 30일)                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  100 │                          *                │  │
│  │   80 │              *    *   *                   │  │
│  │   60 │  *    *   *                               │  │
│  │   40 │                                           │  │
│  │   20 │                                           │  │
│  │    0 └──────────────────────────────────────────│  │
│  │       D-30  D-25  D-20  D-15  D-10  D-5  Today  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  🔔 최근 알림                                          │
│  - 14:30 A기업: 나라장터 신규 대형 계약 감지 (450억)    │
│  - 11:00 C기업: 임원 주식 대량 매도 보고                │
│  - 09:15 B기업: AI 엔지니어 채용 공고 15건 신규 등록    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 종목 상세 페이지 레이아웃

```
┌────────────────────────────────────────────────────────┐
│  A기업 (005930)  │  현재가: 72,500원  │  시총: 4.3조   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  종합 점수: 87/100 (STRONG_BUY)                        │
│                                                        │
│  📊 신호 분해                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  나라장터     ████████████████████████  95/100   │  │
│  │  채용 신호    █████████████████░░░░░░  75/100   │  │
│  │  NLP 변화     ████████████████░░░░░░░  70/100   │  │
│  │  대안 데이터  █████████████████████░░  85/100   │  │
│  │  감성 역발상  ██████████████░░░░░░░░░  60/100   │  │
│  │  공급망       ████████████████████░░░  80/100   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  🔑 핵심 Catalyst                                      │
│  - 나라장터 450억원 낙찰 (시총 대비 10.5%)              │
│  - AI 엔지니어 채용 전년 대비 300% 증가                 │
│  - 컨퍼런스콜 감성 점수 +0.3 개선                      │
│                                                        │
│  ⚠️ 리스크 요인                                        │
│  - 매크로 환경 불확실성 (금리 동결 장기화)               │
│  - 섹터 밸류에이션 고점 논란                            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 6.7 가중치 최적화 (Optuna)

### 백테스팅 기반 자동 최적화

```python
import optuna

def optimize_weights(historical_signals: list, actual_returns: list) -> dict:
    """Optuna를 사용하여 최적 가중치를 탐색합니다."""

    def objective(trial):
        weights = {
            "government_contract": trial.suggest_float("gov", 0.05, 0.40),
            "hiring_signal": trial.suggest_float("hire", 0.05, 0.35),
            "language_change": trial.suggest_float("nlp", 0.05, 0.35),
            "alternative_data": trial.suggest_float("alt", 0.05, 0.25),
            "sentiment_extreme": trial.suggest_float("sent", 0.02, 0.20),
            "supply_chain": trial.suggest_float("supply", 0.02, 0.20),
        }

        # 가중치 합이 1이 되도록 정규화
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        # 수익률과의 상관관계 (Information Coefficient) 최대화
        scorer = AlphaScorer(weights=weights)
        predicted_scores = [
            scorer.calculate_weighted_score(sig, weights)
            for sig in historical_signals
        ]

        ic = calculate_information_coefficient(predicted_scores, actual_returns)
        return ic

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=500)

    return study.best_params
```

---

## 핵심 요약

```
1. AlphaScorer = 6개 신호를 가중 평균하여 0~100 점수 산출
2. 개별 스코어링 = 각 데이터 소스별 독립적인 0~100 점수
3. 점수 해석 = 80+ Strong Buy, 65+ Buy, 40+ Hold, 25+ Sell, 0+ Strong Sell
4. 가중치 최적화 = Optuna로 백테스팅 기반 자동 튜닝
5. 대시보드 = 메인 요약 + 종목 상세 + 신호 분해 시각화
```

---

> **다음 문서**: [07. 바이브 코딩 개발 로드맵](./07_development_roadmap.md)
