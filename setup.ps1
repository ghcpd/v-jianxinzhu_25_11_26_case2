#
# Python Dependency Modernization - Setup Script (Windows - PowerShell)
# 
# This script sets up the modernized Python environment with upgraded dependencies.
# Supports: Windows 10+
# Python: 3.9+
# PowerShell: 5.1+
#
# Usage:
#   .\setup.ps1                    # Interactive setup
#   .\setup.ps1 -NoVenv           # Install globally (not recommended)
#   .\setup.ps1 -Upgrade          # Upgrade existing environment
#
# Note: You may need to run:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#

param(
    [switch]$NoVenv = $false,
    [switch]$Upgrade = $false,
    [switch]$Help = $false
)

# Script configuration
$ProjectName = "python-modernization"
$VenvDir = "venv"
$RequirementsFile = "requirements-updated.txt"
$PythonMinVersion = "3.9"

# Colors and formatting
function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host ("═" * 55) -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host ("═" * 55) -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host @"
Python Dependency Modernization - Windows Setup Script

Usage:
  .\setup.ps1 [OPTIONS]

Options:
  -NoVenv      Install globally (not recommended)
  -Upgrade     Create new environment alongside existing one
  -Help        Show this help message

Examples:
  .\setup.ps1                    # Standard setup with virtual environment
  .\setup.ps1 -NoVenv           # Install to global Python
  .\setup.ps1 -Upgrade          # Create timestamped backup environment

"@
}

function Test-PythonInstalled {
    Write-Header "Checking Python Installation"
    
    try {
        $version = python --version 2>&1
        Write-Success "Found: $version"
        return $true
    }
    catch {
        Write-Error-Custom "Python not found. Please install Python 3.9 or higher."
        Write-Host "Download from: https://www.python.org/downloads/"
        return $false
    }
}

function Test-PythonVersion {
    Write-Header "Verifying Python Version"
    
    $output = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
    $version = $output -join ""
    
    Write-Host "Python version: $version"
    
    # Check if version is >= 3.9
    $major, $minor = $version -split "\."
    if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 9)) {
        Write-Error-Custom "Python $version is older than required $PythonMinVersion"
        return $false
    }
    
    Write-Success "Python version meets requirements"
    return $true
}

function Test-SystemDependencies {
    Write-Header "Checking System Dependencies"
    
    # Check for pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Success "pip is available: $pipVersion"
    }
    catch {
        Write-Error-Custom "pip is not available"
        return $false
    }
    
    # Check for git (optional but helpful)
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gitVersion = git --version 2>&1
        Write-Success "git is available: $gitVersion"
    }
    else {
        Write-Warning "git not found (optional, but recommended)"
    }
    
    return $true
}

function New-VirtualEnvironment {
    Write-Header "Creating Virtual Environment"
    
    if (Test-Path $VenvDir) {
        Write-Warning "Virtual environment already exists at $VenvDir"
        $response = Read-Host "Delete and recreate? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item -Recurse -Force $VenvDir
            Write-Success "Deleted existing environment"
        }
        else {
            Write-Success "Using existing environment"
            return
        }
    }
    
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create virtual environment"
        return $false
    }
    
    Write-Success "Virtual environment created at $VenvDir"
    return $true
}

function Invoke-VirtualEnvironment {
    Write-Header "Activating Virtual Environment"
    
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error-Custom "Activation script not found: $activateScript"
        return $false
    }
    
    & $activateScript
    Write-Success "Virtual environment activated"
    return $true
}

function Update-Pip {
    Write-Header "Upgrading pip, setuptools, and wheel"
    
    python -m pip install --upgrade pip setuptools wheel
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to upgrade pip"
        return $false
    }
    
    Write-Success "pip, setuptools, and wheel upgraded"
    return $true
}

function Install-Requirements {
    Write-Header "Installing Dependencies"
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Error-Custom "Requirements file not found: $RequirementsFile"
        return $false
    }
    
    Write-Host "Installing packages from $RequirementsFile..."
    python -m pip install -r $RequirementsFile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to install dependencies"
        return $false
    }
    
    Write-Success "All dependencies installed successfully"
    return $true
}

