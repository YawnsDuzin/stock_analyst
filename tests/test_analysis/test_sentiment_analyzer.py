"""감성 분석 모듈 유닛 테스트"""

import pytest

from stock_analyst.analysis.sentiment_analyzer import (
    SentimentAnalyzer,
    POSITIVE_SIGNALS,
    NEGATIVE_SIGNALS,
    EVASION_SIGNALS,
)


class TestSentimentAnalyzer:
    """SentimentAnalyzer 기본 기능 테스트"""

    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_positive_text(self):
        """긍정적 텍스트 분석"""
        text = "올해 실적이 기대 이상으로 사상 최대를 기록했으며 시장 점유율 확대가 가시적입니다."
        result = self.analyzer.analyze(text)
        assert result["positive_count"] >= 2
        assert result["sentiment_score"] > 0
        assert result["overall"] == "POSITIVE"

    def test_negative_text(self):
        """부정적 텍스트 분석"""
        text = "시장 환경이 어렵고 수요 둔화로 인해 가이던스 하향 조정이 불가피합니다. 재고 조정이 필요합니다."
        result = self.analyzer.analyze(text)
        assert result["negative_count"] >= 2
        assert result["sentiment_score"] < 0
        assert result["overall"] == "NEGATIVE"

    def test_neutral_text(self):
        """중립적 텍스트 분석"""
        text = "오늘 날씨가 좋습니다. 점심은 김치찌개를 먹었습니다."
        result = self.analyzer.analyze(text)
        assert result["positive_count"] == 0
        assert result["negative_count"] == 0
        assert result["sentiment_score"] == 0.0
        assert result["overall"] == "NEUTRAL"

    def test_evasive_text(self):
        """회피적 텍스트 감지"""
        text = (
            "그 부분은 노력하겠습니다. "
            "구체적인 것은 추후 말씀드리겠습니다. "
            "아직 확정되지 않은 사항이라 검토 중입니다."
        )
        result = self.analyzer.analyze(text)
        assert result["evasion_count"] >= 3
        assert result["overall"] == "EVASIVE"

    def test_mixed_signals(self):
        """긍정/부정 혼합 텍스트"""
        text = "신규 계약 체결로 성장하고 있지만 시장 환경이 어렵습니다."
        result = self.analyzer.analyze(text)
        assert result["positive_count"] >= 1
        assert result["negative_count"] >= 1

    def test_empty_text(self):
        """빈 텍스트 처리"""
        result = self.analyzer.analyze("")
        assert result["positive_count"] == 0
        assert result["negative_count"] == 0
        assert result["sentiment_score"] == 0.0
        assert result["overall"] == "NEUTRAL"

    def test_result_structure(self):
        """결과 구조 확인"""
        result = self.analyzer.analyze("테스트")
        assert "sentiment_score" in result
        assert "positive_count" in result
        assert "negative_count" in result
        assert "evasion_count" in result
        assert "positive_matches" in result
        assert "negative_matches" in result
        assert "evasion_matches" in result
        assert "overall" in result


class TestSentimentComparison:
    """텍스트 비교 분석 테스트"""

    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_improving_sentiment(self):
        """감성 개선 감지"""
        previous = "시장 환경이 어렵고 수요 둔화가 우려됩니다."
        current = "신규 계약 체결로 성장 가속화되고 있으며 시장 점유율 확대가 가시적입니다."
        result = self.analyzer.compare_texts(current, previous)
        assert result["sentiment_delta"] > 0
        assert result["direction"] == "improving"

    def test_deteriorating_sentiment(self):
        """감성 악화 감지"""
        previous = "신규 계약 체결로 기대 이상의 성과를 달성했습니다."
        current = "시장 환경이 어렵고 수요 둔화로 재고 조정이 필요합니다."
        result = self.analyzer.compare_texts(current, previous)
        assert result["sentiment_delta"] < 0
        assert result["direction"] == "deteriorating"

    def test_stable_sentiment(self):
        """감성 안정 유지"""
        text = "일반적인 내용의 텍스트입니다."
        result = self.analyzer.compare_texts(text, text)
        assert result["sentiment_delta"] == 0
        assert result["direction"] == "stable"

    def test_comparison_structure(self):
        """비교 결과 구조 확인"""
        result = self.analyzer.compare_texts("현재", "이전")
        assert "current" in result
        assert "previous" in result
        assert "sentiment_delta" in result
        assert "direction" in result


class TestCustomKeywords:
    """사용자 정의 키워드 테스트"""

    def test_custom_positive_keywords(self):
        """사용자 정의 긍정 키워드"""
        analyzer = SentimentAnalyzer(
            positive_keywords=["좋다", "훌륭"],
            negative_keywords=["나쁘다"],
        )
        result = analyzer.analyze("실적이 좋다고 평가됩니다.")
        assert result["positive_count"] == 1

    def test_default_keywords_loaded(self):
        """기본 키워드가 로드되는지 확인"""
        analyzer = SentimentAnalyzer()
        assert len(analyzer.positive_keywords) == len(POSITIVE_SIGNALS)
        assert len(analyzer.negative_keywords) == len(NEGATIVE_SIGNALS)
        assert len(analyzer.evasion_keywords) == len(EVASION_SIGNALS)
