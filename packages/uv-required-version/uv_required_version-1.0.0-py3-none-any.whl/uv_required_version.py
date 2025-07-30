"""
uv-required-version
"""

import argparse
import logging
import pathlib
import shutil
import subprocess
import sys
from os import getenv
from typing import Sequence

from uv import find_uv_bin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.getLevelName(getenv("LOG_LEVEL", "WARNING").upper()))

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # pragma: no cover

logger = logging.getLogger(__name__)

UV_CONFIG_FILES = [
    "uv.toml",
    "pyproject.toml",
]


def find_config_file() -> pathlib.Path | None:
    """
    Find the first available uv config file by traversing the current directory and its parents.
    """
    config_file = None
    current_path = pathlib.Path.cwd().resolve()
    while current_path != current_path.parent:
        for config_name in UV_CONFIG_FILES:
            file_path = current_path / config_name
            if file_path.exists():
                return file_path
        current_path = current_path.parent
    return config_file


def find_uv_binary() -> pathlib.Path:
    """
    Find the uv binary.

    First, try to find the uv binary in the system PATH.
    If not found, use the uv.find_uv_bin function to locate it.
    """
    uv_binary = shutil.which("uv")
    if not uv_binary:
        uv_binary = find_uv_bin()
    return pathlib.Path(uv_binary)


def get_uv_version(config_file: pathlib.Path) -> str | None:
    """
    Get the UV version from the config file.
    If no version is found, it will return None.
    """
    config_file_content = config_file.read_text(encoding="utf-8")
    config_file_dict = tomllib.loads(config_file_content)
    if config_file.name == "uv.toml":
        version = config_file_dict.get("required-version")
    elif config_file.name == "pyproject.toml":
        version = config_file_dict.get("tool", {}).get("uv", {}).get("required-version")
    else:
        raise ValueError(f"Unsupported config file: {config_file.name}")
    if not version:
        return None
    else:
        version = str(version).strip()
        if version[0].isdigit():
            version = f"=={version}"
        return f"uv{version.strip()}"


def uv_required_version(
    args: Sequence[str], capture_output: bool = False
) -> subprocess.CompletedProcess:
    """
    Run the uv-required-version Workflow.

    1) Find the UV config file in the current directory or its parents.
    2) Get the UV version from the config file.
    3) Find the UV binary in the system PATH or using uv.find_uv_bin.
    4) Construct the CLI command to run UV with the specified version.
    5) Execute the command with the provided arguments.
    """
    config_file = find_config_file()
    logger.debug("<uv-required-version> Config File: %s", config_file)
    uv_version = get_uv_version(config_file=config_file) if config_file else None
    logger.debug("<uv-required-version> UV Version: %s", uv_version)
    uv_binary = find_uv_binary()
    logger.debug("<uv-required-version> UV Binary: %s", uv_binary)
    logger.debug("<uv-required-version> UV Args: %s", args)
    cli_args = list(args)
    if uv_version:
        cli_args = ["tool", "run", uv_version] + cli_args
    cli_args = [str(uv_binary)] + cli_args
    logger.debug("<uv-required-version> Managed CLI: %s", cli_args)
    print(f"\033[1;33muv-required-version: {uv_version}\033[0m", file=sys.stderr)
    result = subprocess.run(args=cli_args, check=False, capture_output=capture_output)
    return result


def cli(capture_output: bool = False) -> subprocess.CompletedProcess:
    """
    uv-required-version
    """
    parser = argparse.ArgumentParser(add_help=False)
    _, args = parser.parse_known_args()
    result = uv_required_version(args=args, capture_output=capture_output)
    sys.exit(result.returncode)
    return result  # noqa


if __name__ == "__main__":  # pragma: no cover
    cli()
