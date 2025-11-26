#!/bin/bash
# Cross-platform setup script for Unix-like systems (Linux/macOS)
# Sets up Python environment and installs dependencies

set -e  # Exit on error

echo "================================"
echo "Dependency Modernization Setup"
echo "Platform: Linux/macOS"
echo "================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    OS="Unknown"
fi

echo "Detected OS: $OS"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Check if Python version is 3.8+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Virtual environment recreated"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Choose dependency set to install:"
echo "1) Old dependencies (requirements.txt) - for baseline testing"
echo "2) New dependencies (requirements-new.txt) - upgraded versions"
echo "3) Both (install old first, then new in separate environments)"
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "Installing OLD dependencies..."
        pip install -r requirements.txt
        echo "✓ Old dependencies installed"
        ;;
    2)
        echo ""
        echo "Installing NEW dependencies..."
        pip install -r requirements-new.txt
        echo "✓ New dependencies installed"
        ;;
    3)
        echo ""
        echo "Installing in current environment: NEW dependencies"
        pip install -r requirements-new.txt
        echo "✓ New dependencies installed in current environment"
        echo ""
        echo "To test old dependencies, run:"
        echo "  deactivate"
        echo "  python3 -m venv venv-old"
        echo "  source venv-old/bin/activate"
        echo "  pip install -r requirements.txt"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
echo ""

# Run Django setup
echo "Setting up Django..."
python manage.py makemigrations sample_app
python manage.py migrate
echo "✓ Django database initialized"
echo ""

# Create superuser prompt
echo "Create Django superuser? (y/N): "
read create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi
echo ""

# Display package versions
echo "================================"
echo "Installed Package Versions:"
echo "================================"
pip list | grep -E "(Django|requests|pandas|numpy|scipy|psycopg2|celery|urllib3)"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run tests: pytest tests/ -v"
echo "  2. Run server: python manage.py runserver"
echo "  3. Run analysis: python dependency_analysis.py"
echo ""
echo "To deactivate virtual environment: deactivate"
echo ""
