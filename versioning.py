"""
Version utilities for Python projects.

This module provides functions to retrieve the current version of a project,
prioritizing installed package metadata and falling back to local pyproject.toml.

Public functions:
    - read_version_from_pyproject() -> str: Extracts version directly from local pyproject.toml.
    - get_version(distribution_name: str) -> str: Gets version from installed distribution or pyproject.toml.

Example usage:
    >>> from version_utils import get_version
    >>> print(get_version("myproject"))  # Returns "1.2.3" or "0.0.0"

Author: zerojun
Version: 1.0
"""

from importlib.metadata import version as pkg_version, PackageNotFoundError
from pathlib import Path
import tomllib


def read_version_from_pyproject() -> str:
    """
    Read the project version from the local pyproject.toml file.

    :return: Version string from pyproject.toml, or "0.0.0" if unavailable.
    :rtype: str
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

    :param distribution_name: Name of the installed distribution.
    :type distribution_name: str
    :return: Current version string.
    :rtype: str
    """
    try:
        return pkg_version(distribution_name)
    except PackageNotFoundError:
        return read_version_from_pyproject()
