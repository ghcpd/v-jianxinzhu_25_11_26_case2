# Test runner script for Windows (PowerShell)
# Runs comprehensive test suite and generates reports

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Dependency Test Suite Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Virtual environment is not activated" -ForegroundColor Yellow
    Write-Host "Activating venv..." -ForegroundColor Yellow
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
    } else {
        Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
        Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Running tests with pytest..." -ForegroundColor Yellow
Write-Host ""

# Run tests with different options based on user input
Write-Host "Select test mode:" -ForegroundColor Cyan
Write-Host "1) Quick tests (skip integration tests)"
Write-Host "2) Full test suite (including integration tests)"
Write-Host "3) With coverage report"
Write-Host "4) Verbose output"
$choice = Read-Host "Enter choice (1/2/3/4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running quick tests..." -ForegroundColor Yellow
        pytest tests\ -v -m "not integration"
    }
    "2" {
        Write-Host ""
        Write-Host "Running full test suite..." -ForegroundColor Yellow
        pytest tests\ -v
    }
    "3" {
        Write-Host ""
        Write-Host "Running tests with coverage..." -ForegroundColor Yellow
        pytest tests\ --cov=sample_app --cov-report=html --cov-report=term
        Write-Host ""
        Write-Host "Coverage report generated in htmlcov\index.html" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "Running tests with verbose output..." -ForegroundColor Yellow
        pytest tests\ -vv -s
    }
    default {
        Write-Host ""
        Write-Host "Running default tests..." -ForegroundColor Yellow
        pytest tests\ -v
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test run complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
