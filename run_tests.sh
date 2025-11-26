#!/bin/bash
# Test runner script for Unix-like systems (Linux/macOS)
# Runs comprehensive test suite and generates reports

set -e

echo "================================"
echo "Dependency Test Suite Runner"
echo "================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated"
    echo "Activating venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "ERROR: Virtual environment not found"
        echo "Please run setup.sh first"
        exit 1
    fi
fi

echo "Running tests with pytest..."
echo ""

# Run tests with different options based on user input
echo "Select test mode:"
echo "1) Quick tests (skip integration tests)"
echo "2) Full test suite (including integration tests)"
echo "3) With coverage report"
echo "4) Verbose output"
read -p "Enter choice (1/2/3/4): " choice

case $choice in
    1)
        echo ""
        echo "Running quick tests..."
        pytest tests/ -v -m "not integration"
        ;;
    2)
        echo ""
        echo "Running full test suite..."
        pytest tests/ -v
        ;;
    3)
        echo ""
        echo "Running tests with coverage..."
        pytest tests/ --cov=sample_app --cov-report=html --cov-report=term
        echo ""
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    4)
        echo ""
        echo "Running tests with verbose output..."
        pytest tests/ -vv -s
        ;;
    *)
        echo ""
        echo "Running default tests..."
        pytest tests/ -v
        ;;
esac

echo ""
echo "================================"
echo "Test run complete!"
echo "================================"
