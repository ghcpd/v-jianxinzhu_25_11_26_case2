#!/bin/bash
#
# Python Dependency Modernization - Setup Script (Linux/macOS)
# 
# This script sets up the modernized Python environment with upgraded dependencies.
# Supports: Linux, macOS
# Python: 3.9+
#
# Usage:
#   ./setup.sh                    # Interactive setup
#   ./setup.sh --no-venv         # Install globally (not recommended)
#   ./setup.sh --upgrade         # Upgrade existing environment
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="python-modernization"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements-updated.txt"
PYTHON_MIN_VERSION="3.9"
USE_VENV=true

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_python_version() {
    print_header "Checking Python Version"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.9 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_success "Found Python $PYTHON_VERSION"
    
    # Check version
    if (( $(echo "$PYTHON_VERSION < $PYTHON_MIN_VERSION" | bc -l) )); then
        print_error "Python $PYTHON_VERSION is older than required $PYTHON_MIN_VERSION"
        exit 1
    fi
}

check_dependencies() {
    print_header "Checking System Dependencies"
    
    # Check for required build tools
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            print_warning "Homebrew not found. Some packages may require manual installation."
        else
            print_success "Homebrew found"
        fi
    else
        # Linux
        if command -v apt-get &> /dev/null; then
            print_success "apt-get package manager found (Debian/Ubuntu)"
        elif command -v yum &> /dev/null; then
            print_success "yum package manager found (RHEL/CentOS)"
        else
            print_warning "Package manager not found. Some packages may require manual installation."
        fi
    fi
}

create_virtual_environment() {
    print_header "Creating Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_success "Deleted existing environment"
        else
            print_success "Using existing environment"
            return
        fi
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

activate_virtual_environment() {
    print_header "Activating Virtual Environment"
    
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    # Verify activation
    VENV_PYTHON=$(python -c 'import sys; print(sys.executable)')
    echo -e "  Python path: $VENV_PYTHON"
}

upgrade_pip() {
    print_header "Upgrading pip, setuptools, and wheel"
    
    python -m pip install --upgrade pip setuptools wheel
    print_success "pip, setuptools, and wheel upgraded"
}

install_requirements() {
    print_header "Installing Dependencies"
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    echo "Installing packages from $REQUIREMENTS_FILE..."
    python -m pip install -r "$REQUIREMENTS_FILE"
    print_success "All dependencies installed successfully"
}

run_verification() {
    print_header "Verifying Installation"
    
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
"
    
    print_success "All packages verified"
}

run_tests() {
    print_header "Running Regression Tests"
    
    if [ -f "test_regression_suite.py" ]; then
        echo "Running regression test suite..."
        python -m pytest test_regression_suite.py -v --tb=short || {
            print_warning "Some tests failed. Review the output above."
            return 1
        }
        print_success "Regression tests completed"
    else
        print_warning "test_regression_suite.py not found. Skipping tests."
    fi
}

show_next_steps() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}Your Python environment has been modernized with the following upgrades:${NC}"
    echo ""
    echo "  Django:        2.1.5  →  4.2.8   (LTS, all CVEs patched)"
    echo "  requests:      2.20.0 →  2.32.3  (Security updates)"
    echo "  pandas:        0.25.3 →  2.2.0   (API modernization)"
    echo "  numpy:         1.16.2 →  1.26.3  (Buffer overflow fixes)"
    echo "  scipy:         1.2.1  →  1.13.0  (Algorithm improvements)"
    echo "  psycopg2:      2.7.6  →  2.9.9   (Auth/SQL injection fixes)"
    echo "  celery:        4.2.1  →  5.3.4   (Security & async support)"
    echo "  urllib3:       1.24.2 →  2.1.0   (HTTP/2, CVE fixes)"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source $VENV_DIR/bin/activate"
    echo ""
    echo "2. Review breaking changes:"
    echo "   cat UPGRADE_RATIONALE.md"
    echo ""
    echo "3. Update your application code for breaking changes:"
    echo "   - pandas: Use pd.concat() instead of .append()"
    echo "   - celery: Update task decorators and configuration"
    echo "   - Django: Update admin interface and middleware"
    echo ""
    echo "4. Run your application tests:"
    echo "   python -m pytest"
    echo ""
    echo "5. Deploy to production with care"
    echo ""
}

cleanup_on_exit() {
    if [ $? -ne 0 ]; then
        print_error "Setup failed. Check the output above for details."
        if [ "$USE_VENV" = true ] && [ -d "$VENV_DIR" ]; then
            print_warning "Virtual environment at $VENV_DIR may be incomplete."
        fi
    fi
}

trap cleanup_on_exit EXIT

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print_header "Python Dependency Modernization - Linux/macOS Setup"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --no-venv)
            USE_VENV=false
            shift
            ;;
        --upgrade)
            VENV_DIR="${VENV_DIR}_upgrade_$(date +%s)"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-venv    Install globally (not recommended)"
            echo "  --upgrade    Create new environment alongside existing one"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $arg"
            exit 1
            ;;
    esac
done

# Execute setup steps
check_python_version
check_dependencies

if [ "$USE_VENV" = true ]; then
    create_virtual_environment
    activate_virtual_environment
else
    print_warning "Installing globally. This is not recommended."
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if ! [[ $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

upgrade_pip
install_requirements
run_verification

# Optional: Run tests
if [ -f "test_regression_suite.py" ]; then
    read -p "Run regression tests now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
fi

show_next_steps

print_success "Setup completed successfully!"