function Verify-Installation {
    Write-Header "Verifying Installation"
    
    $pythonScript = @"
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

print('Installed packages:')
for display_name, module_name in packages.items():
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f'  ✓ {display_name}: {version}')
    except ImportError as e:
        print(f'  ✗ {display_name}: NOT FOUND')
        sys.exit(1)

print()
print(f'Python version: {sys.version}')
"@
    
    python -c $pythonScript
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Verification failed"
        return $false
    }
    
    Write-Success "All packages verified"
    return $true
}

function Invoke-RegressionTests {
    Write-Header "Running Regression Tests"
    
    if (-not (Test-Path "test_regression_suite.py")) {
        Write-Warning "test_regression_suite.py not found. Skipping tests."
        return $true
    }
    
    Write-Host "Running regression test suite..."
    python -m pytest test_regression_suite.py -v --tb=short
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Some tests failed. Review the output above."
        return $false
    }
    
    Write-Success "Regression tests completed"
    return $true
}

function Show-NextSteps {
    Write-Header "Setup Complete!"
    
    Write-Host "Your Python environment has been modernized with the following upgrades:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Django:        2.1.5  →  4.2.8   (LTS, all CVEs patched)"
    Write-Host "  requests:      2.20.0 →  2.32.3  (Security updates)"
    Write-Host "  pandas:        0.25.3 →  2.2.0   (API modernization)"
    Write-Host "  numpy:         1.16.2 →  1.26.3  (Buffer overflow fixes)"
    Write-Host "  scipy:         1.2.1  →  1.13.0  (Algorithm improvements)"
    Write-Host "  psycopg2:      2.7.6  →  2.9.9   (Auth/SQL injection fixes)"
    Write-Host "  celery:        4.2.1  →  5.3.4   (Security & async support)"
    Write-Host "  urllib3:       1.24.2 →  2.1.0   (HTTP/2, CVE fixes)"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Activate the virtual environment:"
    Write-Host "   .\$VenvDir\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "2. Review breaking changes:"
    Write-Host "   notepad UPGRADE_RATIONALE.md"
    Write-Host ""
    Write-Host "3. Update your application code for breaking changes:"
    Write-Host "   - pandas: Use pd.concat() instead of .append()"
    Write-Host "   - celery: Update task decorators and configuration"
    Write-Host "   - Django: Update admin interface and middleware"
    Write-Host ""
    Write-Host "4. Run your application tests:"
    Write-Host "   python -m pytest"
    Write-Host ""
    Write-Host "5. Deploy to production with care"
    Write-Host ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Header "Python Dependency Modernization - Windows (PowerShell) Setup"

if ($Help) {
    Show-Help
    exit 0
}

# Handle timestamp for upgrade mode
if ($Upgrade) {
    $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $VenvDir = "${VenvDir}_backup_${timestamp}"
    Write-Warning "Creating new environment at: $VenvDir"
}

# Execute setup steps
if (-not (Test-PythonInstalled)) { exit 1 }
if (-not (Test-PythonVersion)) { exit 1 }
if (-not (Test-SystemDependencies)) { exit 1 }

if (-not $NoVenv) {
    if (-not (New-VirtualEnvironment)) { exit 1 }
    if (-not (Invoke-VirtualEnvironment)) { exit 1 }
}
else {
    Write-Warning "Installing globally. This is not recommended."
    $response = Read-Host "Continue? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        exit 1
    }
}

if (-not (Update-Pip)) { exit 1 }
if (-not (Install-Requirements)) { exit 1 }
if (-not (Verify-Installation)) { exit 1 }

# Optional: Run tests
$runTests = Read-Host "Run regression tests now? (y/N)"
if ($runTests -eq 'y' -or $runTests -eq 'Y') {
    if (-not (Invoke-RegressionTests)) {
        Write-Warning "Tests failed, but setup is complete"
    }
}

Show-NextSteps

Write-Success "Setup completed successfully!"
