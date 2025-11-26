# Cross-platform setup script for Windows (PowerShell)
# Sets up Python environment and installs dependencies

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Dependency Modernization Setup" -ForegroundColor Cyan
Write-Host "Platform: Windows" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "ERROR: Python 3.8 or higher is required" -ForegroundColor Red
            exit 1
        }
        Write-Host "✓ Python version is compatible" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
    $recreate = Read-Host "Do you want to recreate it? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✓ Virtual environment recreated" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Choose dependency set to install:" -ForegroundColor Cyan
Write-Host "1) Old dependencies (requirements.txt) - for baseline testing"
Write-Host "2) New dependencies (requirements-new.txt) - upgraded versions"
Write-Host "3) Both (install old first, then new in separate environments)"
$choice = Read-Host "Enter choice (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Installing OLD dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        Write-Host "✓ Old dependencies installed" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "Installing NEW dependencies..." -ForegroundColor Yellow
        pip install -r requirements-new.txt
        Write-Host "✓ New dependencies installed" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "Installing in current environment: NEW dependencies" -ForegroundColor Yellow
        pip install -r requirements-new.txt
        Write-Host "✓ New dependencies installed in current environment" -ForegroundColor Green
        Write-Host ""
        Write-Host "To test old dependencies, run:" -ForegroundColor Cyan
        Write-Host "  deactivate"
        Write-Host "  python -m venv venv-old"
        Write-Host "  .\venv-old\Scripts\Activate.ps1"
        Write-Host "  pip install -r requirements.txt"
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Run Django setup
Write-Host "Setting up Django..." -ForegroundColor Yellow
python manage.py makemigrations sample_app
python manage.py migrate
Write-Host "✓ Django database initialized" -ForegroundColor Green
Write-Host ""

# Create superuser prompt
$createSuperuser = Read-Host "Create Django superuser? (y/N)"
if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
    python manage.py createsuperuser
}
Write-Host ""

# Display package versions
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Installed Package Versions:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
pip list | Select-String -Pattern "(Django|requests|pandas|numpy|scipy|psycopg2|celery|urllib3)"
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run tests: pytest tests\ -v"
Write-Host "  2. Run server: python manage.py runserver"
Write-Host "  3. Run analysis: python dependency_analysis.py"
Write-Host ""
Write-Host "To deactivate virtual environment: deactivate" -ForegroundColor Yellow
Write-Host ""
