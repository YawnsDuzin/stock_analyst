"""AlphaScorer 유닛 테스트"""

import pytest

from stock_analyst.scoring.alpha_scorer import AlphaScorer, SignalScore


class TestSignalScore:
    """SignalScore 데이터 클래스 테스트"""

    def test_basic_creation(self):
        """기본 생성 확인"""
        score = SignalScore(
            source="test",
            raw_value=0.85,
            normalized=85.0,
            confidence=0.9,
        )
        assert score.source == "test"
        assert score.normalized == 85.0
        assert score.confidence == 0.9

    def test_normalized_clamped(self):
        """정규화 값이 0~100으로 클램핑되는지 확인"""
        score_high = SignalScore(
            source="test", raw_value=1.5, normalized=150.0, confidence=1.0,
        )
        assert score_high.normalized == 100.0

        score_low = SignalScore(
            source="test", raw_value=-0.5, normalized=-50.0, confidence=1.0,
        )
        assert score_low.normalized == 0.0

    def test_confidence_clamped(self):
        """신뢰도가 0~1로 클램핑되는지 확인"""
        score = SignalScore(
            source="test", raw_value=0.5, normalized=50.0, confidence=1.5,
        )
        assert score.confidence == 1.0

        score2 = SignalScore(
            source="test", raw_value=0.5, normalized=50.0, confidence=-0.5,
        )
        assert score2.confidence == 0.0


class TestAlphaScorer:
    """AlphaScorer 핵심 기능 테스트"""

    def test_default_weights(self):
        """기본 가중치 합이 1.0인지 확인"""
        scorer = AlphaScorer()
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 0.01

    def test_custom_weights_normalization(self):
        """사용자 지정 가중치가 자동 정규화되는지 확인"""
        custom_weights = {
            "government_contract": 2.0,
            "hiring_signal": 2.0,
            "language_change": 2.0,
            "alternative_data": 2.0,
            "sentiment_extreme": 1.0,
            "supply_chain": 1.0,
        }
        scorer = AlphaScorer(weights=custom_weights)
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 0.01

    def test_calculate_score_all_high(self):
        """모든 신호가 높을 때 STRONG_BUY"""
        scorer = AlphaScorer()
        scores = {
            "government_contract": 90,
            "hiring_signal": 85,
            "language_change": 80,
            "alternative_data": 85,
            "sentiment_extreme": 90,
            "supply_chain": 80,
        }
        result = scorer.calculate_score(scores)
        assert result["total_score"] >= 80
        assert result["signal"] == "STRONG_BUY"

    def test_calculate_score_all_low(self):
        """모든 신호가 낮을 때 STRONG_SELL"""
        scorer = AlphaScorer()
        scores = {
            "government_contract": 10,
            "hiring_signal": 15,
            "language_change": 20,
            "alternative_data": 10,
            "sentiment_extreme": 15,
            "supply_chain": 10,
        }
        result = scorer.calculate_score(scores)
        assert result["total_score"] < 25
        assert result["signal"] == "STRONG_SELL"

    def test_calculate_score_mixed(self):
        """혼합 신호일 때 HOLD"""
        scorer = AlphaScorer()
        scores = {
            "government_contract": 50,
            "hiring_signal": 50,
            "language_change": 50,
            "alternative_data": 50,
            "sentiment_extreme": 50,
            "supply_chain": 50,
        }
        result = scorer.calculate_score(scores)
        assert result["total_score"] == 50.0
        assert result["signal"] == "HOLD"

    def test_missing_signals_default_to_neutral(self):
        """누락된 신호가 50 (중립)으로 처리되는지 확인"""
        scorer = AlphaScorer()
        scores = {
            "government_contract": 90,
            # 나머지 신호 누락
        }
        result = scorer.calculate_score(scores)
        # government_contract만 90, 나머지는 50
        # 0.25 * 90 + 0.75 * 50 = 22.5 + 37.5 = 60.0
        assert result["total_score"] == 60.0

    def test_score_clamping(self):
        """입력 점수가 0~100 범위로 클램핑되는지 확인"""
        scorer = AlphaScorer()
        scores = {
            "government_contract": 150,  # 100으로 클램핑
            "hiring_signal": -10,        # 0으로 클램핑
        }
        result = scorer.calculate_score(scores)
        assert result["breakdown"]["government_contract"] == 100.0
        assert result["breakdown"]["hiring_signal"] == 0.0

    def test_result_has_required_fields(self):
        """결과에 필수 필드가 포함되는지 확인"""
        scorer = AlphaScorer()
        result = scorer.calculate_score({})
        assert "total_score" in result
        assert "breakdown" in result
        assert "signal" in result
        assert "weights_used" in result
        assert "timestamp" in result


