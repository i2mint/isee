"""Run GitHub Actions workflows locally using act.

This module automates running your CI pipeline locally before pushing to GitHub.
It checks for required dependencies (act, Docker) and provides clear setup
instructions if anything is missing.

Usage:

```
# Check if everything is set up
python -m isee.local_cli --check-deps

# Run entire CI workflow (fast, clean - no local artifacts)
python -m isee.local_cli

# Run with local artifacts for debugging
python -m isee.local_cli --bind

# Run just validation job (all matrix combinations)
python -m isee.local_cli -j validation

# Run specific matrix combination
python -m isee.local_cli -j validation -m python-version:3.12

# For M-series Macs (if needed)
python -m isee.local_cli --container-arch linux/amd64

# See what would run without executing
python -m isee.local_cli --dry-run

# Quiet mode (less output)
python -m isee.local_cli -q
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
            ["which", command],
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
            ["docker", "info"],
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
        "act": {
            "darwin": "brew install act",
            "linux": "curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash",
        },
        "docker": {
            "darwin": "brew install --cask docker\n# Then start Docker Desktop from Applications",
            "linux": "Visit https://docs.docker.com/engine/install/ for your distro",
        },
    }

    return {
        tool: instructions[tool].get(
            platform, f"Visit https://github.com/nektos/act for {tool} installation"
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

    if not _check_command_exists("act"):
        missing.append("act")
        if verbose:
            print("❌ 'act' is not installed.")
            print(f"   Install with: {instructions['act']}\n")

    if not _check_command_exists("docker"):
        missing.append("docker")
        if verbose:
            print("❌ 'docker' is not installed.")
            print(f"   Install with: {instructions['docker']}\n")
    elif not _check_docker_running():
        missing.append("docker-daemon")
        if verbose:
            print("❌ Docker is installed but not running.")
            print("   Start Docker and try again.\n")

    if not missing and verbose:
        print("✅ All dependencies ready (act, Docker)")

    return (len(missing) == 0, missing)


def _build_act_command(
    workflow_path: str,
    *,
    bind: bool = False,
    keep_container: bool = False,
    container_arch: str | None = None,
) -> list[str]:
    """Build the act command with appropriate flags.

    >>> cmd = _build_act_command('ci.yml')
    >>> '--bind' not in cmd and '--container-architecture' not in cmd
    True
    >>> cmd = _build_act_command('ci.yml', bind=True, container_arch='linux/amd64')
    >>> '--bind' in cmd and 'linux/amd64' in cmd
    True
    """
    cmd = ["act", "-W", workflow_path]

    if bind:
        cmd.append("--bind")

    if container_arch:  # Only add if explicitly specified
        cmd.extend(["--container-architecture", container_arch])

    if keep_container:
        cmd.append("--rm=false")

    return cmd


def run_ci(
    *,
    job: str | None = None,
    matrix: str | None = None,
    dry_run: bool = False,
    workflow_file: str = ".github/workflows/ci.yml",
    verbose: bool = True,
    bind: bool = False,
    container_arch: str | None = None,
) -> int:
    """Run CI workflow locally using act.

    Args:
        job: Specific job to run (e.g., 'validation'). If None, runs all jobs.
        matrix: Matrix combination (e.g., 'python-version:3.12'). Requires job to be set.
        dry_run: If True, list what would run without executing.
        workflow_file: Path to workflow file to run.
        verbose: If True, print progress information.
        bind: Mount working directory (creates local artifacts like dist/).
        container_arch: Container architecture (e.g., 'linux/amd64' for M-series Macs).

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
    cmd = _build_act_command(
        workflow_file,
        bind=bind,
        keep_container=False,
        container_arch=container_arch,
    )

    if dry_run:
        cmd.append("-l")

    if job:
        cmd.extend(["-j", job])

    if matrix:
        if not job:
            if verbose:
                print("❌ --matrix requires --job to be specified")
            return 1
        cmd.extend(["--matrix", matrix])

    if verbose:
        print(f"🚀 Running: {' '.join(cmd)}\n")

    # Run act
    try:
        result = subprocess.run(cmd, check=False)

        if result.returncode != 0 and verbose:
            print("\n❌ CI failed.")
            print("\n📋 Debugging tips:")
            print("   # List containers (including stopped ones)")
            print("   docker ps -a")
            print("\n   # Start and enter a stopped container for debugging")
            print("   docker start <container-id>")
            print("   docker exec -it <container-id> bash")
            print("\n   # View logs from a container")
            print("   docker logs <container-id>")
            print("\n   # Clean up when done")
            print("   docker rm <container-id>")
        elif verbose:
            print("\n✅ CI passed!")

        return result.returncode

    except KeyboardInterrupt:
        if verbose:
            print("\n⚠️  Interrupted. Containers may still be running.")
            print("   Check with: docker ps -a")
        return 130


