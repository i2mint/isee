"""Tests for local_cli.py - GitHub Actions local runner using act.

This test suite mocks external dependencies (act, Docker) to ensure tests
can run in any environment without requiring those tools to be installed.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from isee.local_cli import (
    _check_command_exists,
    _check_docker_running,
    _get_setup_instructions,
    check_dependencies,
    main,
    run_ci,
)


class TestCheckCommandExists:
    """Test the _check_command_exists helper function."""

    def test_existing_command(self):
        """Test that an existing command returns True."""
        # Python should exist on any system running these tests
        assert _check_command_exists("python")

    def test_nonexistent_command(self):
        """Test that a non-existent command returns False."""
        assert not _check_command_exists("definitely_not_a_real_command_xyz_12345")

    @patch("subprocess.run")
    def test_command_exists_with_mock(self, mock_run):
        """Test successful command detection with mocked subprocess."""
        mock_run.return_value = MagicMock(returncode=0)
        assert _check_command_exists("act")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_command_not_found_with_mock(self, mock_run):
        """Test command not found with mocked subprocess."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "which")
        assert not _check_command_exists("act")


class TestCheckDockerRunning:
    """Test the _check_docker_running helper function."""

    @patch("subprocess.run")
    def test_docker_running(self, mock_run):
        """Test when Docker daemon is running."""
        mock_run.return_value = MagicMock(returncode=0)
        assert _check_docker_running()
        mock_run.assert_called_once_with(
            ["docker", "info"],
            capture_output=True,
            check=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_docker_not_running(self, mock_run):
        """Test when Docker daemon is not running."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker info")
        assert not _check_docker_running()

    @patch("subprocess.run")
    def test_docker_command_not_found(self, mock_run):
        """Test when Docker command doesn't exist."""
        mock_run.side_effect = FileNotFoundError()
        assert not _check_docker_running()

    @patch("subprocess.run")
    def test_docker_timeout(self, mock_run):
        """Test when Docker command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker info", 5)
        assert not _check_docker_running()


class TestGetSetupInstructions:
    """Test the _get_setup_instructions helper function."""

    def test_returns_dict(self):
        """Test that instructions are returned as a dictionary."""
        instructions = _get_setup_instructions()
        assert isinstance(instructions, dict)
        assert "act" in instructions
        assert "docker" in instructions

    def test_instructions_not_empty(self):
        """Test that all instructions contain actual content."""
        instructions = _get_setup_instructions()
        for tool, instruction in instructions.items():
            assert instruction, f"Empty instruction for {tool}"
            assert isinstance(instruction, str)


class TestCheckDependencies:
    """Test the check_dependencies function."""

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_all_dependencies_ready(self, mock_check_cmd, mock_check_docker):
        """Test when all dependencies are available."""
        mock_check_cmd.return_value = True
        mock_check_docker.return_value = True

        ready, missing = check_dependencies(verbose=False)

        assert ready is True
        assert missing == []

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_act_missing(self, mock_check_cmd, mock_check_docker):
        """Test when act is not installed."""
        mock_check_cmd.side_effect = lambda cmd: cmd != "act"
        mock_check_docker.return_value = True

        ready, missing = check_dependencies(verbose=False)

        assert ready is False
        assert "act" in missing
        assert "docker" not in missing

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_docker_missing(self, mock_check_cmd, mock_check_docker):
        """Test when Docker is not installed."""
        mock_check_cmd.side_effect = lambda cmd: cmd != "docker"
        mock_check_docker.return_value = False

        ready, missing = check_dependencies(verbose=False)

        assert ready is False
        assert "docker" in missing

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_docker_not_running(self, mock_check_cmd, mock_check_docker):
        """Test when Docker is installed but not running."""
        mock_check_cmd.return_value = True
        mock_check_docker.return_value = False

        ready, missing = check_dependencies(verbose=False)

        assert ready is False
        assert "docker-daemon" in missing

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_all_missing(self, mock_check_cmd, mock_check_docker):
        """Test when all dependencies are missing."""
        mock_check_cmd.return_value = False
        mock_check_docker.return_value = False

        ready, missing = check_dependencies(verbose=False)

        assert ready is False
        assert len(missing) >= 2  # At least act and docker

    @patch("builtins.print")
    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_verbose_output_success(
        self, mock_check_cmd, mock_check_docker, mock_print
    ):
        """Test verbose output when all dependencies are ready."""
        mock_check_cmd.return_value = True
        mock_check_docker.return_value = True

        ready, missing = check_dependencies(verbose=True)

        assert ready is True
        # Should print success message
        assert any("✅" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.print")
    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_verbose_output_failure(
        self, mock_check_cmd, mock_check_docker, mock_print
    ):
        """Test verbose output when dependencies are missing."""
        mock_check_cmd.return_value = False
        mock_check_docker.return_value = False

        ready, missing = check_dependencies(verbose=True)

        assert ready is False
        # Should print error messages
        assert any("❌" in str(call) for call in mock_print.call_args_list)


class TestRunCI:
    """Test the run_ci function."""

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_success(self, mock_check_deps, mock_subprocess):
        """Test successful CI run."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(verbose=False)

        assert exit_code == 0
        mock_subprocess.assert_called_once()
        # Check that act was called
        cmd = mock_subprocess.call_args[0][0]
        assert cmd[0] == "act"

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_failure(self, mock_check_deps, mock_subprocess):
        """Test CI run with failures."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=1)

        exit_code = run_ci(verbose=False)

        assert exit_code == 1

    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_missing_dependencies(self, mock_check_deps):
        """Test CI run when dependencies are missing."""
        mock_check_deps.return_value = (False, ["act", "docker"])

        exit_code = run_ci(verbose=False)

        assert exit_code == 1

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_with_job(self, mock_check_deps, mock_subprocess):
        """Test running a specific job."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(job="validation", verbose=False)

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert "-j" in cmd
        assert "validation" in cmd

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_with_matrix(self, mock_check_deps, mock_subprocess):
        """Test running with specific matrix combination."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(
            job="validation", matrix="python-version:3.12", verbose=False
        )

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert "--matrix" in cmd
        assert "python-version:3.12" in cmd

    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_matrix_without_job(self, mock_check_deps):
        """Test that matrix requires job to be specified."""
        mock_check_deps.return_value = (True, [])

        exit_code = run_ci(matrix="python-version:3.12", verbose=False)

        assert exit_code == 1

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_dry_run(self, mock_check_deps, mock_subprocess):
        """Test dry run mode (list workflows without executing)."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(dry_run=True, verbose=False)

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert "-l" in cmd

    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_missing_workflow_file(self, mock_check_deps):
        """Test when workflow file doesn't exist."""
        mock_check_deps.return_value = (True, [])

        exit_code = run_ci(workflow_file="/nonexistent/workflow.yml", verbose=False)

        assert exit_code == 1

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_keyboard_interrupt(self, mock_check_deps, mock_subprocess):
        """Test handling of keyboard interrupt."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.side_effect = KeyboardInterrupt()

        exit_code = run_ci(verbose=False)

        assert exit_code == 130

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_binds_local_directory(self, mock_check_deps, mock_subprocess):
        """Test that local directory is bound for debugging."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        run_ci(verbose=False)

        cmd = mock_subprocess.call_args[0][0]
        assert "--bind" in cmd

    @patch("subprocess.run")
    @patch("isee.local_cli.check_dependencies")
    def test_run_ci_custom_workflow(self, mock_check_deps, mock_subprocess):
        """Test running with custom workflow file."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Create a temporary workflow file for testing
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("name: test\n")
            temp_workflow = f.name

        try:
            exit_code = run_ci(workflow_file=temp_workflow, verbose=False)
            assert exit_code == 0

            cmd = mock_subprocess.call_args[0][0]
            assert "-W" in cmd
            assert temp_workflow in cmd
        finally:
            Path(temp_workflow).unlink()


class TestMainCLI:
    """Test the main CLI entry point."""

    @patch("isee.local_cli.check_dependencies")
    @patch("sys.argv", ["local_cli.py", "--check-deps"])
    def test_main_check_deps_success(self, mock_check_deps):
        """Test --check-deps flag with all dependencies available."""
        mock_check_deps.return_value = (True, [])

        exit_code = main()

        assert exit_code == 0
        mock_check_deps.assert_called_once()

    @patch("isee.local_cli.check_dependencies")
    @patch("sys.argv", ["local_cli.py", "--check-deps"])
    def test_main_check_deps_failure(self, mock_check_deps):
        """Test --check-deps flag with missing dependencies."""
        mock_check_deps.return_value = (False, ["act"])

        exit_code = main()

        assert exit_code == 1

    @patch("isee.local_cli.run_ci")
    @patch("sys.argv", ["local_cli.py"])
    def test_main_default_run(self, mock_run_ci):
        """Test default run without arguments."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        mock_run_ci.assert_called_once()

    @patch("isee.local_cli.run_ci")
    @patch("sys.argv", ["local_cli.py", "-j", "validation"])
    def test_main_with_job(self, mock_run_ci):
        """Test running specific job via CLI."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        # Check that job was passed
        call_kwargs = mock_run_ci.call_args[1]
        assert call_kwargs["job"] == "validation"

    @patch("isee.local_cli.run_ci")
    @patch(
        "sys.argv", ["local_cli.py", "-j", "validation", "-m", "python-version:3.12"]
    )
    def test_main_with_matrix(self, mock_run_ci):
        """Test running with matrix via CLI."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        call_kwargs = mock_run_ci.call_args[1]
        assert call_kwargs["job"] == "validation"
        assert call_kwargs["matrix"] == "python-version:3.12"

    @patch("isee.local_cli.run_ci")
    @patch("sys.argv", ["local_cli.py", "--dry-run"])
    def test_main_dry_run(self, mock_run_ci):
        """Test dry run via CLI."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        call_kwargs = mock_run_ci.call_args[1]
        assert call_kwargs["dry_run"] is True

    @patch("sys.argv", ["local_cli.py", "-q"])
    @patch("isee.local_cli.run_ci")
    def test_main_quiet_mode(self, mock_run_ci):
        """Test quiet mode via CLI."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        call_kwargs = mock_run_ci.call_args[1]
        assert call_kwargs["verbose"] is False

    @patch("isee.local_cli.run_ci")
    @patch("sys.argv", ["local_cli.py", "-w", "custom.yml"])
    def test_main_custom_workflow(self, mock_run_ci):
        """Test custom workflow file via CLI."""
        mock_run_ci.return_value = 0

        exit_code = main()

        assert exit_code == 0
        call_kwargs = mock_run_ci.call_args[1]
        assert call_kwargs["workflow_file"] == "custom.yml"


class TestIntegration:
    """Integration tests that test the full workflow."""

    @patch("subprocess.run")
    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_full_ci_run_success(
        self, mock_check_cmd, mock_check_docker, mock_subprocess
    ):
        """Test complete successful CI run from start to finish."""
        # Setup: all dependencies available
        mock_check_cmd.return_value = True
        mock_check_docker.return_value = True
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Run CI
        exit_code = run_ci(verbose=False)

        # Verify
        assert exit_code == 0
        assert mock_subprocess.called

    @patch("subprocess.run")
    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_full_ci_run_with_failure(
        self, mock_check_cmd, mock_check_docker, mock_subprocess
    ):
        """Test complete CI run with failure."""
        # Setup
        mock_check_cmd.return_value = True
        mock_check_docker.return_value = True
        mock_subprocess.return_value = MagicMock(returncode=1)

        # Run CI
        exit_code = run_ci(verbose=False)

        # Verify
        assert exit_code == 1

    @patch("isee.local_cli._check_docker_running")
    @patch("isee.local_cli._check_command_exists")
    def test_dependency_check_prevents_run(self, mock_check_cmd, mock_check_docker):
        """Test that missing dependencies prevent CI from running."""
        # Setup: missing dependencies
        mock_check_cmd.return_value = False
        mock_check_docker.return_value = False

        # Try to run CI
        exit_code = run_ci(verbose=False)

        # Verify: should fail without attempting to run act
        assert exit_code == 1


# Doctests are embedded in the original module, but we can test them here too
def test_doctests():
    """Run doctests embedded in the module."""
    import doctest
    import isee.local_cli

    results = doctest.testmod(isee.local_cli, verbose=False)
    assert results.failed == 0, f"{results.failed} doctests failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
