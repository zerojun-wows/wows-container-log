"""
Version utilities for Python projects.

This module provides functions to retrieve the current version of a project,
prioritizing installed package metadata and falling back to local pyproject.toml.

Functions
---------
read_version_from_pyproject()
    Extract the version directly from a local pyproject.toml file.
get_version(distribution_name)
    Get the version from the installed distribution or pyproject.toml.

Notes
-----
The version is obtained in the following order:

1. Try to read the version from the installed distribution metadata.
2. If the distribution is not installed (e.g., during development),
   fall back to the version specified in ``pyproject.toml``.
3. If both methods fail, a default version is returned by
   :func:`read_version_from_pyproject`.

Examples
--------
>>> from version_utils import get_version
>>> get_version("myproject")  # doctest: +SKIP
'1.2.3'

Author
------
zerojun

Version
-------
1.0
"""

from importlib.metadata import version as pkg_version, PackageNotFoundError
from pathlib import Path
import tomllib


def read_version_from_pyproject() -> str:
    """
    Read the project version from the local pyproject.toml file.

    Returns
    -------
    str
        Version string from pyproject.toml, or "0.0.0" if unavailable.
    """
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        return data["project"]["version"]
    except Exception:
        return "0.0.0"


def get_version(distribution_name: str) -> str:
    """
    Return the current version of the given project.

    If the project is installed, use importlib.metadata.
    During development, fall back to the version in pyproject.toml.

    Parameters
    ----------
    distribution_name: str
        Name of the installed distribution.

    Returns
    -------
    str
        Current version string.
    """
    try:
        return pkg_version(distribution_name)
    except PackageNotFoundError:
        return read_version_from_pyproject()
