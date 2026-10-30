from src.core.config import Settings
from src.core.choices import ChoiceEnum
from src.auth.constants import RoleChoices


def test_choice_enum_keeps_value_and_human_readable_label():
    class ExampleChoice(ChoiceEnum):
        READY = 'ready', 'Ready to use'

    assert ExampleChoice.READY.value == 'ready'
    assert ExampleChoice.READY.label == 'Ready to use'
    assert RoleChoices.ADMIN.value == 'admin'


def test_settings_accepts_explicit_test_configuration():
    settings = Settings(
        database_url='postgresql://user:pass@localhost/test',
        debug=False,
        cors_origins=['https://example.test'],
        jwt_secret_key='test-secret',
    )

    assert settings.database_url.startswith('postgresql://')
    assert settings.cors_origins == ['https://example.test']
    assert settings.jwt_algorithm == 'HS256'


def test_settings_warns_when_sqlite_is_selected(capsys):
    Settings(
        database_url='sqlite:///./test.db',
        debug=True,
        cors_origins=[],
        jwt_secret_key='test-secret',
    )

    assert 'Using SQLite' in capsys.readouterr().out
