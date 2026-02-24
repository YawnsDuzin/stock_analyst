"""
DART 전자공시 데이터 수집기

금융감독원 DART API를 통해 기업 공시 데이터를 수집합니다.
- 사업보고서, 분기보고서
- 대량보유 보고 (5% 룰)
- 임원 주식 매매 보고
- 정정 공시
"""

import logging

import httpx

from stock_analyst.config import get_settings
from stock_analyst.data_sources.base import BaseCollector

logger = logging.getLogger(__name__)

DART_BASE_URL = "https://opendart.fss.or.kr/api"


class DartCollector(BaseCollector):
    """DART 전자공시 데이터 수집기"""

    def __init__(self):
        settings = get_settings()
        super().__init__(name="DART", api_key=settings.dart_api_key)
        self.base_url = DART_BASE_URL

    async def collect(self, **kwargs) -> list[dict]:
        """DART에서 공시 목록을 수집합니다."""
        corp_code = kwargs.get("corp_code", "")
        bgn_de = kwargs.get("bgn_de", "")  # 시작일 (YYYYMMDD)
        end_de = kwargs.get("end_de", "")  # 종료일 (YYYYMMDD)

        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_count": kwargs.get("page_count", 100),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/list.json",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "000":
            logger.warning(f"DART API 응답 오류: {data.get('message', 'unknown')}")
            return []

        return data.get("list", [])

    def validate(self, data: dict) -> bool:
        """DART 데이터의 유효성을 검증합니다."""
        required_fields = ["corp_code", "corp_name", "report_nm"]
        return all(field in data for field in required_fields)

    async def get_company_info(self, corp_code: str) -> dict:
        """기업 개황을 조회합니다."""
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/company.json",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_major_shareholder_reports(
        self, corp_code: str
    ) -> list[dict]:
        """대량보유 보고 (5% 룰) 변동 내역을 조회합니다."""
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/majorstock.json",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

        return data.get("list", [])
