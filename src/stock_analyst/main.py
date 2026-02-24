"""
Stock Analyst API 서버

FastAPI 기반 메인 애플리케이션 엔트리포인트
"""

from fastapi import FastAPI

from stock_analyst import __version__
from stock_analyst.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Stock Analyst API",
    description="Claude 기반 증권 애널리스트 시스템 - 대안 데이터로 알파를 발굴하는 AI 분석 플랫폼",
    version=__version__,
)


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "name": "Stock Analyst API",
        "version": __version__,
        "environment": settings.environment,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}
