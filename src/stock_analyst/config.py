"""
설정 관리 모듈

환경 변수와 Pydantic Settings를 사용하여 애플리케이션 설정을 관리합니다.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 환경
    environment: str = "development"
    log_level: str = "INFO"

    # Claude API
    anthropic_api_key: str = ""

    # DART API
    dart_api_key: str = ""

    # 공공데이터포털 API
    data_go_kr_api_key: str = ""

    # 텔레그램
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # 데이터베이스
    database_url: str = "sqlite:///./stock_analyst.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Claude 모델 선택
    claude_model_analysis: str = "claude-sonnet-4-20250514"
    claude_model_deep: str = "claude-opus-4-20250514"
    claude_model_quick: str = "claude-haiku-4-20250514"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """싱글톤 Settings 인스턴스를 반환합니다."""
    return Settings()
