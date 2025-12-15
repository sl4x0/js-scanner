#!/bin/bash

# JS Scanner - VPS Setup Script
# For Ubuntu/Debian systems

set -e

echo "================================================"
echo "  JS Scanner - VPS Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Running as root. Consider using a regular user.${NC}"
fi

# 2. Check system resources
echo "[*] Checking system resources..."

# Check available memory
available_mem=$(free -m | awk 'NR==2{print $7}')
if [ "$available_mem" -lt 2048 ]; then
    echo -e "${YELLOW}⚠️  Warning: Less than 2GB available RAM. Scanner may have memory issues.${NC}"
fi

# Check disk space
available_space=$(df / | tail -1 | awk '{print $4}')
if [ "$available_space" -lt 10485760 ]; then
    echo -e "${YELLOW}⚠️  Warning: Less than 10GB free disk space.${NC}"
else
    echo -e "${GREEN}✓ Sufficient disk space available${NC}"
fi

# 3. Update system packages
echo ""
echo "[*] Updating system packages..."
sudo apt-get update -qq

# 4. Install Python 3.8+
echo ""
echo "[*] Checking Python installation..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python $python_version found${NC}"
else
    echo "[*] Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# 5. Install system dependencies
echo ""
echo "[*] Installing system dependencies..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

echo -e "${GREEN}✓ System dependencies installed${NC}"

# 6. Create Python virtual environment
echo ""
echo "[*] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# 7. Activate virtual environment and install Python packages
echo ""
echo "[*] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Python packages installed${NC}"

# 8. Install Playwright browsers
echo ""
echo "[*] Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

echo -e "${GREEN}✓ Playwright browsers installed${NC}"

# 9. Install TruffleHog
echo ""
echo "[*] Installing TruffleHog..."

if command -v trufflehog &> /dev/null; then
    echo -e "${GREEN}✓ TruffleHog already installed${NC}"
else
    echo "[*] Downloading TruffleHog..."
    curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
    
    if command -v trufflehog &> /dev/null; then
        echo -e "${GREEN}✓ TruffleHog installed successfully${NC}"
        trufflehog_path="/usr/local/bin/trufflehog"
    else
        echo -e "${RED}✗ TruffleHog installation failed${NC}"
        echo "Please install manually from: https://github.com/trufflesecurity/trufflehog/releases"
    fi
fi

# 10. Create directory structure
echo ""
echo "[*] Creating directory structure..."
mkdir -p results cache logs temp
chmod 700 results cache logs temp

echo -e "${GREEN}✓ Directory structure created${NC}"

# 11. Check config.yaml
echo ""
echo "[*] Checking configuration..."

if [ -f "config.yaml" ]; then
    # Check if Discord webhook is configured
    if grep -q "YOUR_WEBHOOK_URL" config.yaml; then
        echo -e "${YELLOW}⚠️  Warning: Discord webhook not configured!${NC}"
        echo "Please edit config.yaml and add your Discord webhook URL"
    else
        echo -e "${GREEN}✓ Configuration file exists${NC}"
    fi
else
    echo -e "${RED}✗ config.yaml not found${NC}"
fi

# 12. Test installation
echo ""
echo "[*] Testing installation..."

# Test Python imports
python3 -c "
import sys
try:
    import playwright
    import aiohttp
    import yaml
    import jsbeautifier
    print('✓ All Python modules imported successfully')
except ImportError as e:
    print(f'✗ Missing module: {e}')
    sys.exit(1)
"

# 13. Print summary
echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml and add your Discord webhook URL"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run a test scan: python -m jsscanner -t example.com"
echo ""
echo "Useful commands:"
echo "  - Run scan: python -m jsscanner -t <target>"
echo "  - View help: python -m jsscanner --help"
echo "  - Check logs: tail -f results/<target>/logs/scan.log"
echo ""

# 14. Check TruffleHog path for config
if command -v trufflehog &> /dev/null; then
    trufflehog_location=$(which trufflehog)
    echo "TruffleHog location: $trufflehog_location"
    echo "Update config.yaml if needed:"
    echo "  trufflehog_path: \"$trufflehog_location\""
    echo ""
fi

echo -e "${GREEN}Happy hunting! 🎯${NC}"
