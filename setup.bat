@echo off
REM
REM Python Dependency Modernization - Setup Script (Windows - Batch)
REM
REM This script sets up the modernized Python environment with upgraded dependencies.
REM Supports: Windows 10+ with Command Prompt
REM Python: 3.9+
REM
REM Usage:
REM   setup.bat                    - Interactive setup
REM   setup.bat --no-venv         - Install globally (not recommended)
REM   setup.bat --help            - Show help message
REM

setlocal enabledelayedexpansion

REM Configuration
set "PROJECT_NAME=python-modernization"
set "VENV_DIR=venv"
set "REQUIREMENTS_FILE=requirements-updated.txt"
set "PYTHON_MIN_VERSION=3.9"
set "USE_VENV=1"

REM Parse arguments
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--no-venv" (
    set "USE_VENV=0"
    shift
)

REM ============================================================================
REM MAIN EXECUTION
REM ============================================================================

cls
echo.
echo ========================================================
echo Python Dependency Modernization - Windows Setup
echo ========================================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9 or higher.
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VER=%%i"
echo [OK] Found Python: %PYTHON_VER%
echo.

REM Check pip
echo Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)
echo [OK] pip is available
echo.

REM Create virtual environment if needed
if "%USE_VENV%"=="1" (
    if exist "%VENV_DIR%" (
        echo Virtual environment already exists at: %VENV_DIR%
        set /p "DELETE_VENV=Delete and recreate? (y/N): "
        if /i "!DELETE_VENV!"=="y" (
            echo Deleting existing environment...
            rmdir /s /q "%VENV_DIR%"
        )
    )
    
    if not exist "%VENV_DIR%" (
        echo Creating virtual environment...
        python -m venv "%VENV_DIR%"
        if errorlevel 1 (
            echo ERROR: Failed to create virtual environment
            pause
            exit /b 1
        )
        echo [OK] Virtual environment created
        echo.
    )
    
    REM Activate virtual environment
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
    if errorlevel 1 (
        echo ERROR: Failed to activate virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment activated
    echo.
)

REM Upgrade pip
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo [OK] pip, setuptools, and wheel upgraded
echo.

REM Install requirements
if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: Requirements file not found: %REQUIREMENTS_FILE%
    pause
    exit /b 1
)

echo Installing dependencies from %REQUIREMENTS_FILE%...
python -m pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Verify installation
echo Verifying installation...
python -c "
import sys
packages = {
    'Django': 'django',
    'requests': 'requests',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'scipy': 'scipy',
    'psycopg2': 'psycopg2',
    'celery': 'celery',
    'urllib3': 'urllib3',
}

all_ok = True
print('Installed packages:')
for display_name, module_name in packages.items():
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f'  [OK] {display_name}: {version}')
    except ImportError:
        print(f'  [ERR] {display_name}: NOT FOUND')
        all_ok = False

if not all_ok:
    sys.exit(1)
"

if errorlevel 1 (
    echo ERROR: Verification failed
    pause
    exit /b 1
)
echo [OK] All packages verified
echo.

REM Optional: Run tests
set /p "RUN_TESTS=Run regression tests? (y/N): "
if /i "!RUN_TESTS!"=="y" (
    if exist "test_regression_suite.py" (
        echo Running regression tests...
        python -m pytest test_regression_suite.py -v --tb=short
        if errorlevel 1 (
            echo WARNING: Some tests failed
        ) else (
            echo [OK] Regression tests passed
        )
    ) else (
        echo WARNING: test_regression_suite.py not found
    )
    echo.
)

REM Show next steps
cls
echo.
echo ========================================================
echo Setup Complete!
echo ========================================================
echo.
echo Your Python environment has been modernized with the following upgrades:
echo.
echo   Django:        2.1.5  -^>  4.2.8   (LTS, all CVEs patched)
echo   requests:      2.20.0 -^>  2.32.3  (Security updates)
echo   pandas:        0.25.3 -^>  2.2.0   (API modernization)
echo   numpy:         1.16.2 -^>  1.26.3  (Buffer overflow fixes)
echo   scipy:         1.2.1  -^>  1.13.0  (Algorithm improvements)
echo   psycopg2:      2.7.6  -^>  2.9.9   (Auth/SQL injection fixes)
echo   celery:        4.2.1  -^>  5.3.4   (Security ^& async support)
echo   urllib3:       1.24.2 -^>  2.1.0   (HTTP/2, CVE fixes)
echo.
echo NEXT STEPS:
echo.
echo 1. Activate the virtual environment (if not already active):
echo    .\%VENV_DIR%\Scripts\activate.bat
echo.
echo 2. Review breaking changes:
echo    notepad UPGRADE_RATIONALE.md
echo.
echo 3. Update your application code for breaking changes:
echo    - pandas: Use pd.concat() instead of .append()
echo    - celery: Update task decorators and configuration
echo    - Django: Update admin interface and middleware
echo.
echo 4. Run your application tests:
echo    python -m pytest
echo.
echo 5. Deploy to production with care
echo.
pause
exit /b 0

:show_help
echo.
echo Python Dependency Modernization - Windows Setup
echo.
echo Usage:
echo   setup.bat              Standard setup with virtual environment
echo   setup.bat --no-venv   Install to global Python (not recommended)
echo   setup.bat --help      Show this help message
echo.
pause
exit /b 0