class TestInterpretScore:
    """점수 해석 테스트"""

    def setup_method(self):
        self.scorer = AlphaScorer()

    def test_strong_buy(self):
        assert self.scorer.interpret_score(95) == "STRONG_BUY"
        assert self.scorer.interpret_score(80) == "STRONG_BUY"

    def test_buy(self):
        assert self.scorer.interpret_score(79) == "BUY"
        assert self.scorer.interpret_score(65) == "BUY"

    def test_hold(self):
        assert self.scorer.interpret_score(64) == "HOLD"
        assert self.scorer.interpret_score(40) == "HOLD"

    def test_sell(self):
        assert self.scorer.interpret_score(39) == "SELL"
        assert self.scorer.interpret_score(25) == "SELL"

    def test_strong_sell(self):
        assert self.scorer.interpret_score(24) == "STRONG_SELL"
        assert self.scorer.interpret_score(0) == "STRONG_SELL"


class TestWeightedScore:
    """신뢰도 보정 가중 평균 테스트"""

    def test_full_confidence(self):
        """신뢰도 1.0일 때 일반 가중 평균과 동일"""
        scorer = AlphaScorer()
        signals = {
            "government_contract": SignalScore(
                source="test", raw_value=0.9, normalized=90, confidence=1.0,
            ),
            "hiring_signal": SignalScore(
                source="test", raw_value=0.9, normalized=90, confidence=1.0,
            ),
        }
        score = scorer.calculate_weighted_score(signals)
        assert score == 90.0

    def test_low_confidence_reduces_weight(self):
        """신뢰도가 낮으면 해당 신호의 가중치가 줄어드는지 확인"""
        scorer = AlphaScorer()
        signals_high_conf = {
            "government_contract": SignalScore(
                source="test", raw_value=0.9, normalized=90, confidence=1.0,
            ),
            "hiring_signal": SignalScore(
                source="test", raw_value=0.1, normalized=10, confidence=1.0,
            ),
        }
        signals_low_conf = {
            "government_contract": SignalScore(
                source="test", raw_value=0.9, normalized=90, confidence=1.0,
            ),
            "hiring_signal": SignalScore(
                source="test", raw_value=0.1, normalized=10, confidence=0.1,
            ),
        }
        score_high = scorer.calculate_weighted_score(signals_high_conf)
        score_low = scorer.calculate_weighted_score(signals_low_conf)

        # 낮은 신뢰도의 부정적 신호는 영향이 줄어들어야 함
        assert score_low > score_high

    def test_no_matching_weights(self):
        """가중치에 없는 키만 있을 때 중립(50) 반환"""
        scorer = AlphaScorer()
        signals = {
            "unknown_signal": SignalScore(
                source="test", raw_value=0.9, normalized=90, confidence=1.0,
            ),
        }
        score = scorer.calculate_weighted_score(signals)
        assert score == 50.0


class TestDetailedInterpretation:
    """상세 해석 테스트"""

    def test_consistent_high_signals(self):
        """일관되게 높은 신호"""
        scorer = AlphaScorer()
        result = scorer.calculate_score({
            "government_contract": 80,
            "hiring_signal": 75,
            "language_change": 85,
            "alternative_data": 70,
            "sentiment_extreme": 50,
            "supply_chain": 50,
        })
        interpretation = scorer.get_detailed_interpretation(result)
        assert len(interpretation["strong_signals"]) >= 3

    def test_top_driver_identification(self):
        """핵심 드라이버가 올바르게 식별되는지"""
        scorer = AlphaScorer()
        result = scorer.calculate_score({
            "government_contract": 95,  # 가장 극단적
            "hiring_signal": 50,
            "language_change": 50,
            "alternative_data": 50,
            "sentiment_extreme": 50,
            "supply_chain": 50,
        })
        interpretation = scorer.get_detailed_interpretation(result)
        assert interpretation["top_driver"] == "government_contract"
