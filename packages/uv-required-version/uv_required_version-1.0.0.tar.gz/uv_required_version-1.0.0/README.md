# uv-required-version

<p>
  <a href="https://github.com/juftin/uv-required-version"><img src="https://img.shields.io/pypi/v/uv-required-version?color=blue&label=%E2%9A%A1%20uv-required-version" alt="PyPI"></a>
  <a href="https://pypi.python.org/pypi/uv-required-version/"><img src="https://img.shields.io/pypi/pyversions/uv-required-version" alt="PyPI - Python Version"></a>
  <a href="https://github.com/juftin/uv-required-version/blob/main/LICENSE"><img src="https://img.shields.io/github/license/juftin/uv-required-version?color=blue" alt="GitHub License"></a>
  <a href="https://github.com/juftin/uv-required-version/actions/workflows/test.yaml?query=branch%3Amain"><img src="https://github.com/juftin/uv-required-version/actions/workflows/test.yaml/badge.svg?branch=main" alt="Testing Status"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
</p>

`uv-required-version` is a command line wrapper around [uv](https://github.com/astral-sh/uv)
that respects the [required-version](https://docs.astral.sh/uv/reference/settings/#required-version)
setting in your `pyproject.toml` / `uv.toml` file.

When `uv-required-version` detects a `required-version` setting, instead of running
`uv` directly it will run `uv tool run "uv==<required-version>" <commands>`, ensuring that the
correct version of `uv` is used.

Ideally, the functionality of this tool would be integrated into `uv` itself
(see [astral-sh/uv#11065](https://github.com/astral-sh/uv/issues/11065)) - until then
you can use `uv-required-version`.

## Usage

```shell
uv tool install uv-required-version
```

```shell
uv-required-version sync
```
