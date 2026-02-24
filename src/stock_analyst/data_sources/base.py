"""
데이터 수집기 기본 클래스

모든 데이터 수집기가 상속해야 하는 기본 인터페이스를 정의합니다.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """모든 데이터 수집기의 기본 클래스"""

    def __init__(self, name: str, api_key: str | None = None):
        self.name = name
        self.api_key = api_key
        self.last_collected_at: datetime | None = None

    @abstractmethod
    async def collect(self, **kwargs) -> list[dict]:
        """데이터를 수집합니다."""
        pass

    @abstractmethod
    def validate(self, data: dict) -> bool:
        """수집된 데이터의 유효성을 검증합니다."""
        pass

    async def collect_with_retry(
        self, max_retries: int = 3, **kwargs
    ) -> list[dict]:
        """재시도 로직이 포함된 수집"""
        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                data = await self.collect(**kwargs)
                self.last_collected_at = datetime.now()
                logger.info(
                    f"[{self.name}] 수집 성공: {len(data)}건 (시도 {attempt + 1})"
                )
                return data
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[{self.name}] 수집 실패 (시도 {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 지수 백오프: 1, 2, 4초
                    await asyncio.sleep(wait_time)

        logger.error(f"[{self.name}] 최대 재시도 횟수 초과")
        raise last_error  # type: ignore[misc]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
