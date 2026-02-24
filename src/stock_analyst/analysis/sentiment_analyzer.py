"""
감성 분석 모듈

컨퍼런스콜, 사업보고서, 뉴스 텍스트의 감성을 분석합니다.
한국어 금융 텍스트에 특화된 키워드 기반 감성 분석을 제공합니다.
"""


# 긍정 신호 키워드
POSITIVE_SIGNALS = [
    "가시성이 높아지고",
    "수주 파이프라인이 견조",
    "초과 달성",
    "기대 이상",
    "상향 조정",
    "신규 계약 체결",
    "시장 점유율 확대",
    "사상 최대",
    "흑자 전환",
    "성장 가속화",
    "수출 호조",
    "신규 수주",
    "턴어라운드",
]

# 부정 신호 키워드
NEGATIVE_SIGNALS = [
    "불확실성을 모니터링",
    "보수적으로 접근",
    "일회성 비용",
    "시장 환경이 어렵",
    "수요 둔화",
    "재고 조정",
    "가이던스 하향",
    "구조조정",
    "비용 절감 노력",
    "점진적 회복 기대",
    "적자 지속",
    "실적 부진",
    "경쟁 심화",
]

# 회피 신호 키워드 (특히 주의)
EVASION_SIGNALS = [
    "노력하겠습니다",
    "검토 중입니다",
    "구체적인 것은 추후",
    "자세한 것은 나중에",
    "아직 확정되지 않은",
    "말씀드리기 어려운",
]


class SentimentAnalyzer:
    """한국어 금융 텍스트 감성 분석기"""

    def __init__(
        self,
        positive_keywords: list[str] | None = None,
        negative_keywords: list[str] | None = None,
        evasion_keywords: list[str] | None = None,
    ):
        self.positive_keywords = positive_keywords or POSITIVE_SIGNALS
        self.negative_keywords = negative_keywords or NEGATIVE_SIGNALS
        self.evasion_keywords = evasion_keywords or EVASION_SIGNALS

    def analyze(self, text: str) -> dict:
        """
        텍스트의 감성을 분석합니다.

        Args:
            text: 분석할 텍스트

        Returns:
            감성 분석 결과
        """
        positive_matches = self._find_matches(text, self.positive_keywords)
        negative_matches = self._find_matches(text, self.negative_keywords)
        evasion_matches = self._find_matches(text, self.evasion_keywords)

        total_signals = len(positive_matches) + len(negative_matches)
        if total_signals == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (
                len(positive_matches) - len(negative_matches)
            ) / total_signals

        return {
            "sentiment_score": round(sentiment_score, 3),
            "positive_count": len(positive_matches),
            "negative_count": len(negative_matches),
            "evasion_count": len(evasion_matches),
            "positive_matches": positive_matches,
            "negative_matches": negative_matches,
            "evasion_matches": evasion_matches,
            "overall": self._classify(sentiment_score, len(evasion_matches)),
        }

    def compare_texts(self, current: str, previous: str) -> dict:
        """
        두 텍스트의 감성 변화를 비교합니다.

        Args:
            current: 현재 텍스트
            previous: 이전 텍스트

        Returns:
            감성 변화 결과
        """
        current_result = self.analyze(current)
        previous_result = self.analyze(previous)

        delta = current_result["sentiment_score"] - previous_result["sentiment_score"]

        return {
            "current": current_result,
            "previous": previous_result,
            "sentiment_delta": round(delta, 3),
            "direction": (
                "improving" if delta > 0.1
                else "deteriorating" if delta < -0.1
                else "stable"
            ),
        }

    def _find_matches(self, text: str, keywords: list[str]) -> list[str]:
        """텍스트에서 키워드 매칭을 수행합니다."""
        return [kw for kw in keywords if kw in text]

    @staticmethod
    def _classify(score: float, evasion_count: int) -> str:
        """감성 점수와 회피 횟수를 종합하여 분류합니다."""
        if evasion_count >= 3:
            return "EVASIVE"  # 회피적 (경고)
        if score > 0.3:
            return "POSITIVE"
        if score < -0.3:
            return "NEGATIVE"
        return "NEUTRAL"
