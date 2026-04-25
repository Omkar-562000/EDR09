#!/bin/bash
# EDR System Setup Script for Linux/macOS
# ========================================
# 
# This script automates the setup of the EDR system on Linux/macOS.
# It creates a virtual environment, installs dependencies, and configures the system.
#
# Usage: ./setup.sh [options]
#   --frontend    Also install frontend dependencies (requires Node.js)
#   --help        Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
INSTALL_FRONTEND=false

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    cat << 'EOF'
EDR System Setup Script

Usage: ./setup.sh [options]

Options:
  --frontend    Also install frontend dependencies (requires Node.js)
  --help        Show this help message

Examples:
  ./setup.sh                # Setup backend only
  ./setup.sh --frontend     # Setup backend and frontend

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend)
            INSTALL_FRONTEND=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check Python version
print_header "Checking Python Version"
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found. Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Create virtual environment
print_header "Setting Up Virtual Environment"
if [ ! -d "$VENV_DIR" ]; then
    print_success "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_success "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_header "Upgrading pip, setuptools, and wheel"
pip install --upgrade pip setuptools wheel

# Install backend dependencies
print_header "Installing Backend Dependencies"
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt"
    print_success "Backend dependencies installed"
else
    print_error "requirements.txt not found in $BACKEND_DIR"
    exit 1
fi

# Check and validate configuration
print_header "Validating Configuration"
if [ -f "$BACKEND_DIR/config/settings.json" ]; then
    print_success "settings.json found"
else
    print_error "settings.json not found"
    exit 1
fi

if [ -f "$BACKEND_DIR/config/rules.json" ]; then
    print_success "rules.json found"
else
    print_error "rules.json not found"
    exit 1
fi

# Install frontend dependencies if requested
if [ "$INSTALL_FRONTEND" = true ]; then
    print_header "Installing Frontend Dependencies"
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js 20+ to setup frontend."
        print_warning "You can still run the backend: python main.py"
    elif ! command -v npm &> /dev/null; then
        print_error "npm not found. Please install npm to setup frontend."
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        
        if [ -f "$FRONTEND_DIR/package.json" ]; then
            cd "$FRONTEND_DIR"
            npm install
            cd "$PROJECT_ROOT"
            print_success "Frontend dependencies installed"
        else
            print_error "package.json not found in $FRONTEND_DIR"
        fi
    fi
fi

# Set session secret if not already set
print_header "Configuration"
if [ -z "$EDR_SESSION_SECRET" ]; then
    print_warning "EDR_SESSION_SECRET not set. Using default (INSECURE for production!)"
    print_warning "To set a secure secret, run:"
    echo "  export EDR_SESSION_SECRET='$(openssl rand -hex 32)'"
fi

# Print next steps
print_header "Setup Complete!"
print_success "EDR system is ready to run"
echo ""
echo "Next steps:"
echo ""
echo "1. (Optional) Set session secret for production:"
echo "   export EDR_SESSION_SECRET='$(openssl rand -hex 32)'"
echo ""
echo "2. Start the EDR system:"

if [ "$INSTALL_FRONTEND" = true ]; then
    echo "   python main.py --frontend"
else
    echo "   python main.py"
fi

echo ""
echo "3. Access the API:"
echo "   Backend: http://127.0.0.1:8000"
echo "   Docs: http://127.0.0.1:8000/docs"

if [ "$INSTALL_FRONTEND" = true ]; then
    echo ""
    echo "4. Access the frontend:"
    echo "   Frontend: http://localhost:5173"
fi

echo ""
echo "Default credentials:"
echo "   Email: admin@edr.local"
echo "   Password: SecurePassword123!"
echo ""
