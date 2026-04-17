#!/bin/bash
# JARVIS + Chief of Staff Quick Launch Script
# Run from jarvis directory: bash launch.sh

set -e

echo "🤖 JARVIS + Chief of Staff System"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check Node
echo -e "${BLUE}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION}${NC}"

# Check Anthropic API key
echo -e "${BLUE}Checking Anthropic API key...${NC}"
if [ -z "$ANTHROPIC_API_KEY" ] && ! grep -q "ANTHROPIC_API_KEY" backend/.env 2>/dev/null; then
    echo -e "${YELLOW}⚠ ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Please set your API key:"
    echo ""
    echo "  Option 1 - Environment variable:"
    echo "    export ANTHROPIC_API_KEY=sk-..."
    echo "    bash launch.sh"
    echo ""
    echo "  Option 2 - .env file:"
    echo "    cp backend/.env.example backend/.env"
    echo "    Edit backend/.env with your key"
    echo "    bash launch.sh"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ API key configured${NC}"

# Setup backend
echo ""
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if needed
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> .env
    fi
fi

echo -e "${GREEN}✓ Backend ready${NC}"
cd ..

# Setup frontend
echo ""
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing JavaScript dependencies..."
    npm install -q
fi

echo -e "${GREEN}✓ Frontend ready${NC}"
cd ..

# Create vault structure
echo ""
echo -e "${BLUE}Creating vault structure...${NC}"
mkdir -p ~/.openclaw/workspace/{vault,memory,vault/decisions,vault/patterns}
echo -e "${GREEN}✓ Vault ready${NC}"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ System ready to launch${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To start the system, open 2 terminals and run:"
echo ""
echo -e "${BLUE}Terminal 1 (Backend):${NC}"
echo "  cd jarvis/backend"
echo "  source venv/bin/activate"
echo "  python server.py"
echo ""
echo -e "${BLUE}Terminal 2 (Frontend):${NC}"
echo "  cd jarvis/frontend"
echo "  npm run dev"
echo ""
echo "Then open browser to:"
echo -e "${BLUE}  http://localhost:5173${NC}"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
echo -e "${YELLOW}Docs:${NC}"
echo "  Quick Start:    docs/SETUP.md"
echo "  Architecture:   docs/ARCHITECTURE.md"
echo "  Full README:    README.md"
echo ""
