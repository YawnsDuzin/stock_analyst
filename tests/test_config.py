"""설정 모듈 유닛 테스트"""

import os

import pytest

from stock_analyst.config import Settings, get_settings


class TestSettings:
    """Settings 클래스 테스트"""

    def test_default_settings(self):
        """기본 설정값이 올바르게 적용되는지 확인"""
        settings = Settings(
            _env_file=None,  # .env 파일 무시
        )
        assert settings.environment == "development"
        assert settings.log_level == "INFO"
        assert settings.database_url == "sqlite:///./stock_analyst.db"

    def test_is_development(self):
        """개발 환경 판별이 올바른지 확인"""
        settings = Settings(environment="development", _env_file=None)
        assert settings.is_development is True
        assert settings.is_production is False

    def test_is_production(self):
        """프로덕션 환경 판별이 올바른지 확인"""
        settings = Settings(environment="production", _env_file=None)
        assert settings.is_development is False
        assert settings.is_production is True

    def test_default_model_names(self):
        """Claude 모델명 기본값 확인"""
        settings = Settings(_env_file=None)
        assert "sonnet" in settings.claude_model_analysis
        assert "opus" in settings.claude_model_deep
        assert "haiku" in settings.claude_model_quick

    def test_api_keys_default_empty(self):
        """API 키가 기본적으로 빈 문자열인지 확인"""
        settings = Settings(_env_file=None)
        assert settings.anthropic_api_key == ""
        assert settings.dart_api_key == ""
        assert settings.data_go_kr_api_key == ""

    def test_settings_from_env_vars(self, monkeypatch):
        """환경 변수에서 설정을 읽어오는지 확인"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

        settings = Settings(_env_file=None)
        assert settings.environment == "production"
        assert settings.log_level == "DEBUG"
        assert settings.anthropic_api_key == "test-key-123"


class TestGetSettings:
    """get_settings 함수 테스트"""

    def test_returns_settings_instance(self):
        """Settings 인스턴스를 반환하는지 확인"""
        # lru_cache 초기화
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_singleton_pattern(self):
        """동일 인스턴스를 반환하는지 확인 (캐싱)"""
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
