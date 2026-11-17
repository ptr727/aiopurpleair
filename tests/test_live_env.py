"""Test the live-test credentials loader without the live API."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests import test_live_api


@pytest.fixture(autouse=True)
def _isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point each test's own ``_load_env()`` call at an empty temporary home.

    This isolates the calls these tests make, not the live module's import. With
    ``AIOPURPLEAIR_LIVE_TESTS=1`` set, importing ``test_live_api`` loads the real
    credentials file at collection, since that flag is the opt-in to use it.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(test_live_api.Path, "home", lambda: home)
    return home


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _host_file(home: Path) -> Path:
    return home / ".secrets" / "aiopurpleair_live_test.env"


def test_load_env_named_file_loads_dotenv_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A named file's values load literally, with quotes, export, and comments handled."""
    env_file = _write(
        tmp_path / "creds.env",
        '# comment\nPURPLEAIR_API_KEY="file-key"\nexport PURPLEAIR_SENSOR_INDEX_1=12345 # trailing\n'
        "PURPLEAIR_OWNER_EMAIL=a${HOME}b\nNOVALUE\n",
    )
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(env_file))
    monkeypatch.delenv("PURPLEAIR_API_KEY", raising=False)
    monkeypatch.delenv("PURPLEAIR_SENSOR_INDEX_1", raising=False)
    monkeypatch.delenv("PURPLEAIR_OWNER_EMAIL", raising=False)
    monkeypatch.delenv("NOVALUE", raising=False)

    values = test_live_api._load_env()

    assert values["PURPLEAIR_API_KEY"] == "file-key"
    assert values["PURPLEAIR_SENSOR_INDEX_1"] == "12345"
    assert values["PURPLEAIR_OWNER_EMAIL"] == "a${HOME}b"
    assert "NOVALUE" not in values


def test_load_env_environment_overrides_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A variable already in the environment wins over the file's value."""
    env_file = _write(tmp_path / "creds.env", "PURPLEAIR_API_KEY=file-key\n")
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(env_file))
    monkeypatch.setenv("PURPLEAIR_API_KEY", "env-key")

    assert test_live_api._load_env()["PURPLEAIR_API_KEY"] == "env-key"


def test_load_env_missing_named_path_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A path named in AIOPURPLEAIR_TEST_ENV that does not exist is refused."""
    missing = tmp_path / "missing.env"
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(missing))

    with pytest.raises(RuntimeError, match=rf"names {re.escape(str(missing))}, which does not exist: fix or unset it"):
        test_live_api._load_env()


def test_load_env_unreadable_file_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A credentials path that cannot be read as a file is refused."""
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(tmp_path))

    with pytest.raises(
        RuntimeError, match=rf"cannot read credentials file {re.escape(str(tmp_path))}: .+: fix it, then re-run"
    ):
        test_live_api._load_env()


def test_load_env_non_utf8_file_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A credentials file that is not valid UTF-8 is refused like an unreadable one."""
    env_file = tmp_path / "creds.env"
    env_file.write_bytes(b"PURPLEAIR_API_KEY=\xff\n")
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(env_file))

    with pytest.raises(
        RuntimeError,
        match=rf"cannot read credentials file {re.escape(str(env_file))}: not valid UTF-8 \(.+\): fix it, then re-run",
    ):
        test_live_api._load_env()


def test_load_env_default_reads_repository_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With no named path, the repository-root file loads from any working directory."""
    _write(tmp_path / ".env.test", "PURPLEAIR_API_KEY=root-key\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.setattr(test_live_api, "__file__", str(tmp_path / "tests" / "test_live_api.py"))
    monkeypatch.delenv("AIOPURPLEAIR_TEST_ENV", raising=False)
    monkeypatch.delenv("PURPLEAIR_API_KEY", raising=False)
    monkeypatch.chdir(elsewhere)

    assert test_live_api._load_env()["PURPLEAIR_API_KEY"] == "root-key"


def test_load_env_missing_default_means_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With no named path, no repository-root file, and no host file, only the environment loads."""
    monkeypatch.setattr(test_live_api, "__file__", str(tmp_path / "tests" / "test_live_api.py"))
    monkeypatch.delenv("AIOPURPLEAIR_TEST_ENV", raising=False)
    monkeypatch.setenv("PURPLEAIR_API_KEY", "env-key")

    assert test_live_api._load_env()["PURPLEAIR_API_KEY"] == "env-key"


def test_load_env_falls_back_to_host_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _isolated_home: Path
) -> None:
    """With no named path and no repository-root file, the host ~/.secrets file loads."""
    _write(_host_file(_isolated_home), "PURPLEAIR_API_KEY=host-key\n")
    monkeypatch.setattr(test_live_api, "__file__", str(tmp_path / "tests" / "test_live_api.py"))
    monkeypatch.delenv("AIOPURPLEAIR_TEST_ENV", raising=False)
    monkeypatch.delenv("PURPLEAIR_API_KEY", raising=False)

    assert test_live_api._load_env()["PURPLEAIR_API_KEY"] == "host-key"


def test_load_env_repository_root_wins_over_host_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _isolated_home: Path
) -> None:
    """A repository-root file is used, and the host file is not merged into it."""
    _write(tmp_path / ".env.test", "PURPLEAIR_API_KEY=root-key\n")
    _write(_host_file(_isolated_home), "PURPLEAIR_API_KEY=host-key\nPURPLEAIR_API_KEY_2=host-key-2\n")
    monkeypatch.setattr(test_live_api, "__file__", str(tmp_path / "tests" / "test_live_api.py"))
    monkeypatch.delenv("AIOPURPLEAIR_TEST_ENV", raising=False)
    monkeypatch.delenv("PURPLEAIR_API_KEY", raising=False)
    monkeypatch.delenv("PURPLEAIR_API_KEY_2", raising=False)

    values = test_live_api._load_env()

    assert values["PURPLEAIR_API_KEY"] == "root-key"
    assert "PURPLEAIR_API_KEY_2" not in values


def test_load_env_named_path_skips_host_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _isolated_home: Path
) -> None:
    """A path named in AIOPURPLEAIR_TEST_ENV is the only file read."""
    env_file = _write(tmp_path / "creds.env", "PURPLEAIR_API_KEY=named-key\n")
    _write(_host_file(_isolated_home), "PURPLEAIR_API_KEY=host-key\nPURPLEAIR_API_KEY_2=host-key-2\n")
    monkeypatch.setenv("AIOPURPLEAIR_TEST_ENV", str(env_file))
    monkeypatch.delenv("PURPLEAIR_API_KEY", raising=False)
    monkeypatch.delenv("PURPLEAIR_API_KEY_2", raising=False)

    values = test_live_api._load_env()

    assert values["PURPLEAIR_API_KEY"] == "named-key"
    assert "PURPLEAIR_API_KEY_2" not in values


def test_load_env_unreadable_host_file_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _isolated_home: Path
) -> None:
    """A host fallback path that cannot be read as a file is refused with its path."""
    host = _host_file(_isolated_home)
    host.mkdir(parents=True)
    monkeypatch.setattr(test_live_api, "__file__", str(tmp_path / "tests" / "test_live_api.py"))
    monkeypatch.delenv("AIOPURPLEAIR_TEST_ENV", raising=False)

    with pytest.raises(
        RuntimeError, match=rf"cannot read credentials file {re.escape(str(host))}: .+: fix it, then re-run"
    ):
        test_live_api._load_env()
