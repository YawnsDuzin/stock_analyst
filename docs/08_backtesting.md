# 08. 백테스팅 및 검증

> **이 문서의 목적**: 신호의 실제 유효성을 검증하는 방법론, 백테스팅 구현, 편향 방지 전략을 상세히 설명합니다.

---

## 목차

- [8.1 백테스팅의 목적과 원칙](#81-백테스팅의-목적과-원칙)
- [8.2 신호 유효성 검증 방법](#82-신호-유효성-검증-방법)
- [8.3 핵심 성과 지표](#83-핵심-성과-지표)
- [8.4 백테스팅 편향과 방지책](#84-백테스팅-편향과-방지책)
- [8.5 Walk-Forward 분석](#85-walk-forward-분석)
- [8.6 실전 검증 프로세스](#86-실전-검증-프로세스)

---

## 8.1 백테스팅의 목적과 원칙

### 목적

1. **신호 유효성 확인**: 각 대안 데이터 신호가 실제로 주가 예측력을 가지는지 검증
2. **가중치 최적화**: 어떤 신호가 가장 강한 예측력을 가지는지 정량화
3. **리스크 측정**: 전략의 최대 손실(MDD), 변동성 등 리스크 프로파일 확인
4. **과적합 방지**: 과거에만 통하는 전략인지, 미래에도 유효한지 검증

### 원칙

```
1. 미래 정보 사용 금지 (Look-Ahead Bias 방지)
2. 생존 편향 제거 (상장폐지 종목 포함)
3. 거래 비용 반영 (수수료, 슬리피지, 시장 충격)
4. 충분한 데이터 기간 (최소 3년, 권장 5년)
5. 아웃오브샘플 검증 필수
```

---

## 8.2 신호 유효성 검증 방법

### BackTester 클래스

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class BackTester:
    """신호의 과거 유효성을 검증하는 백테스터"""

    def __init__(self, price_data: pd.DataFrame):
        """
        Args:
            price_data: 일별 주가 데이터 (columns: date, ticker, close, volume)
        """
        self.price_data = price_data

    def test_signal(
        self,
        signal_name: str,
        lookback_years: int = 3
    ) -> dict:
        """
        신호 발생 후 N일/N주 뒤 주가 성과를 측정합니다.

        Args:
            signal_name: 테스트할 신호 이름
            lookback_years: 검증 기간 (년)

        Returns:
            검증 결과 딕셔너리
        """
        results = []

        for event in self.get_historical_signals(signal_name):
            # 각 기간별 수익률 계산
            price_after = {
                "5d":  self.get_return(event["ticker"], event["date"], 5),
                "20d": self.get_return(event["ticker"], event["date"], 20),
                "60d": self.get_return(event["ticker"], event["date"], 60),
            }
            results.append({**event, **price_after})

        df = pd.DataFrame(results)

        if df.empty:
            return {"error": "No historical signals found"}

        return {
            "signal_name": signal_name,
            "sample_size": len(df),
            "hit_rate_5d": float((df["5d"] > 0).mean()),
            "hit_rate_20d": float((df["20d"] > 0).mean()),
            "hit_rate_60d": float((df["60d"] > 0).mean()),
            "avg_return_5d": float(df["5d"].mean()),
            "avg_return_20d": float(df["20d"].mean()),
            "avg_return_60d": float(df["60d"].mean()),
            "sharpe_ratio": float(self.calc_sharpe(df["20d"])),
            "max_drawdown": float(df["20d"].min()),
            "win_loss_ratio": float(
                df[df["20d"] > 0]["20d"].mean() /
                abs(df[df["20d"] < 0]["20d"].mean())
                if (df["20d"] < 0).any() else float('inf')
            ),
        }

    def get_return(
        self,
        ticker: str,
        signal_date: str,
        forward_days: int
    ) -> float:
        """신호 발생일로부터 N일 후 수익률을 계산합니다."""
        ticker_data = self.price_data[
            self.price_data["ticker"] == ticker
        ].sort_values("date")

        signal_idx = ticker_data[
            ticker_data["date"] >= signal_date
        ].index

        if len(signal_idx) == 0:
            return 0.0

        start_idx = signal_idx[0]
        start_price = ticker_data.loc[start_idx, "close"]

        # forward_days 후 데이터 찾기
        future_data = ticker_data[
            ticker_data.index > start_idx
        ].head(forward_days)

        if future_data.empty:
            return 0.0

        end_price = future_data.iloc[-1]["close"]
        return (end_price - start_price) / start_price

    @staticmethod
    def calc_sharpe(returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """샤프 비율을 계산합니다."""
        if returns.std() == 0:
            return 0.0
        excess_return = returns.mean() - (risk_free_rate / 252)
        return excess_return / returns.std() * np.sqrt(252)

    def get_historical_signals(self, signal_name: str) -> list[dict]:
        """과거 신호 데이터를 조회합니다."""
        # 데이터베이스에서 과거 신호 조회
        # 실제 구현에서는 DB 쿼리
        pass
```

### 개별 신호 테스트 예시

```python
# 나라장터 신호 백테스트
procurement_results = backtester.test_signal("procurement_large_contract")
print(f"나라장터 대형 계약 신호:")
print(f"  표본 수: {procurement_results['sample_size']}")
print(f"  20일 적중률: {procurement_results['hit_rate_20d']:.1%}")
print(f"  20일 평균 수익률: {procurement_results['avg_return_20d']:.2%}")
print(f"  샤프 비율: {procurement_results['sharpe_ratio']:.2f}")

# 채용 신호 백테스트
hiring_results = backtester.test_signal("hiring_expansion")
print(f"\n채용 급증 신호:")
print(f"  표본 수: {hiring_results['sample_size']}")
print(f"  60일 적중률: {hiring_results['hit_rate_60d']:.1%}")
print(f"  60일 평균 수익률: {hiring_results['avg_return_60d']:.2%}")
```

---

## 8.3 핵심 성과 지표

### 신호 평가 지표

| 지표 | 설명 | 기준값 |
|------|------|--------|
| **적중률 (Hit Rate)** | 수익이 발생한 비율 | > 55% 유의미 |
| **평균 수익률** | 신호 후 평균 수익 | > 2% (20일) |
| **Information Coefficient (IC)** | 예측과 실제의 순위 상관 | > 0.05 유의미 |
| **샤프 비율** | 위험 대비 수익 | > 1.0 양호 |
| **최대 손실 (Max Drawdown)** | 최악의 개별 손실 | < -15% 주의 |
| **Win/Loss Ratio** | 이익/손실 비율 | > 1.5 양호 |

### Information Coefficient (IC) 계산

```python
from scipy import stats

def calculate_information_coefficient(
    predicted_scores: list[float],
    actual_returns: list[float]
) -> float:
    """
    예측 점수와 실제 수익률 간의 순위 상관계수를 계산합니다.
    Spearman Rank Correlation을 사용합니다.

    Args:
        predicted_scores: 예측 점수 리스트
        actual_returns: 실제 수익률 리스트

    Returns:
        IC 값 (-1 ~ 1)
    """
    ic, p_value = stats.spearmanr(predicted_scores, actual_returns)
    return ic
```

### 전략 수준 성과 지표

```python
def calculate_strategy_metrics(portfolio_returns: pd.Series) -> dict:
    """전략의 종합 성과 지표를 계산합니다."""
    cumulative = (1 + portfolio_returns).cumprod()

    return {
        "total_return": float(cumulative.iloc[-1] - 1),
        "annualized_return": float(
            (cumulative.iloc[-1] ** (252 / len(cumulative))) - 1
        ),
        "volatility": float(portfolio_returns.std() * np.sqrt(252)),
        "sharpe_ratio": float(
            portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)
        ),
        "max_drawdown": float(
            ((cumulative / cumulative.cummax()) - 1).min()
        ),
        "calmar_ratio": float(
            ((cumulative.iloc[-1] ** (252 / len(cumulative))) - 1) /
            abs(((cumulative / cumulative.cummax()) - 1).min())
        ),
    }
```

---

## 8.4 백테스팅 편향과 방지책

### 주의할 편향 4가지

#### 1. 생존 편향 (Survivorship Bias)

현재 상장된 종목만 분석하면 과거에 상장폐지된 종목(대부분 부진 기업)을 누락합니다.

```python
# ❌ 잘못된 방법: 현재 상장 종목만 사용
current_tickers = get_current_listed_tickers()

# ✅ 올바른 방법: 시점별 상장 종목 사용
def get_universe_at_date(date: str) -> list[str]:
    """특정 시점에 상장되어 있던 종목 리스트를 반환합니다."""
    return db.query(
        "SELECT ticker FROM historical_listings "
        "WHERE listed_date <= %s AND (delisted_date IS NULL OR delisted_date > %s)",
        (date, date)
    )
```

#### 2. 미래 데이터 누출 (Look-Ahead Bias)

신호 시점과 실제 데이터 공개 시점의 차이를 확인해야 합니다.

```python
# ❌ 잘못된 방법: 데이터 생성일 기준
signal_date = contract["created_date"]

# ✅ 올바른 방법: 데이터 공개일 기준 (접근 가능 시점)
signal_date = contract["published_date"]  # 실제 공개 시점
# + 1일 여유 (데이터 수집/처리 시간 고려)
tradable_date = signal_date + timedelta(days=1)
```

#### 3. 과적합 (Overfitting)

백테스팅 성과가 좋아도 실제와 괴리가 발생할 수 있습니다.

```python
# 방지책 1: 아웃오브샘플 분할
train_data = data[data["date"] < "2023-01-01"]  # 학습용
test_data = data[data["date"] >= "2023-01-01"]  # 검증용

# 방지책 2: 파라미터 수 최소화
# 가중치 6개만 사용 (과도한 파라미터 지양)

# 방지책 3: Walk-Forward Analysis (아래 섹션 참조)
```

#### 4. 거래비용 미반영 (Transaction Cost Neglect)

```python
# 반드시 포함해야 할 비용
TRANSACTION_COSTS = {
    "commission": 0.00015,    # 수수료 0.015% (편도)
    "slippage": 0.001,        # 슬리피지 0.1%
    "market_impact": 0.002,   # 시장 충격 0.2% (중소형주)
    "tax": 0.0023,            # 증권거래세 0.23% (매도 시)
}

def apply_transaction_costs(gross_return: float, is_sell: bool = False) -> float:
    """거래 비용을 차감한 순수익률을 계산합니다."""
    costs = TRANSACTION_COSTS["commission"] + TRANSACTION_COSTS["slippage"]
    if is_sell:
        costs += TRANSACTION_COSTS["tax"]
    return gross_return - costs
```

---

## 8.5 Walk-Forward 분석

과적합을 방지하는 가장 효과적인 방법입니다.

### 원리

```
전체 기간: |--------Train--------|--Test--|
                                 |
          1차: |---Train---|--Test--|
                           |
          2차:    |---Train---|--Test--|
                              |
          3차:       |---Train---|--Test--|
                                 |
          각 Test 기간의 성과를 합산하여 최종 평가
```

### 구현

```python
class WalkForwardAnalyzer:
    """Walk-Forward 분석으로 과적합을 방지합니다."""

    def __init__(
        self,
        train_months: int = 24,
        test_months: int = 6,
        step_months: int = 3
    ):
        self.train_months = train_months
        self.test_months = test_months
        self.step_months = step_months

    def analyze(
        self,
        data: pd.DataFrame,
        optimizer_fn,   # 가중치 최적화 함수
        scorer_fn       # 스코어 계산 함수
    ) -> dict:
        """Walk-Forward 분석을 실행합니다."""
        results = []
        start_date = data["date"].min()
        end_date = data["date"].max()

        current_start = start_date

        while True:
            train_end = current_start + pd.DateOffset(months=self.train_months)
            test_end = train_end + pd.DateOffset(months=self.test_months)

            if test_end > end_date:
                break

            # 학습 구간에서 최적 가중치 탐색
            train_data = data[
                (data["date"] >= current_start) & (data["date"] < train_end)
            ]
            optimal_weights = optimizer_fn(train_data)

            # 테스트 구간에서 성과 측정
            test_data = data[
                (data["date"] >= train_end) & (data["date"] < test_end)
            ]
            test_performance = scorer_fn(test_data, optimal_weights)

            results.append({
                "train_period": f"{current_start} ~ {train_end}",
                "test_period": f"{train_end} ~ {test_end}",
                "weights": optimal_weights,
                "performance": test_performance
            })

            current_start += pd.DateOffset(months=self.step_months)

        return {
            "periods": results,
            "avg_performance": np.mean([r["performance"] for r in results]),
            "stability": np.std([r["performance"] for r in results]),
        }
```

---

## 8.6 실전 검증 프로세스

### Paper Trading (모의 투자)

백테스팅 통과 후, 실제 자금 투입 전 반드시 모의 투자를 진행합니다.

```python
class PaperTrader:
    """실시간 신호로 모의 투자를 진행합니다."""

    def __init__(self, initial_capital: float = 100_000_000):
        self.capital = initial_capital
        self.positions = {}       # {ticker: {"shares": N, "entry_price": P}}
        self.trade_history = []
        self.daily_nav = []       # 일별 순자산

    def execute_signal(self, ticker: str, signal: str, score: float):
        """신호에 따라 모의 매매를 실행합니다."""
        current_price = self.get_current_price(ticker)

        if signal in ("STRONG_BUY", "BUY") and ticker not in self.positions:
            # 매수
            position_size = self.calculate_position_size(score)
            shares = int(position_size / current_price)
            self.positions[ticker] = {
                "shares": shares,
                "entry_price": current_price,
                "entry_date": datetime.now().isoformat()
            }
            self.capital -= shares * current_price
            self.log_trade("BUY", ticker, shares, current_price)

        elif signal in ("SELL", "STRONG_SELL") and ticker in self.positions:
            # 매도
            pos = self.positions.pop(ticker)
            proceeds = pos["shares"] * current_price
            self.capital += proceeds
            self.log_trade("SELL", ticker, pos["shares"], current_price)

    def get_nav(self) -> float:
        """현재 순자산가치를 계산합니다."""
        positions_value = sum(
            pos["shares"] * self.get_current_price(ticker)
            for ticker, pos in self.positions.items()
        )
        return self.capital + positions_value
```

### 검증 단계 요약

```
Step 1: 백테스팅 (3년 과거 데이터)
  ↓ IC > 0.05, 적중률 > 55%, 샤프 > 1.0 통과

Step 2: Walk-Forward 분석
  ↓ 안정성 확인 (구간별 성과 편차 < 50%)

Step 3: Paper Trading (1~3개월)
  ↓ 실시간 성과 백테스팅 대비 70% 이상

Step 4: 소액 실전 투자
  ↓ 점진적 자금 확대

Step 5: 정규 운용
```

---

## 핵심 요약

```
1. 백테스팅 = 신호 발생 후 5/20/60일 수익률 측정
2. 핵심 지표 = IC, 적중률, 샤프비율, MDD
3. 4대 편향 주의 = 생존, 미래데이터, 과적합, 거래비용
4. Walk-Forward = 과적합 방지의 핵심 방법론
5. 실전 전 = Paper Trading 최소 1개월 필수
```

---

> **다음 문서**: [09. 리스크 관리 및 법적 주의사항](./09_risk_management.md)
