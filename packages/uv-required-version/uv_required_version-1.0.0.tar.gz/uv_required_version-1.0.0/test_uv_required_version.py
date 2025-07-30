import pathlib
import types
from unittest.mock import MagicMock, patch

import pytest

import uv_required_version


def test_find_config_file_found(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that find_config_file returns the config file when it exists in the current directory.

    Scenario: File is found in current directory.
    """
    config = tmp_path / "uv.toml"
    config.write_text("required-version = '1.2.3'")
    monkeypatch.chdir(tmp_path)
    found = uv_required_version.find_config_file()
    assert found == config


def test_find_config_file_found_in_parent(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that find_config_file finds the config file in a parent directory.

    Scenario: File is found in parent directory.
    """
    parent = tmp_path
    child = tmp_path / "child"
    child.mkdir()
    config = parent / "pyproject.toml"
    config.write_text("[tool.uv]\nrequired-version = '==2.0.0'")
    monkeypatch.chdir(child)
    found = uv_required_version.find_config_file()
    assert found == config


def test_find_config_file_not_found(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that find_config_file returns None if no config file is found.

    Scenario: Config file is not found.
    """
    monkeypatch.chdir(tmp_path)
    assert uv_required_version.find_config_file() is None


def test_find_uv_binary_system_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that find_uv_binary returns the correct path when found in the system PATH.

    Scenario: Found via system PATH.
    """
    monkeypatch.setattr(
        uv_required_version.shutil, "which", lambda _: "/usr/local/bin/uv"
    )
    result = uv_required_version.find_uv_binary()
    assert str(result) == "/usr/local/bin/uv"


def test_find_uv_binary_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that find_uv_binary falls back to find_uv_bin if not found in PATH.

    Scenario: Fallback to find_uv_bin when not found in PATH.
    """
    monkeypatch.setattr(uv_required_version.shutil, "which", lambda _: None)
    monkeypatch.setattr(uv_required_version, "find_uv_bin", lambda: "/another/path/uv")
    result = uv_required_version.find_uv_binary()
    assert str(result) == "/another/path/uv"


@pytest.mark.parametrize(
    "filename,contents,expected",
    [
        ("uv.toml", "required-version = '==1.2.3'", "uv==1.2.3"),
        ("pyproject.toml", "[tool.uv]\nrequired-version = '==2.0.0'", "uv==2.0.0"),
        ("uv.toml", "", None),
        ("pyproject.toml", "[tool.uv]\n", None),
    ],
)
def test_get_uv_version(
    filename: str, contents: str, expected: str | None, tmp_path: pathlib.Path
) -> None:
    """
    Parametrized test for get_uv_version, covering various file contents and expectations.

    Tests get_uv_version with different TOML files and expected results.
    """
    file = tmp_path / filename
    file.write_text(contents)
    result = uv_required_version.get_uv_version(file)
    assert result == expected


def test_get_uv_version_invalid_file(tmp_path: pathlib.Path) -> None:
    """
    Test that get_uv_version raises ValueError for an invalid file.

    Scenario: Invalid file raises ValueError.
    """
    file = tmp_path / "invalid.toml"
    file.write_text("")
    with pytest.raises(ValueError):
        uv_required_version.get_uv_version(file)


@patch("uv_required_version.subprocess.run")
def test_uv_required_version_with_version(
    mock_run: MagicMock, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test uv_required_version when a version is specified in the config file.

    Scenario: With version specified in config.
    """
    config = tmp_path / "uv.toml"
    config.write_text("required-version = '==3.4.5'")
    monkeypatch.setattr(uv_required_version, "find_config_file", lambda: config)
    monkeypatch.setattr(
        uv_required_version, "find_uv_binary", lambda: pathlib.Path("/fake/uv")
    )
    monkeypatch.setattr(
        uv_required_version, "get_uv_version", lambda config_file: "uv==3.4.5"
    )
    mock_result = MagicMock(returncode=0)
    mock_run.return_value = mock_result

    result = uv_required_version.uv_required_version(["foo", "--bar"])
    mock_run.assert_called_once()
    args = mock_run.call_args[1]["args"]
    assert args[:4] == ["/fake/uv", "tool", "run", "uv==3.4.5"]
    assert "foo" in args
    assert result is mock_result


@patch("uv_required_version.subprocess.run")
def test_uv_required_version_no_version(
    mock_run: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test uv_required_version when no version is specified in the config file.

    Scenario: No version specified in config.
    """
    monkeypatch.setattr(uv_required_version, "find_config_file", lambda: None)
    monkeypatch.setattr(
        uv_required_version, "find_uv_binary", lambda: pathlib.Path("/fake/uv")
    )
    mock_result = MagicMock(returncode=0)
    mock_run.return_value = mock_result

    result = uv_required_version.uv_required_version(["foo"])
    mock_run.assert_called_once()
    args = mock_run.call_args[1]["args"]
    assert args[0] == "/fake/uv"
    assert "tool" not in args
    assert result is mock_result


@patch("uv_required_version.uv_required_version")
@patch("sys.exit")
def test_cli(mock_exit: MagicMock, mock_uv_required_version: MagicMock) -> None:
    """
    Test the CLI integration with uv_required_version and click.Context.exit.

    Ensures the CLI exits with the correct return code.
    """
    mock_uv_required_version.return_value.returncode = 42
    from uv_required_version import cli

    with patch("sys.argv", ["foo", "bar"]):
        cli()

    mock_exit.assert_called_once_with(42)


def test_get_uv_version_toml_parsing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that get_uv_version uses TOML parsing logic as expected.

    Scenario: TOML parsing logic is invoked and used.
    """
    file = tmp_path / "uv.toml"
    file.write_text("required-version = '==1.2.3'")
    called: dict[str, str] = {}

    def fake_loads(content: str) -> dict[str, str]:
        called["content"] = content
        return {"required-version": "==1.2.3"}

    monkeypatch.setattr(
        uv_required_version, "tomllib", types.SimpleNamespace(loads=fake_loads)
    )
    result = uv_required_version.get_uv_version(file)
    assert called["content"] == "required-version = '==1.2.3'"
    assert result == "uv==1.2.3"


@patch("sys.exit")
@pytest.mark.parametrize(
    "uv_version",
    [
        "==0.7.18",
        "0.7.18",
        "==0.7.0",
        "==0.6.0",
    ],
)
def test_integration(
    mock_exit: MagicMock,
    uv_version: str,
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """
    Test the integration of all components in uv_required_version.

    This test ensures that find_config_file, get_uv_version, and find_uv_binary work together.
    """
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "uv.toml"
    config.write_text(f'required-version = "{uv_version}"')
    monkeypatch.setattr("sys.argv", ["uv_required_version", "--version"])
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    result = uv_required_version.cli(capture_output=True)
    _, err = capsys.readouterr()
    mock_exit.assert_called_once_with(0)
    uv_version = "==" + uv_version.replace("==", "")
    assert err == f"\x1b[1;33muv-required-version: uv{uv_version}\x1b[0m\n"
    assert result.stdout.decode().startswith(f"uv {uv_version.replace('==', '')}")
    assert result.returncode == 0
