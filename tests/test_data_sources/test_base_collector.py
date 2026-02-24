"""BaseCollector 유닛 테스트"""

import pytest

from stock_analyst.data_sources.base import BaseCollector


class MockCollector(BaseCollector):
    """테스트용 Mock 수집기"""

    def __init__(self, fail_count: int = 0):
        super().__init__(name="MockCollector", api_key="test-key")
        self.fail_count = fail_count
        self._call_count = 0

    async def collect(self, **kwargs) -> list[dict]:
        self._call_count += 1
        if self._call_count <= self.fail_count:
            raise ConnectionError(f"Mock failure #{self._call_count}")
        return [{"id": 1, "data": "test"}]

    def validate(self, data: dict) -> bool:
        return "id" in data and "data" in data


class TestBaseCollector:
    """BaseCollector 기본 기능 테스트"""

    def test_init(self):
        """초기화 확인"""
        collector = MockCollector()
        assert collector.name == "MockCollector"
        assert collector.api_key == "test-key"
        assert collector.last_collected_at is None

    def test_repr(self):
        """문자열 표현 확인"""
        collector = MockCollector()
        assert "MockCollector" in repr(collector)

    @pytest.mark.asyncio
    async def test_collect_success(self):
        """정상 수집 테스트"""
        collector = MockCollector()
        data = await collector.collect()
        assert len(data) == 1
        assert data[0]["id"] == 1

    @pytest.mark.asyncio
    async def test_collect_with_retry_success_first_try(self):
        """첫 시도에 성공하는 재시도 테스트"""
        collector = MockCollector(fail_count=0)
        data = await collector.collect_with_retry(max_retries=3)
        assert len(data) == 1
        assert collector.last_collected_at is not None

    @pytest.mark.asyncio
    async def test_collect_with_retry_success_after_failure(self):
        """실패 후 재시도 성공 테스트"""
        collector = MockCollector(fail_count=2)
        data = await collector.collect_with_retry(max_retries=3)
        assert len(data) == 1
        assert collector._call_count == 3  # 2번 실패 + 1번 성공

    @pytest.mark.asyncio
    async def test_collect_with_retry_all_fail(self):
        """모든 재시도 실패 테스트"""
        collector = MockCollector(fail_count=5)
        with pytest.raises(ConnectionError):
            await collector.collect_with_retry(max_retries=3)

    def test_validate_success(self):
        """유효성 검증 성공 테스트"""
        collector = MockCollector()
        assert collector.validate({"id": 1, "data": "test"}) is True

    def test_validate_failure(self):
        """유효성 검증 실패 테스트"""
        collector = MockCollector()
        assert collector.validate({"name": "test"}) is False
