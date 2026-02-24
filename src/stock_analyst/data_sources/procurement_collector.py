"""
나라장터 (조달청) 낙찰 데이터 수집기

공공데이터포털 API를 통해 나라장터 낙찰 결과를 수집합니다.
대형 계약 낙찰은 IR 공시보다 평균 2~4주 먼저 확인할 수 있는 선행 지표입니다.
"""

import logging
from datetime import datetime, timedelta

import httpx

from stock_analyst.config import get_settings
from stock_analyst.data_sources.base import BaseCollector

logger = logging.getLogger(__name__)

PROCUREMENT_API_URL = (
    "https://apis.data.go.kr/1230000/ScsbidInfoService"
    "/getOpengResultListInfoServcPPSSrch"
)


class ProcurementCollector(BaseCollector):
    """나라장터 낙찰 데이터 수집기"""

    def __init__(self):
        settings = get_settings()
        super().__init__(name="나라장터", api_key=settings.data_go_kr_api_key)

    async def collect(self, **kwargs) -> list[dict]:
        """나라장터에서 낙찰 결과를 수집합니다."""
        company_name = kwargs.get("company_name", "")
        days_back = kwargs.get("days_back", 30)

        date_to = datetime.now().strftime("%Y%m%d")
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

        params = {
            "ServiceKey": self.api_key,
            "numOfRows": kwargs.get("num_of_rows", 100),
            "pageNo": kwargs.get("page_no", 1),
            "inqryDiv": 1,
            "type": "json",
            "inqryBgnDt": date_from,
            "inqryEndDt": date_to,
        }

        if company_name:
            params["bidNtceNm"] = company_name

        async with httpx.AsyncClient() as client:
            response = await client.get(
                PROCUREMENT_API_URL,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

        # 응답 구조에서 결과 리스트 추출
        items = (
            data.get("response", {})
            .get("body", {})
            .get("items", [])
        )

        if isinstance(items, dict):
            items = items.get("item", [])

        if isinstance(items, dict):
            items = [items]

        return items

    def validate(self, data: dict) -> bool:
        """낙찰 데이터의 유효성을 검증합니다."""
        required_fields = ["bidNtceNm", "sucsfbidAmt"]
        return all(field in data for field in required_fields)

    def calculate_significance(
        self, contract_amount: int, market_cap: int
    ) -> dict:
        """
        계약금액의 중요도를 평가합니다.

        Args:
            contract_amount: 계약 금액 (원)
            market_cap: 시가총액 (원)

        Returns:
            중요도 평가 결과
        """
        if market_cap <= 0:
            return {"ratio": 0, "significance": "N/A"}

        ratio = contract_amount / market_cap

        if ratio >= 0.15:
            significance = "VERY_HIGH"
        elif ratio >= 0.10:
            significance = "HIGH"
        elif ratio >= 0.05:
            significance = "MEDIUM"
        elif ratio >= 0.02:
            significance = "LOW"
        else:
            significance = "MINIMAL"

        return {
            "ratio": round(ratio, 4),
            "significance": significance,
            "contract_amount": contract_amount,
            "market_cap": market_cap,
        }
