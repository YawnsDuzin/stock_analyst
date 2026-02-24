"""나라장터 수집기 유닛 테스트"""

import pytest

from stock_analyst.data_sources.procurement_collector import ProcurementCollector


class TestProcurementCollector:
    """ProcurementCollector 테스트"""

    def test_init(self):
        """초기화 확인"""
        collector = ProcurementCollector()
        assert collector.name == "나라장터"

    def test_validate_success(self):
        """유효한 낙찰 데이터 검증"""
        collector = ProcurementCollector()
        data = {
            "bidNtceNm": "테스트 계약",
            "sucsfbidAmt": 1000000000,
        }
        assert collector.validate(data) is True

    def test_validate_failure_missing_field(self):
        """필수 필드 누락 시 검증 실패"""
        collector = ProcurementCollector()
        data = {"bidNtceNm": "테스트 계약"}
        assert collector.validate(data) is False

    def test_validate_failure_empty(self):
        """빈 데이터 검증 실패"""
        collector = ProcurementCollector()
        assert collector.validate({}) is False


class TestProcurementSignificance:
    """계약 중요도 평가 테스트"""

    def setup_method(self):
        self.collector = ProcurementCollector()

    def test_very_high_significance(self):
        """시총 대비 15% 이상 = VERY_HIGH"""
        result = self.collector.calculate_significance(
            contract_amount=15_000_000_000,  # 150억
            market_cap=100_000_000_000,      # 1000억
        )
        assert result["significance"] == "VERY_HIGH"
        assert result["ratio"] == 0.15

    def test_high_significance(self):
        """시총 대비 10% = HIGH"""
        result = self.collector.calculate_significance(
            contract_amount=10_000_000_000,
            market_cap=100_000_000_000,
        )
        assert result["significance"] == "HIGH"

    def test_medium_significance(self):
        """시총 대비 5% = MEDIUM"""
        result = self.collector.calculate_significance(
            contract_amount=5_000_000_000,
            market_cap=100_000_000_000,
        )
        assert result["significance"] == "MEDIUM"

    def test_low_significance(self):
        """시총 대비 2% = LOW"""
        result = self.collector.calculate_significance(
            contract_amount=2_000_000_000,
            market_cap=100_000_000_000,
        )
        assert result["significance"] == "LOW"

    def test_minimal_significance(self):
        """시총 대비 1% = MINIMAL"""
        result = self.collector.calculate_significance(
            contract_amount=1_000_000_000,
            market_cap=100_000_000_000,
        )
        assert result["significance"] == "MINIMAL"

    def test_zero_market_cap(self):
        """시가총액 0일 때 N/A 처리"""
        result = self.collector.calculate_significance(
            contract_amount=1_000_000_000,
            market_cap=0,
        )
        assert result["significance"] == "N/A"
        assert result["ratio"] == 0

    def test_negative_market_cap(self):
        """음수 시가총액 방어"""
        result = self.collector.calculate_significance(
            contract_amount=1_000_000_000,
            market_cap=-100,
        )
        assert result["significance"] == "N/A"
