#!/bin/bash

# OCR Service Setup Verification Script
# Verifies all setup steps are complete

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

echo "=========================================="
echo "OCR Service Setup Verification"
echo "=========================================="
echo ""

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Tesseract
echo "${BLUE}1. Checking Tesseract installation...${NC}"
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -1)
    echo "${GREEN}✓ Tesseract installed: $TESSERACT_VERSION${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Tesseract not found${NC}"
    echo "   Install with: brew install tesseract"
    ((FAILED++))
fi
echo ""

# 2. Check virtual environment
echo "${BLUE}2. Checking virtual environment...${NC}"
if [ -d "venv" ] && [ -f "venv/bin/python3" ]; then
    echo "${GREEN}✓ Virtual environment exists${NC}"
    VENV_PYTHON="venv/bin/python3"
    ((PASSED++))
else
    echo "${YELLOW}⚠ Virtual environment not found${NC}"
    echo "   Create with: python3 -m venv venv"
    VENV_PYTHON="python3"
    ((FAILED++))
fi
echo ""

# 3. Check Python dependencies
echo "${BLUE}3. Checking Python dependencies...${NC}"
if [ -f "$VENV_PYTHON" ]; then
    MISSING_DEPS=0
    
    # Map package names to their Python import names
    declare -A DEP_MAP=(
        ["pytesseract"]="pytesseract"
        ["Pillow"]="PIL"
        ["opencv-python"]="cv2"
        ["numpy"]="numpy"
        ["flask"]="flask"
        ["python-dateutil"]="dateutil"
    )
    
    for pkg_name in pytesseract Pillow opencv-python numpy flask python-dateutil; do
        import_name="${DEP_MAP[$pkg_name]}"
        if $VENV_PYTHON -c "import $import_name" 2>/dev/null; then
            echo "${GREEN}✓ $pkg_name installed${NC}"
        else
            echo "${RED}✗ $pkg_name not found${NC}"
            ((MISSING_DEPS++))
        fi
    done
    
    if [ $MISSING_DEPS -eq 0 ]; then
        ((PASSED++))
    else
        echo "   Install with: source venv/bin/activate && pip install -r requirements_ocr.txt"
        ((FAILED++))
    fi
else
    echo "${YELLOW}⚠ Skipping dependency check (venv not found)${NC}"
fi
echo ""

# 4. Check Laravel configuration
echo "${BLUE}4. Checking Laravel .env configuration...${NC}"
if [ -f ".env" ]; then
    if grep -q "OCR_SERVICE_URL" .env; then
        OCR_URL=$(grep "OCR_SERVICE_URL" .env | cut -d '=' -f2)
        echo "${GREEN}✓ OCR_SERVICE_URL configured: $OCR_URL${NC}"
        ((PASSED++))
    else
        echo "${RED}✗ OCR_SERVICE_URL not found in .env${NC}"
        echo "   Add: OCR_SERVICE_URL=http://127.0.0.1:5000"
        ((FAILED++))
    fi
    
    if grep -q "OCR_SERVICE_TIMEOUT" .env; then
        OCR_TIMEOUT=$(grep "OCR_SERVICE_TIMEOUT" .env | cut -d '=' -f2)
        echo "${GREEN}✓ OCR_SERVICE_TIMEOUT configured: $OCR_TIMEOUT${NC}"
        ((PASSED++))
    else
        echo "${RED}✗ OCR_SERVICE_TIMEOUT not found in .env${NC}"
        echo "   Add: OCR_SERVICE_TIMEOUT=60"
        ((FAILED++))
    fi
else
    echo "${RED}✗ .env file not found${NC}"
    echo "   Create .env file and add OCR service configuration"
    ((FAILED++))
fi
echo ""

# 5. Check .gitignore
echo "${BLUE}5. Checking .gitignore...${NC}"
if [ -f ".gitignore" ]; then
    if grep -qE "^/venv$|^venv$" .gitignore; then
        echo "${GREEN}✓ venv/ is in .gitignore${NC}"
        ((PASSED++))
    else
        echo "${YELLOW}⚠ venv/ not in .gitignore${NC}"
        echo "   Consider adding: /venv"
    fi
else
    echo "${YELLOW}⚠ .gitignore not found${NC}"
fi
echo ""

# 6. Test service startup (optional)
echo "${BLUE}6. Testing service startup (optional)...${NC}"
read -p "Test service startup? This will start the service briefly. (y/n): " test_service

if [ "$test_service" = "y" ] || [ "$test_service" = "Y" ]; then
    if [ -f "$VENV_PYTHON" ]; then
        echo "Starting service..."
        ./ocr_service/run_server.sh > /tmp/ocr_verify.log 2>&1 &
        SERVER_PID=$!
        sleep 3
        
        if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
            HEALTH_RESPONSE=$(curl -s http://127.0.0.1:5000/health)
            echo "${GREEN}✓ Service started successfully${NC}"
            echo "   Health response: $HEALTH_RESPONSE"
            ((PASSED++))
        else
            echo "${RED}✗ Service health check failed${NC}"
            echo "   Check logs: /tmp/ocr_verify.log"
            ((FAILED++))
        fi
        
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        echo "Service stopped"
    else
        echo "${YELLOW}⚠ Skipping service test (venv not found)${NC}"
    fi
else
    echo "Skipping service test"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo "${RED}Failed: $FAILED${NC}"
else
    echo "${GREEN}Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo "${GREEN}✓ All checks passed! OCR service is ready to use.${NC}"
    echo ""
    echo "${BLUE}To start the service:${NC}"
    echo "  ./ocr_service/run_server.sh"
    echo ""
    exit 0
else
    echo "${YELLOW}⚠ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    exit 1
fi
