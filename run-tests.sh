#!/bin/bash
# Local test runner script - Same commands as CI/CD

set -e  # Exit on error

echo "========================================="
echo "  Drivee Integration Test Suite"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is active
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
    echo "Consider activating a virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # Linux/Mac"
    echo "  venv\\Scripts\\activate     # Windows"
    echo ""
fi

# Install dependencies
echo "📦 Installing test dependencies..."
pip install -q -r requirements_test.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run linting
echo "🔍 Running ruff linting..."
if ruff check .; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    exit 1
fi
echo ""

# Run type checking
echo "🔍 Running mypy type checking..."
if mypy custom_components/drivee; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${RED}✗ Type checking failed${NC}"
    exit 1
fi
echo ""

# Run tests
echo "🧪 Running tests with coverage..."
if pytest tests/ \
    --cov=custom_components.drivee \
    --cov-report=html \
    --cov-report=term-missing \
    -v; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "========================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo "========================================="
echo ""
echo "Coverage report: htmlcov/index.html"
echo ""