def run_workflow_locally(
    workflow_path: str = None,
    *,
    bind: bool = False,
    keep_container: bool = False,
    container_architecture: str | None = None,
) -> int:
    """
    Run a GitHub Actions workflow locally using act.

    Args:
        workflow_path: Path to workflow file (if None, auto-detects)
        bind: Mount working directory into container (creates local artifacts)
        keep_container: Keep container after run for debugging
        container_architecture: Container architecture (e.g., 'linux/amd64')
    """
    # Check dependencies first
    ready, missing = check_dependencies(verbose=True)
    if not ready:
        print(f"\n❌ Cannot run workflow: missing {', '.join(missing)}")
        print("   Fix the issues above and try again.")
        return 1

    # Auto-detect workflow file if not provided
    if workflow_path is None:
        workflow_files = list(Path(".github/workflows").glob("*.yml"))
        if not workflow_files:
            print("❌ No workflow files found in .github/workflows/")
            return 1
        if len(workflow_files) > 1:
            print("⚠️  Multiple workflow files found:")
            for wf in workflow_files:
                print(f"   - {wf.name}")
            print("   Using the first one found.")
        workflow_path = str(workflow_files[0])

    # Build act command
    cmd = _build_act_command(
        workflow_path,
        bind=bind,
        keep_container=keep_container,
        container_arch=container_architecture,
    )

    # Run act
    try:
        result = subprocess.run(cmd, check=False)

        if result.returncode != 0:
            print("\n❌ Workflow run failed.")
            print("\n📋 Debugging tips:")
            print("   # List containers (including stopped ones)")
            print("   docker ps -a")
            print("\n   # Start and enter a stopped container for debugging")
            print("   docker start <container-id>")
            print("   docker exec -it <container-id> bash")
            print("\n   # Inside the container, you can:")
            print("   pwd                    # See working directory")
            print("   ls -la                 # List files")
            print("   python --version       # Check Python version")
            print("   pip list               # See installed packages")
            print("\n   # View logs from a container")
            print("   docker logs <container-id>")
            print("\n   # Clean up when done")
            print("   docker rm <container-id>")
        else:
            print("\n✅ Workflow run succeeded!")

        return result.returncode

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted. Containers may still be running.")
        print("   Check with: docker ps -a")
        return 130


def main():
    """CLI entry point for running CI locally."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run GitHub Actions CI locally using act"
    )
    parser.add_argument(
        "-j",
        "--job",
        help="Specific job to run (e.g., validation)",
    )
    parser.add_argument(
        "-m",
        "--matrix",
        help="Matrix combination (e.g., python-version:3.12)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="List what would run without executing",
    )
    parser.add_argument(
        "-w",
        "--workflow",
        default=".github/workflows/ci.yml",
        help="Path to workflow file (default: .github/workflows/ci.yml)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Only check dependencies and exit",
    )
    parser.add_argument(
        "--bind",
        action="store_true",
        help="Mount working directory (creates local artifacts like dist/)",
    )
    parser.add_argument(
        "--container-arch",
        help="Container architecture (e.g., linux/amd64 for M-series Macs)",
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
        bind=args.bind,
        container_arch=args.container_arch,
    )


if __name__ == "__main__":
    sys.exit(main())
