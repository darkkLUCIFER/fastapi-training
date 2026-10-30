import logging

from src.core.logging import configure_logging
from src.core.services import SecurityUtils
from src.core.dependencies import get_security_utils


def test_security_dependency_returns_security_utility():
    assert isinstance(get_security_utils(), SecurityUtils)


def test_logging_configuration_sets_expected_defaults(monkeypatch):
    calls = []
    monkeypatch.setattr(logging, 'basicConfig', lambda **kwargs: calls.append(kwargs))

    configure_logging()

    assert calls == [
        {
            'level': logging.INFO,
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        }
    ]
