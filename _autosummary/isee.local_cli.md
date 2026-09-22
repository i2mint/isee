# isee.local_cli

Run GitHub Actions workflows locally using act.

This module automates running your CI pipeline locally before pushing to GitHub.
It checks for required dependencies (act, Docker) and provides clear setup
instructions if anything is missing.

Usage:

```text
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

### Functions

| [`check_dependencies`](#isee.local_cli.check_dependencies)(\*[, verbose])                | Check if act and Docker are available and provide setup instructions if not.   |
|---------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [`main`](#isee.local_cli.main)()                                           | CLI entry point for running CI locally.                                        |
| [`run_ci`](#isee.local_cli.run_ci)(\*[, job, matrix, dry_run, ...])          | Run CI workflow locally using act.                                             |
| [`run_workflow_locally`](#isee.local_cli.run_workflow_locally)([workflow_path, bind, ...]) | Run a GitHub Actions workflow locally using act.                               |

### isee.local_cli.check_dependencies(, verbose=True)

Check if act and Docker are available and provide setup instructions if not.

* **Returns:**
  bool, missing: list[str])
* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`bool`](https://docs.python.org/3/builtins/functions.html#bool), [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]

```pycon
>>> ready, missing = check_dependencies(verbose=False)
>>> isinstance(ready, bool) and isinstance(missing, list)
True
```

### isee.local_cli.main()

CLI entry point for running CI locally.

### isee.local_cli.run_ci(, job=None, matrix=None, dry_run=False, workflow_file='.github/workflows/ci.yml', verbose=True, bind=False, container_arch=None)

Run CI workflow locally using act.

* **Parameters:**
  * **job** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Specific job to run (e.g., ‘validation’). If None, runs all jobs.
  * **matrix** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Matrix combination (e.g., ‘python-version:3.12’). Requires job to be set.
  * **dry_run** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, list what would run without executing.
  * **workflow_file** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Path to workflow file to run.
  * **verbose** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, print progress information.
  * **bind** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Mount working directory (creates local artifacts like dist/).
  * **container_arch** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Container architecture (e.g., ‘linux/amd64’ for M-series Macs).
* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)
* **Returns:**
  Exit code (0 for success, non-zero for failure).

### Examples

```pycon
>>> # These examples don't actually run act, just demonstrate the interface
>>> # run_ci(job='validation', matrix='python-version:3.12')  # Run one matrix combo
>>> # run_ci(job='validation')  # Run all validation matrix combos
>>> # run_ci(dry_run=True)  # See what would run
```

### isee.local_cli.run_workflow_locally(workflow_path=None, , bind=False, keep_container=False, container_architecture=None)

Run a GitHub Actions workflow locally using act.

* **Parameters:**
  * **workflow_path** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Path to workflow file (if None, auto-detects)
  * **bind** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Mount working directory into container (creates local artifacts)
  * **keep_container** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Keep container after run for debugging
  * **container_architecture** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Container architecture (e.g., ‘linux/amd64’)
* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)
