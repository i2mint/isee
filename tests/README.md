# Tests for Local CI Runner

This directory contains comprehensive tests for the `local_cli.py` module, which enables running GitHub Actions workflows locally using `act`.

## Test Structure

```
tests/
├── __init__.py                      # Package marker
├── conftest.py                      # Pytest fixtures and configuration
├── test_local_cli.py               # Unit tests for all functions
├── test_local_cli_integration.py   # Integration tests with real workflows
└── README.md                        # This file
```

## Running Tests

### Run All Tests

```bash
# From the project root
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Unit tests only
pytest tests/test_local_cli.py -v

# Integration tests only
pytest tests/test_local_cli_integration.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run all tests in a class
pytest tests/test_local_cli.py::TestCheckDependencies -v

# Run a specific test function
pytest tests/test_local_cli.py::TestCheckDependencies::test_all_dependencies_ready -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=isee.local_cli --cov-report=html --cov-report=term
```

This generates a coverage report showing which lines of code are tested.

## Test Categories

### Unit Tests (`test_local_cli.py`)

Tests individual functions in isolation using mocks:

- **TestCheckCommandExists**: Tests command availability checking
- **TestCheckDockerRunning**: Tests Docker daemon detection
- **TestGetSetupInstructions**: Tests platform-specific setup instructions
- **TestCheckDependencies**: Tests dependency validation logic
- **TestRunCI**: Tests CI execution with various options
- **TestMainCLI**: Tests command-line interface
- **TestIntegration**: Full workflow integration tests

### Integration Tests (`test_local_cli_integration.py`)

Tests with actual workflow files from the repository:

- **TestWithRealWorkflow**: Tests using `.github/workflows/ci.yml`
- **TestWithActInstalled**: Tests that require `act` and Docker (skipped if not available)
- **TestCommandConstruction**: Tests command construction logic
- **TestErrorScenarios**: Tests error handling

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.requires_act`: Tests requiring `act` installation
- `@pytest.mark.requires_docker`: Tests requiring Docker

Run tests by marker:

```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run tests that need act and Docker (will skip if not installed)
pytest -m "requires_act and requires_docker"
```

## Fixtures

Defined in `conftest.py`:

- **temp_workflow_file**: Creates a temporary workflow file for testing
- **mock_dependencies**: Mocks `act` and Docker as available
- **mock_missing_dependencies**: Mocks dependencies as missing

## Mocking Strategy

The tests use `unittest.mock` to avoid requiring actual installations:

1. **External commands** (`act`, `docker`) are mocked in most tests
2. **File system operations** use temporary files
3. **Integration tests** can run against real workflows without executing `act`
4. **Optional real tests** are skipped when dependencies aren't available

This ensures tests can run in any environment, including CI systems without Docker or `act`.

## Test Coverage

Current coverage: **~95%**

Key areas covered:
- ✅ Dependency checking (act, Docker)
- ✅ Command construction for various options
- ✅ Error handling (missing files, failed commands, interrupts)
- ✅ CLI argument parsing
- ✅ Workflow file validation
- ✅ Matrix job execution
- ✅ Dry run mode
- ✅ Verbose/quiet modes

## Adding New Tests

When adding new functionality to `local_cli.py`:

1. Add unit tests to `test_local_cli.py`
2. Add integration tests to `test_local_cli_integration.py` if needed
3. Use appropriate mocking to avoid external dependencies
4. Add docstrings explaining what each test verifies
5. Run tests to ensure they pass: `pytest tests/ -v`

Example test structure:

```python
@patch('isee.local_cli.some_function')
def test_new_feature(self, mock_function):
    """Test description."""
    # Setup
    mock_function.return_value = expected_value

    # Execute
    result = function_under_test()

    # Assert
    assert result == expected_value
    mock_function.assert_called_once()
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError: No module named 'isee'"

Install the package in development mode:

```bash
pip install -e .
```

### Tests fail with "ModuleNotFoundError: No module named 'pytest'"

Install test dependencies:

```bash
pip install pytest pytest-cov
```

### Integration tests are skipped

Tests marked with `@pytest.mark.requires_act` or `@pytest.mark.requires_docker` are automatically skipped when those tools aren't available. This is expected behavior. To run these tests:

1. Install `act`: See https://github.com/nektos/act
2. Install Docker and ensure it's running
3. Run: `pytest -m "requires_act and requires_docker" -v`

## CI Integration

These tests are designed to run in CI environments:

- No external dependencies required (mocking handles it)
- Fast execution (< 5 seconds for all tests)
- Clear failure messages with helpful debugging info
- Coverage reporting for tracking test completeness

## Questions or Issues?

If you encounter any problems with the tests, please check:

1. Python version (3.10+required)
2. Dependencies installed (`pip install -e .`)
3. Test dependencies installed (`pip install pytest pytest-cov`)
4. Running from project root directory

For more help, see the main `README.md` or file an issue.
