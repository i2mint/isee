"""Integration tests for local_cli.py with real workflow files.

These tests use the actual .github/workflows/ci.yml file from the repository
to test more realistic scenarios.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from isee.local_cli import run_ci


@pytest.mark.integration
class TestWithRealWorkflow:
    """Integration tests using the actual CI workflow file."""

    def test_workflow_file_exists(self):
        """Verify that the CI workflow file exists."""
        workflow_path = Path('.github/workflows/ci.yml')
        assert workflow_path.exists(), "CI workflow file should exist"

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_run_with_actual_workflow(self, mock_check_deps, mock_subprocess):
        """Test running with the actual workflow file from the repo."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(
            workflow_file='.github/workflows/ci.yml', verbose=False
        )

        assert exit_code == 0
        # Verify act was called with our workflow
        cmd = mock_subprocess.call_args[0][0]
        assert 'act' in cmd
        assert '.github/workflows/ci.yml' in cmd

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_run_validation_job(self, mock_check_deps, mock_subprocess):
        """Test running the validation job specifically."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(job='validation', verbose=False)

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert '-j' in cmd
        assert 'validation' in cmd

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_run_publish_job(self, mock_check_deps, mock_subprocess):
        """Test running the publish job specifically."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(job='publish', verbose=False)

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert '-j' in cmd
        assert 'publish' in cmd

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_run_with_python_matrix(self, mock_check_deps, mock_subprocess):
        """Test running with Python version matrix."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(
            job='validation',
            matrix='python-version:3.10',
            verbose=False,
        )

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert '--matrix' in cmd
        assert 'python-version:3.10' in cmd

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_dry_run_lists_jobs(self, mock_check_deps, mock_subprocess):
        """Test that dry run lists available jobs."""
        mock_check_deps.return_value = (True, [])
        # Simulate act -l output
        mock_subprocess.return_value = MagicMock(returncode=0)

        exit_code = run_ci(dry_run=True, verbose=False)

        assert exit_code == 0
        cmd = mock_subprocess.call_args[0][0]
        assert '-l' in cmd


@pytest.mark.integration
@pytest.mark.requires_act
@pytest.mark.requires_docker
class TestWithActInstalled:
    """Tests that actually run act (only if installed).

    These tests are skipped unless act and Docker are actually available.
    Run with: pytest -m "requires_act and requires_docker"
    """

    @pytest.fixture(autouse=True)
    def skip_if_not_installed(self):
        """Skip these tests if act or Docker aren't available."""
        from isee.local_cli import check_dependencies

        ready, missing = check_dependencies(verbose=False)
        if not ready:
            pytest.skip(f"Skipping: missing {', '.join(missing)}")

    def test_dry_run_actually_works(self):
        """Actually run act in dry-run mode to list jobs."""
        exit_code = run_ci(dry_run=True, verbose=True)
        assert exit_code == 0

    def test_help_output(self):
        """Test that act help works."""
        result = subprocess.run(
            ['act', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert 'act' in result.stdout.lower()


@pytest.mark.integration
class TestCommandConstruction:
    """Test that the correct act commands are constructed."""

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_basic_command_structure(self, mock_check_deps, mock_subprocess):
        """Test basic act command structure."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        run_ci(verbose=False)

        cmd = mock_subprocess.call_args[0][0]
        assert cmd[0] == 'act'
        assert '-W' in cmd
        assert '--bind' in cmd

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_command_with_all_options(self, mock_check_deps, mock_subprocess):
        """Test command construction with all options."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=0)

        run_ci(
            job='validation',
            matrix='python-version:3.10',
            workflow_file='.github/workflows/ci.yml',
            verbose=False,
        )

        cmd = mock_subprocess.call_args[0][0]
        assert 'act' in cmd
        assert '-W' in cmd
        assert '.github/workflows/ci.yml' in cmd
        assert '-j' in cmd
        assert 'validation' in cmd
        assert '--matrix' in cmd
        assert 'python-version:3.10' in cmd
        assert '--bind' in cmd


@pytest.mark.integration
class TestErrorScenarios:
    """Test various error scenarios."""

    @patch('isee.local_cli.check_dependencies')
    def test_nonexistent_workflow(self, mock_check_deps):
        """Test error handling for nonexistent workflow file."""
        mock_check_deps.return_value = (True, [])

        exit_code = run_ci(
            workflow_file='/nonexistent/path/workflow.yml',
            verbose=False,
        )

        assert exit_code == 1

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_act_command_fails(self, mock_check_deps, mock_subprocess):
        """Test handling of act command failure."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.return_value = MagicMock(returncode=1)

        exit_code = run_ci(verbose=False)

        assert exit_code == 1

    @patch('subprocess.run')
    @patch('isee.local_cli.check_dependencies')
    def test_interrupt_handling(self, mock_check_deps, mock_subprocess):
        """Test keyboard interrupt handling."""
        mock_check_deps.return_value = (True, [])
        mock_subprocess.side_effect = KeyboardInterrupt()

        exit_code = run_ci(verbose=False)

        assert exit_code == 130


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
