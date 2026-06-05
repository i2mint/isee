"""Tests for pip_utils dependency resolution across pyproject.toml and setup.cfg.

These tests exercise the (side-effect-free) resolver functions so they never
touch pip. They cover the issue #38 scenario: a pyproject.toml-only project
must resolve its dependencies instead of raising "No file with name setup.cfg".
"""

from textwrap import dedent

import pytest

from isee.pip_utils import (
    resolve_install_requires,
    resolve_tests_require,
)

PYPROJECT = dedent(
    """
    [build-system]
    requires = ["hatchling"]

    [project]
    name = "demo"
    version = "0.0.1"
    dependencies = ["requests>=2", "rich"]

    [project.optional-dependencies]
    testing = ["pytest", "coverage"]
    docs = ["sphinx"]
    """
)

SETUP_CFG = dedent(
    """
    [options]
    install_requires =
        requests>=2
        rich
    tests_require =
        pytest
        coverage
    """
)


def _write(tmp_path, name, content):
    (tmp_path / name).write_text(content)


class TestPyproject:
    def test_install_requires(self, tmp_path):
        _write(tmp_path, "pyproject.toml", PYPROJECT)
        assert resolve_install_requires(project_dir=str(tmp_path)) == [
            "requests>=2",
            "rich",
        ]

    def test_tests_require_default_testing_extra(self, tmp_path):
        _write(tmp_path, "pyproject.toml", PYPROJECT)
        assert resolve_tests_require(project_dir=str(tmp_path)) == [
            "pytest",
            "coverage",
        ]

    def test_tests_require_custom_extra(self, tmp_path):
        _write(tmp_path, "pyproject.toml", PYPROJECT)
        assert resolve_tests_require(
            project_dir=str(tmp_path), test_extras=("docs",)
        ) == ["sphinx"]

    def test_no_dependencies_is_empty_not_error(self, tmp_path):
        _write(
            tmp_path,
            "pyproject.toml",
            "[project]\nname = 'demo'\nversion = '0.0.1'\n",
        )
        assert resolve_install_requires(project_dir=str(tmp_path)) == []
        assert resolve_tests_require(project_dir=str(tmp_path)) == []

    def test_pyproject_preferred_over_setup_cfg(self, tmp_path):
        _write(tmp_path, "pyproject.toml", PYPROJECT)
        _write(tmp_path, "setup.cfg", "[options]\ninstall_requires =\n    legacy-pkg\n")
        # pyproject wins
        assert "legacy-pkg" not in resolve_install_requires(project_dir=str(tmp_path))


class TestSetupCfg:
    def test_install_requires(self, tmp_path):
        _write(tmp_path, "setup.cfg", SETUP_CFG)
        assert resolve_install_requires(project_dir=str(tmp_path)) == [
            "requests>=2",
            "rich",
        ]

    def test_tests_require(self, tmp_path):
        _write(tmp_path, "setup.cfg", SETUP_CFG)
        assert resolve_tests_require(project_dir=str(tmp_path)) == [
            "pytest",
            "coverage",
        ]

    def test_pyproject_without_project_table_falls_back_to_cfg(self, tmp_path):
        # A pyproject.toml that only carries tool config must NOT shadow setup.cfg
        _write(tmp_path, "pyproject.toml", "[tool.ruff]\nline-length = 88\n")
        _write(tmp_path, "setup.cfg", SETUP_CFG)
        assert resolve_install_requires(project_dir=str(tmp_path)) == [
            "requests>=2",
            "rich",
        ]


class TestMissingMetadata:
    def test_raises_clear_error(self, tmp_path):
        with pytest.raises(RuntimeError, match="No dependency metadata found"):
            resolve_install_requires(project_dir=str(tmp_path))
        with pytest.raises(RuntimeError, match="No dependency metadata found"):
            resolve_tests_require(project_dir=str(tmp_path))
