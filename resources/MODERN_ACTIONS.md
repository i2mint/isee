# Modern GitHub Actions for CI/CD

This directory contains modernized GitHub Actions that use current best practices and tools.

## Overview

These actions replace older tooling with modern equivalents:

| Old Tool | Modern Replacement | Benefits |
|----------|-------------------|----------|
| black | ruff | 10-100x faster, includes linting |
| pylint | ruff | Faster, easier configuration |
| flake8 | ruff | All-in-one solution |
| isort | ruff | Built into ruff |
| setup.py | pyproject.toml + build | PEP 517/518 compliant |
| wheel/setuptools | build | Modern, isolated builds |

## Actions

### 1. install-deps
Modern dependency installation supporting multiple config formats.

**Supports:**
- `pyproject.toml` (preferred)
- `setup.cfg` (backward compatible)
- `requirements.txt`
- PyPI, APT, and NPM packages
- Extras/optional dependencies

**Example:**
```yaml
- uses: i2mint/isee/actions/install-deps@master
  with:
    dependency-files: pyproject.toml
    extras: dev,test
```

### 2. ruff-format
Fast code formatting using ruff (replaces black).

**Features:**
- 10-100x faster than black
- Black-compatible output
- Check-only mode for CI

**Example:**
```yaml
- uses: i2mint/isee/actions/ruff-format@master
  with:
    line-length: 88
    check-only: false  # Set true for validation
```

### 3. ruff-lint
Comprehensive linting (replaces pylint, flake8, isort).

**Features:**
- Extremely fast
- GitHub Actions annotations
- Auto-fix capability
- Hundreds of rules

**Example:**
```yaml
- uses: i2mint/isee/actions/ruff-lint@master
  with:
    root-dir: my_package
    select: E,F,I  # Error, pyflakes, imports
    exclude: tests,examples
```

### 4. run-tests
Streamlined pytest execution.

**Features:**
- Automatic extras installation
- Doctest support
- Coverage reporting
- Clean configuration

**Example:**
```yaml
- uses: i2mint/isee/actions/run-tests@master
  with:
    root-dir: my_package
    coverage: true
    exclude: examples,scrap
```

### 5. version-bump
Semantic version generation with modern config support.

**Supports:**
- `pyproject.toml` (TOML-based versioning)
- `setup.cfg` (backward compatible)
- Semantic versioning from git history
- Outputs version for downstream steps

**Example:**
```yaml
- uses: i2mint/isee/actions/version-bump@master
  id: version
- run: echo "Version is ${{ steps.version.outputs.version }}"
```

### 6. build-dist
PEP 517-compliant package building.

**Features:**
- Uses `python -m build`
- Isolated build environment
- Auto-detects build backend
- Creates both sdist and wheel

**Example:**
```yaml
- uses: i2mint/isee/actions/build-dist@master
  with:
    sdist: true
    wheel: true
```

### 7. pypi-upload
Reliable PyPI publishing.

**Features:**
- Token authentication support
- Test PyPI support
- Skip existing packages
- Verbose logging

**Example:**
```yaml
- uses: i2mint/isee/actions/pypi-upload@master
  with:
    pypi-username: __token__
    pypi-password: ${{ secrets.PYPI_TOKEN }}
```

### 8. git-commit
Simple git commit and push (no external dependencies).

**Features:**
- Configurable user identity
- Pattern-based file addition
- Optional push
- Empty commit support

**Example:**
```yaml
- uses: i2mint/isee/actions/git-commit@master
  with:
    commit-message: "chore: update version"
    ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### 9. git-tag
Git tagging without external tools.

**Features:**
- Lightweight or annotated tags
- Force option
- Automatic push
- Version tagging support

**Example:**
```yaml
- uses: i2mint/isee/actions/git-tag@master
  with:
    tag: ${{ steps.version.outputs.version }}
    message: "Release v${{ steps.version.outputs.version }}"
```

## Migration Guide

### From Old Actions

Replace these in your workflow:

```yaml
# OLD
- uses: i2mint/isee/actions/install-packages@master
# NEW
- uses: i2mint/isee/actions/install-deps@master

# OLD
- uses: i2mint/isee/actions/format-source-code@master
# NEW
- uses: i2mint/isee/actions/ruff-format@master

# OLD
- uses: i2mint/isee/actions/pylint-validation@master
# NEW
- uses: i2mint/isee/actions/ruff-lint@master

# OLD
- uses: i2mint/isee/actions/pytest-validation@master
# NEW
- uses: i2mint/isee/actions/run-tests@master

# OLD
- uses: i2mint/isee/actions/bump-version-number@master
# NEW
- uses: i2mint/isee/actions/version-bump@master

# OLD
- uses: i2mint/isee/actions/package@master
# NEW
- uses: i2mint/isee/actions/build-dist@master

# OLD
- uses: i2mint/isee/actions/publish@master
# NEW
- uses: i2mint/isee/actions/pypi-upload@master

# OLD
- uses: i2mint/isee/actions/check-in@master
# NEW
- uses: i2mint/isee/actions/git-commit@master

# OLD
- uses: i2mint/isee/actions/tag-repository@master
# NEW
- uses: i2mint/isee/actions/git-tag@master
```

### Complete Modern Workflow

See `resources/ci-modern.yml` for a complete example workflow using all modern actions.

## Configuration Files

### Recommended: pyproject.toml

Modern Python projects should use `pyproject.toml`:

```toml
[project]
name = "my-package"
version = "0.1.0"
dependencies = [
    "numpy>=1.20",
]

[project.optional-dependencies]
dev = ["ruff", "pytest"]
test = ["pytest", "pytest-cov"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
exclude = ["tests", "examples"]
```

### Backward Compatible: setup.cfg

Still supported for existing projects:

```ini
[metadata]
name = my-package
version = 0.1.0

[options]
install_requires =
    numpy>=1.20

[options.extras_require]
testing =
    pytest
    pytest-cov
```

## Performance Comparison

| Tool | Lines/sec | Relative Speed |
|------|-----------|----------------|
| ruff | ~50,000 | 10-100x faster |
| black | ~5,000 | baseline |
| pylint | ~2,000 | 25x slower |

## Key Benefits

1. **Speed**: Ruff is 10-100x faster than black/pylint
2. **Simplicity**: Fewer dependencies and tools
3. **Modern**: PEP 517/518 compliant
4. **Maintainable**: Clear, focused actions
5. **Standard**: Uses official Python packaging tools

## Questions?

See the main [isee README](../README.md) for general CI documentation.
