# Running GitHub Actions Locally

This guide shows you how to run your GitHub Actions CI workflow locally using the `local_cli.py` module.

## What It Does

The local CI runner:
- ✅ Runs your `.github/workflows/ci.yml` locally using [act](https://github.com/nektos/act)
- ✅ Spins up isolated Docker containers that mimic GitHub's runners
- ✅ Executes each CI step exactly as defined in your workflow
- ✅ Cleans up containers on success, preserves them on failure for debugging
- ✅ Provides clear feedback on what's happening

## Quick Start

### 1. Check Dependencies

```bash
python -m isee.local_cli --check-deps
```

This checks if `act` and Docker are installed and running. If not, you'll get installation instructions.

### 2. Run Your CI

```bash
# Run the entire CI workflow
python -m isee.local_cli

# Run just the validation job
python -m isee.local_cli -j validation

# Run with specific Python version
python -m isee.local_cli -j validation -m python-version:3.10

# See what would run (dry run)
python -m isee.local_cli --dry-run
```

## Installation

### Install act

**macOS:**
```bash
brew install act
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

**Windows:**
```bash
choco install act-cli
```

### Install Docker

Follow instructions at https://docs.docker.com/get-docker/

Make sure Docker is running before using the local CI runner.

## Usage Examples

### Run Entire Workflow

```bash
python -m isee.local_cli
```

This runs all jobs in your `.github/workflows/ci.yml`.

### Run Specific Job

```bash
# Run just validation
python -m isee.local_cli -j validation

# Run just publish
python -m isee.local_cli -j publish
```

### Run Specific Matrix Combination

```bash
# Run validation with Python 3.10
python -m isee.local_cli -j validation -m python-version:3.10
```

### Dry Run (List Jobs)

```bash
python -m isee.local_cli --dry-run
```

Shows what jobs and steps would run without actually executing them.

### Use Custom Workflow File

```bash
python -m isee.local_cli -w .github/workflows/test.yml
```

### Quiet Mode

```bash
python -m isee.local_cli -q
```

Suppresses progress messages.

## Command-Line Options

```
usage: local_cli.py [-h] [-j JOB] [-m MATRIX] [-n] [-w WORKFLOW] [-q] [--check-deps]

Run GitHub Actions CI locally using act

options:
  -h, --help            show this help message and exit
  -j JOB, --job JOB     Specific job to run (e.g., validation)
  -m MATRIX, --matrix MATRIX
                        Matrix combination (e.g., python-version:3.12)
  -n, --dry-run         List what would run without executing
  -w WORKFLOW, --workflow WORKFLOW
                        Path to workflow file (default: .github/workflows/ci.yml)
  -q, --quiet           Suppress progress messages
  --check-deps          Only check dependencies and exit
```

## Debugging Failures

When CI fails locally, containers are preserved for debugging:

```bash
# List containers
docker ps -a

# View logs
docker logs <container-id>

# Inspect container
docker exec -it <container-id> /bin/bash

# Remove container when done
docker rm <container-id>
```

## How It Works

1. **Dependency Check**: Verifies `act` and Docker are available
2. **Workflow Parse**: Reads your `.github/workflows/ci.yml`
3. **Container Spin-up**: Creates Docker containers mimicking GitHub runners
4. **Job Execution**: Runs each step in your workflow
5. **Cleanup**: Removes containers on success, keeps them on failure

## Single Source of Truth

Your `.github/workflows/ci.yml` is the **only** definition of your CI process. The local runner uses the exact same workflow, ensuring what passes locally will pass on GitHub.

## Differences from GitHub Actions

A few things work differently locally:

- **Secrets**: Not available by default (use `.secrets` file with act)
- **GitHub Context**: Limited (can mock with `-s GITHUB_TOKEN=...`)
- **Caching**: Works differently than GitHub's cache
- **Performance**: May be slower or faster depending on your machine

## Troubleshooting

### "act not found"

Install act:
- macOS: `brew install act`
- Linux: `curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash`

### "Docker not running"

Start Docker Desktop or the Docker daemon.

### "Cannot connect to Docker daemon"

On Linux, you may need to add your user to the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### "Workflow file not found"

Make sure you're running from the repository root, or specify the workflow path with `-w`.

## Testing

The local CI runner has comprehensive tests. To run them:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=isee.local_cli --cov-report=html

# Or use the test runner script
bash run_tests.sh
```

See `tests/README.md` for more details on testing.

## CI Integration

You can also use this in your CI to test workflows:

```yaml
- name: Test workflow locally
  run: |
    pip install -e .
    python -m isee.local_cli --dry-run
```

## More Information

- [act documentation](https://github.com/nektos/act)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Docker documentation](https://docs.docker.com/)

## Questions?

File an issue at https://github.com/i2mint/isee/issues
