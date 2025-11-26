@echo off
REM Cross-platform setup script for Windows (Batch)
REM Sets up Python environment and installs dependencies

echo ================================
echo Dependency Modernization Setup
echo Platform: Windows
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo ✓ Python is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "%recreate%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo ✓ Virtual environment recreated
    )
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo ✓ pip upgraded
echo.

REM Install dependencies
echo Choose dependency set to install:
echo 1) Old dependencies (requirements.txt) - for baseline testing
echo 2) New dependencies (requirements-new.txt) - upgraded versions
echo 3) Install new (recommended)
set /p choice="Enter choice (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo Installing OLD dependencies...
    pip install -r requirements.txt
    echo ✓ Old dependencies installed
) else if "%choice%"=="2" (
    echo.
    echo Installing NEW dependencies...
    pip install -r requirements-new.txt
    echo ✓ New dependencies installed
) else if "%choice%"=="3" (
    echo.
    echo Installing NEW dependencies...
    pip install -r requirements-new.txt
    echo ✓ New dependencies installed
) else (
    echo Invalid choice. Installing new dependencies by default...
    pip install -r requirements-new.txt
)
echo.

REM Run Django setup
echo Setting up Django...
python manage.py makemigrations sample_app
python manage.py migrate
echo ✓ Django database initialized
echo.

REM Display package versions
echo ================================
echo Installed Package Versions:
echo ================================
pip list | findstr /C:"Django" /C:"requests" /C:"pandas" /C:"numpy" /C:"scipy" /C:"psycopg2" /C:"celery" /C:"urllib3"
echo.

echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo   1. Run tests: pytest tests\ -v
echo   2. Run server: python manage.py runserver
echo   3. Run analysis: python dependency_analysis.py
echo.
echo To deactivate virtual environment: deactivate
echo.

pause
