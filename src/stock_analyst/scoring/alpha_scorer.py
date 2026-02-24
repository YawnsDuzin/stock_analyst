"""
AlphaScorer - 통합 스코어링 시스템

여러 데이터 소스에서 수집된 신호를 0~100점 사이의 단일 점수로 통합합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SignalScore:
    """개별 신호의 점수를 담는 데이터 클래스"""

    source: str
    raw_value: float
    normalized: float  # 0~100
    confidence: float  # 0~1
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self.normalized = max(0.0, min(100.0, self.normalized))
        self.confidence = max(0.0, min(1.0, self.confidence))


class AlphaScorer:
    """모든 신호를 통합하여 투자 알파 스코어를 계산합니다."""

    DEFAULT_WEIGHTS = {
        "government_contract": 0.25,
        "hiring_signal": 0.20,
        "language_change": 0.20,
        "alternative_data": 0.15,
        "sentiment_extreme": 0.10,
        "supply_chain": 0.10,
    }

    SIGNAL_THRESHOLDS = {
        "STRONG_BUY": 80,
        "BUY": 65,
        "HOLD": 40,
        "SELL": 25,
    }

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self) -> None:
        """가중치 합이 1.0인지 검증합니다."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            # 자동 정규화
            self.weights = {
                k: v / total for k, v in self.weights.items()
            }

    def calculate_score(self, scores: dict[str, float]) -> dict:
        """
        종목의 통합 알파 스코어를 계산합니다.

        Args:
            scores: 신호별 점수 딕셔너리 (키: 신호명, 값: 0~100 점수)

        Returns:
            통합 스코어 결과
        """
        # 누락된 신호는 50 (중립)으로 처리
        complete_scores = {}
        for key in self.weights:
            complete_scores[key] = max(0.0, min(100.0, scores.get(key, 50.0)))

        total = sum(
            complete_scores[k] * self.weights[k]
            for k in self.weights
        )

        return {
            "total_score": round(total, 2),
            "breakdown": complete_scores,
            "signal": self.interpret_score(total),
            "weights_used": self.weights.copy(),
            "timestamp": datetime.now().isoformat(),
        }

    def interpret_score(self, score: float) -> str:
        """점수를 투자 신호로 변환합니다."""
        if score >= self.SIGNAL_THRESHOLDS["STRONG_BUY"]:
            return "STRONG_BUY"
        if score >= self.SIGNAL_THRESHOLDS["BUY"]:
            return "BUY"
        if score >= self.SIGNAL_THRESHOLDS["HOLD"]:
            return "HOLD"
        if score >= self.SIGNAL_THRESHOLDS["SELL"]:
            return "SELL"
        return "STRONG_SELL"

    def calculate_weighted_score(
        self,
        signal_scores: dict[str, SignalScore],
    ) -> float:
        """
        SignalScore 객체를 사용하여 신뢰도 보정된 가중 평균을 계산합니다.

        Args:
            signal_scores: 신호별 SignalScore 딕셔너리

        Returns:
            가중 평균 점수
        """
        weighted_sum = 0.0
        weight_sum = 0.0

        for key, signal in signal_scores.items():
            if key not in self.weights:
                continue
            effective_weight = self.weights[key] * signal.confidence
            weighted_sum += signal.normalized * effective_weight
            weight_sum += effective_weight

        if weight_sum == 0:
            return 50.0  # 중립

        return weighted_sum / weight_sum

    def get_detailed_interpretation(self, result: dict) -> dict:
        """점수에 대한 상세 해석을 제공합니다."""
        breakdown = result["breakdown"]

        high_signals = [k for k, v in breakdown.items() if v >= 70]
        low_signals = [k for k, v in breakdown.items() if v <= 30]

        consistency = (
            "consistent"
            if len(high_signals) >= 3 or len(low_signals) >= 3
            else "mixed"
        )

        # 중립(50)에서 가장 멀리 벗어난 신호 = 핵심 드라이버
        top_driver = max(breakdown, key=lambda k: abs(breakdown[k] - 50))

        return {
            "total_score": result["total_score"],
            "signal": result["signal"],
            "consistency": consistency,
            "top_driver": top_driver,
            "strong_signals": high_signals,
            "weak_signals": low_signals,
        }
