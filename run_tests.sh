#!/bin/bash
# Test runner script for local_cli tests

set -e  # Exit on error

# Fix for setuptools/distutils compatibility issue
export SETUPTOOLS_USE_DISTUTILS=stdlib

echo "🧪 Running Local CI Tests"
echo "========================"
echo

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed"
    echo "   Install with: pip install pytest pytest-cov"
    exit 1
fi

# Parse command line arguments
COVERAGE=false
VERBOSE=false
PATTERN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --pattern|-k)
            PATTERN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  -c, --coverage    Generate coverage report"
            echo "  -v, --verbose     Verbose output"
            echo "  -k, --pattern     Run tests matching pattern"
            echo "  -h, --help        Show this help message"
            echo
            echo "Examples:"
            echo "  $0                        # Run all tests"
            echo "  $0 --coverage             # Run with coverage report"
            echo "  $0 -k TestCheckDeps       # Run tests matching pattern"
            echo "  $0 --coverage --verbose   # Both coverage and verbose"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
CMD="pytest tests/"

if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=isee.local_cli --cov-report=term --cov-report=html"
fi

if [ -n "$PATTERN" ]; then
    CMD="$CMD -k $PATTERN"
fi

# Run tests
echo "Running: $CMD"
echo
$CMD

# Show coverage location if generated
if [ "$COVERAGE" = true ]; then
    echo
    echo "📊 Coverage report generated: htmlcov/index.html"
    echo "   Open with: xdg-open htmlcov/index.html (Linux) or open htmlcov/index.html (Mac)"
fi

echo
echo "✅ Tests completed successfully!"
