import pytest

from temporal.config import (
    DEFAULT_ADDRESS,
    DEFAULT_NAMESPACE,
    DEFAULT_TASK_QUEUE,
    TemporalConfig,
)


def test_from_env_defaults(monkeypatch):
    for var in (
        "TEMPORAL_ADDRESS",
        "TEMPORAL_NAMESPACE",
        "TEMPORAL_TASK_QUEUE",
        "TEMPORAL_TLS_CERT_PATH",
        "TEMPORAL_TLS_KEY_PATH",
    ):
        monkeypatch.delenv(var, raising=False)

    config = TemporalConfig.from_env()
    assert config.address == DEFAULT_ADDRESS
    assert config.namespace == DEFAULT_NAMESPACE
    assert config.task_queue == DEFAULT_TASK_QUEUE
    assert config.tls_cert_path is None
    assert config.tls_key_path is None
    assert config.tls_enabled is False


def test_from_env_overrides(monkeypatch):
    monkeypatch.setenv("TEMPORAL_ADDRESS", "temporal.prod:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "denjamin-prod")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "denjamin-prod-main")
    monkeypatch.setenv("TEMPORAL_TLS_CERT_PATH", "/certs/client.pem")
    monkeypatch.setenv("TEMPORAL_TLS_KEY_PATH", "/certs/client.key")

    config = TemporalConfig.from_env()
    assert config.address == "temporal.prod:7233"
    assert config.namespace == "denjamin-prod"
    assert config.task_queue == "denjamin-prod-main"
    assert config.tls_cert_path == "/certs/client.pem"
    assert config.tls_key_path == "/certs/client.key"
    assert config.tls_enabled is True


def test_tls_enabled_requires_both_paths(monkeypatch):
    monkeypatch.setenv("TEMPORAL_TLS_CERT_PATH", "/certs/client.pem")
    monkeypatch.delenv("TEMPORAL_TLS_KEY_PATH", raising=False)
    assert TemporalConfig.from_env().tls_enabled is False
