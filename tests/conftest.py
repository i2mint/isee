"""Pytest configuration and shared fixtures for local_cli tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_workflow_file():
    """Create a temporary workflow file for testing.

    Yields the path to a temporary .github/workflows/ci.yml file.
    Cleans up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        workflow_dir = Path(tmpdir) / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflow_dir / "ci.yml"
        workflow_file.write_text(
            """
name: Test CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: echo "Testing"
"""
        )
        yield str(workflow_file)


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock external dependencies (act, docker) as available.

    This fixture makes tests run without requiring actual installation
    of act or Docker.
    """

    def mock_check_cmd(cmd):
        return True

    def mock_check_docker():
        return True

    monkeypatch.setattr("isee.local_cli._check_command_exists", mock_check_cmd)
    monkeypatch.setattr("isee.local_cli._check_docker_running", mock_check_docker)


@pytest.fixture
def mock_missing_dependencies(monkeypatch):
    """Mock external dependencies as missing.

    Useful for testing error handling when dependencies aren't available.
    """

    def mock_check_cmd(cmd):
        return False

    def mock_check_docker():
        return False

    monkeypatch.setattr("isee.local_cli._check_command_exists", mock_check_cmd)
    monkeypatch.setattr("isee.local_cli._check_docker_running", mock_check_docker)
