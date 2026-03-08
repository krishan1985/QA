#!/bin/bash
# ⚡ SIGMA Testing AI Agent — Master Setup Script
# Run: chmod +x scripts/setup.sh && ./scripts/setup.sh

set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo "${CYAN}⚡ SIGMA TESTING AI AGENT — Setup${NC}"
echo "=================================="
echo ""

# Python venv
echo "${GREEN}[1/6] Creating Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q

echo "${GREEN}[2/6] Installing Python dependencies...${NC}"
pip install -r backend/requirements.txt -q

echo "${GREEN}[3/6] Installing Playwright browsers...${NC}"
playwright install chromium firefox --with-deps

echo "${GREEN}[4/6] Setting up environment variables...${NC}"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "${YELLOW}  ⚠ Created .env — Add your API keys!${NC}"
fi

echo "${GREEN}[5/6] Installing CLI...${NC}"
pip install typer rich httpx -q
chmod +x cli/sigma_cli.py

echo "${GREEN}[6/6] Checking Node.js for frontend...${NC}"
if command -v node &>/dev/null; then
  echo "  Node.js: $(node --version)"
else
  echo "${YELLOW}  ⚠ Node.js not found. Install from nodejs.org for full frontend.${NC}"
fi

echo ""
echo "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "${CYAN}Next steps:${NC}"
echo "  1. Edit .env → Add GROQ_API_KEY (FREE at console.groq.com)"
echo "  2. Run: ./scripts/start.sh"
echo "  3. Open: http://localhost:8000/docs"
echo ""
echo "${YELLOW}FREE LLM options:${NC}"
echo "  • Groq (LLaMA 3.1): console.groq.com (instant, no credit card)"
echo "  • Ollama (local): ollama.ai → ollama pull llama3.1"
echo "  • Google Gemini: aistudio.google.com/app/apikey"
echo ""
