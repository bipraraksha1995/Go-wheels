#!/bin/bash
# 🔐 Automated Vulnerability Scanning Setup Script
# This script sets up all security scanning tools for GoWheels

set -e

echo "🔍 GoWheels Vulnerability Scanning Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Install pip-audit
echo "📦 Installing pip-audit..."
if pip install pip-audit; then
    echo -e "${GREEN}✓ pip-audit installed${NC}"
else
    echo -e "${RED}✗ Failed to install pip-audit${NC}"
    exit 1
fi
echo ""

# Install Safety
echo "📦 Installing Safety..."
if pip install safety; then
    echo -e "${GREEN}✓ Safety installed${NC}"
else
    echo -e "${RED}✗ Failed to install Safety${NC}"
    exit 1
fi
echo ""

# Install Bandit
echo "📦 Installing Bandit..."
if pip install bandit; then
    echo -e "${GREEN}✓ Bandit installed${NC}"
else
    echo -e "${RED}✗ Failed to install Bandit${NC}"
    exit 1
fi
echo ""

# Install pre-commit
echo "📦 Installing pre-commit..."
if pip install pre-commit; then
    echo -e "${GREEN}✓ pre-commit installed${NC}"
else
    echo -e "${RED}✗ Failed to install pre-commit${NC}"
    exit 1
fi
echo ""

# Install pre-commit hooks
echo "🔌 Setting up pre-commit hooks..."
if pre-commit install; then
    echo -e "${GREEN}✓ pre-commit hooks installed${NC}"
else
    echo -e "${RED}✗ Failed to install pre-commit hooks${NC}"
    exit 1
fi
echo ""

# Create reports directory
echo "📁 Creating reports directory..."
mkdir -p reports
echo -e "${GREEN}✓ reports/ created${NC}"
echo ""

# Run initial scan
echo "🔍 Running initial vulnerability scan..."
echo ""

echo "   Running pip-audit..."
pip-audit > reports/initial-pip-audit.json 2>&1 || true

echo "   Running Safety..."
safety check --json > reports/initial-safety.json 2>&1 || true

echo "   Running Bandit..."
bandit -r gowheels/ -f json > reports/initial-bandit.json 2>&1 || true

echo ""
echo -e "${GREEN}✓ Scans complete${NC}"
echo ""

# Print summary
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 What was installed:"
echo "   • pip-audit (Python dependency scanner)"
echo "   • Safety (Alternative Python scanner)"
echo "   • Bandit (Python security analysis)"
echo "   • pre-commit (Git hook automation)"
echo ""
echo "📊 Initial scan reports saved to:"
echo "   • reports/initial-pip-audit.json"
echo "   • reports/initial-safety.json"
echo "   • reports/initial-bandit.json"
echo ""
echo "🚀 Next steps:"
echo "   1. Review scan reports: ls -la reports/"
echo "   2. Check for vulnerabilities: pip-audit"
echo "   3. Test pre-commit hooks: pre-commit run --all-files"
echo "   4. Read documentation:"
echo "      • VULNERABILITY_SCANNING_GUIDE.md"
echo "      • VULNERABILITY_REMEDIATION.md"
echo ""
echo "🔔 GitHub Actions:"
echo "   • CI/CD pipeline: .github/workflows/security-scan.yml"
echo "   • Runs on: Push, PR, Daily schedule"
echo "   • Results: Artifacts + PR comments"
echo ""
echo "📝 Configuration files:"
echo "   • pyproject.toml (pip-audit config)"
echo "   • .pre-commit-config.yaml (Git hooks)"
echo "   • .github/workflows/security-scan.yml (CI/CD)"
echo ""
