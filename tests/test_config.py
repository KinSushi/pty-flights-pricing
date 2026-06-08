import pytest

from src.config import load_config


def test_load_config_reads_required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapidapi-key")
    monkeypatch.setenv("GMAIL_USER", "sender@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "test-password")
    monkeypatch.setenv("EMAIL_TO", "recipient@example.com")

    config = load_config(dry_run=True)

    assert config.rapidapi_key == "test-rapidapi-key"
    assert config.gmail_user == "sender@example.com"
    assert config.email_to == "recipient@example.com"
    assert config.dry_run is True


def test_load_config_fails_when_required_env_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.setenv("GMAIL_USER", "sender@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "test-password")
    monkeypatch.setenv("EMAIL_TO", "recipient@example.com")

    with pytest.raises(RuntimeError, match="RAPIDAPI_KEY"):
        load_config()
