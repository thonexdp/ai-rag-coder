from app.core.config import get_settings
from app.services.llm_service import OllamaLLMService, OpenAILLMService, get_llm_service


def _reset_settings_cache():
    get_settings.cache_clear()


def test_llm_provider_ollama(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    _reset_settings_cache()

    service = get_llm_service()

    assert isinstance(service, OllamaLLMService)


def test_llm_provider_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    _reset_settings_cache()

    service = get_llm_service()

    assert isinstance(service, OpenAILLMService)


def test_llm_provider_openai_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    _reset_settings_cache()

    try:
        get_llm_service()
    except ValueError as exc:
        assert str(exc) == "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
    else:  # pragma: no cover - defensive branch
        raise AssertionError("Expected missing OPENAI_API_KEY to raise ValueError")


def test_llm_provider_openai_requires_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    _reset_settings_cache()

    try:
        get_llm_service()
    except ValueError as exc:
        assert str(exc) == "OPENAI_MODEL is required when LLM_PROVIDER=openai"
    else:  # pragma: no cover - defensive branch
        raise AssertionError("Expected missing OPENAI_MODEL to raise ValueError")
