"""Run GitHub Actions workflows locally using act.

This module automates running your CI pipeline locally before pushing to GitHub.
It checks for required dependencies (act, Docker) and provides clear setup
instructions if anything is missing.

Usage:

```
# Check if everything is set up
python local_ci.py --check-deps

# Run entire CI workflow
python local_ci.py

# Run just validation job (all matrix combinations)
python local_ci.py -j validation

# Run specific matrix combination
python local_ci.py -j validation -m python-version:3.12

# See what would run without executing
python local_ci.py --dry-run

# Quiet mode (less output)
python local_ci.py -q
```

"""

import subprocess
import sys
from pathlib import Path
from typing import Literal


def _check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH.

    >>> _check_command_exists('python')
    True
    >>> _check_command_exists('definitely_not_a_real_command_xyz')
    False
    """
    try:
        subprocess.run(
            ['which', command],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _check_docker_running() -> bool:
    """Check if Docker daemon is running.

    >>> isinstance(_check_docker_running(), bool)
    True
    """
    try:
        subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def _get_setup_instructions() -> dict[str, str]:
    """Get platform-specific setup instructions for missing dependencies."""
    platform = sys.platform

    instructions = {
        'act': {
            'darwin': 'brew install act',
            'linux': 'curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash',
        },
        'docker': {
            'darwin': 'brew install --cask docker\n# Then start Docker Desktop from Applications',
            'linux': 'Visit https://docs.docker.com/engine/install/ for your distro',
        },
    }

    return {
        tool: instructions[tool].get(
            platform, f'Visit https://github.com/nektos/act for {tool} installation'
        )
        for tool in instructions
    }


def check_dependencies(*, verbose: bool = True) -> tuple[bool, list[str]]:
    """Check if act and Docker are available and provide setup instructions if not.

    Returns:
        Tuple of (all_ready: bool, missing: list[str])

    >>> ready, missing = check_dependencies(verbose=False)
    >>> isinstance(ready, bool) and isinstance(missing, list)
    True
    """
    missing = []
    instructions = _get_setup_instructions()

    if not _check_command_exists('act'):
        missing.append('act')
        if verbose:
            print("❌ 'act' is not installed.")
            print(f"   Install with: {instructions['act']}\n")

    if not _check_command_exists('docker'):
        missing.append('docker')
        if verbose:
            print("❌ 'docker' is not installed.")
            print(f"   Install with: {instructions['docker']}\n")
    elif not _check_docker_running():
        missing.append('docker-daemon')
        if verbose:
            print("❌ Docker is installed but not running.")
            print("   Start Docker and try again.\n")

    if not missing and verbose:
        print("✅ All dependencies ready (act, Docker)")

    return (len(missing) == 0, missing)


def run_ci(
    *,
    job: str | None = None,
    matrix: str | None = None,
    dry_run: bool = False,
    workflow_file: str = '.github/workflows/ci.yml',
    verbose: bool = True,
) -> int:
    """Run CI workflow locally using act.

    Args:
        job: Specific job to run (e.g., 'validation'). If None, runs all jobs.
        matrix: Matrix combination (e.g., 'python-version:3.12'). Requires job to be set.
        dry_run: If True, list what would run without executing.
        workflow_file: Path to workflow file to run.
        verbose: If True, print progress information.

    Returns:
        Exit code (0 for success, non-zero for failure).

    Examples:
        >>> # These examples don't actually run act, just demonstrate the interface
        >>> # run_ci(job='validation', matrix='python-version:3.12')  # Run one matrix combo
        >>> # run_ci(job='validation')  # Run all validation matrix combos
        >>> # run_ci(dry_run=True)  # See what would run
    """
    # Check dependencies first
    ready, missing = check_dependencies(verbose=verbose)
    if not ready:
        if verbose:
            print(f"\n❌ Cannot run CI: missing {', '.join(missing)}")
            print("   Fix the issues above and try again.")
        return 1

    # Verify workflow file exists
    workflow_path = Path(workflow_file)
    if not workflow_path.exists():
        if verbose:
            print(f"❌ Workflow file not found: {workflow_file}")
        return 1

    # Build act command
    cmd = ['act', '-W', workflow_file]

    if dry_run:
        cmd.append('-l')

    if job:
        cmd.extend(['-j', job])

    if matrix:
        if not job:
            if verbose:
                print("❌ --matrix requires --job to be specified")
            return 1
        cmd.extend(['--matrix', matrix])

    # Always bind local directory for easier debugging
    cmd.append('--bind')

    if verbose:
        print(f"🚀 Running: {' '.join(cmd)}\n")

    # Run act
    try:
        result = subprocess.run(cmd, check=False)

        if result.returncode != 0 and verbose:
            print("\n❌ CI failed. Docker containers preserved for debugging.")
            print("   View containers: docker ps -a")
            print("   View logs: docker logs <container-id>")
            print("   Remove containers: docker rm <container-id>")
        elif verbose:
            print("\n✅ CI passed!")

        return result.returncode

    except KeyboardInterrupt:
        if verbose:
            print("\n⚠️  Interrupted. Containers may still be running.")
            print("   View: docker ps -a")
        return 130


def main():
    """CLI entry point for running CI locally."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run GitHub Actions CI locally using act'
    )
    parser.add_argument(
        '-j',
        '--job',
        help='Specific job to run (e.g., validation)',
    )
    parser.add_argument(
        '-m',
        '--matrix',
        help='Matrix combination (e.g., python-version:3.12)',
    )
    parser.add_argument(
        '-n',
        '--dry-run',
        action='store_true',
        help='List what would run without executing',
    )
    parser.add_argument(
        '-w',
        '--workflow',
        default='.github/workflows/ci.yml',
        help='Path to workflow file (default: .github/workflows/ci.yml)',
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Suppress progress messages',
    )
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Only check dependencies and exit',
    )

    args = parser.parse_args()

    if args.check_deps:
        ready, _ = check_dependencies(verbose=not args.quiet)
        return 0 if ready else 1

    return run_ci(
        job=args.job,
        matrix=args.matrix,
        dry_run=args.dry_run,
        workflow_file=args.workflow,
        verbose=not args.quiet,
    )


if __name__ == '__main__':
    sys.exit(main())
