from pathlib import Path

import pytest
from pydantic import ValidationError

from taskflow.config import DEFAULT_DATABASE_URL, Settings

CUSTOM_DATABASE_URL = (
    "postgresql+psycopg://taskflow:secret@db:5432/taskflow_test"
)
ENVIRONMENT_DATABASE_URL = (
    "postgresql+psycopg://taskflow:env@localhost:5432/taskflow_env"
)


def test_settings_use_local_default_without_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    loaded_settings = Settings()

    assert loaded_settings.database_url == DEFAULT_DATABASE_URL


def test_settings_read_database_url_from_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        f"DATABASE_URL={CUSTOM_DATABASE_URL}\n",
        encoding="utf-8",
    )

    loaded_settings = Settings()

    assert loaded_settings.database_url == CUSTOM_DATABASE_URL


def test_environment_variable_overrides_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        f"DATABASE_URL={CUSTOM_DATABASE_URL}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DATABASE_URL", ENVIRONMENT_DATABASE_URL)

    loaded_settings = Settings()

    assert loaded_settings.database_url == ENVIRONMENT_DATABASE_URL


@pytest.mark.parametrize("blank_value", ["", "   ", "\t\n"])
def test_blank_database_url_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    blank_value: str,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", blank_value)

    with pytest.raises(ValidationError):
        Settings()


def test_unrelated_dotenv_keys_are_ignored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        f"DATABASE_URL={CUSTOM_DATABASE_URL}\n"
        "UNRELATED_SETTING=ignored\n",
        encoding="utf-8",
    )

    loaded_settings = Settings()

    assert loaded_settings.database_url == CUSTOM_DATABASE_URL


def test_env_example_matches_default_database_url() -> None:
    env_example = Path(__file__).resolve().parents[1] / ".env.example"

    assert (
        env_example.read_text(encoding="utf-8").strip()
        == f"DATABASE_URL={DEFAULT_DATABASE_URL}"
    )
