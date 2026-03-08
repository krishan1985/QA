#!/bin/bash
# Sigma AI Testing Agent — Start All Services
set -e
CYAN='\033[0;36m'; GREEN='\033[0;32m'; NC='\033[0m'

echo -e "${CYAN}Starting Sigma AI Testing Agent...${NC}"

# Activate venv if present
[ -f "venv/bin/activate" ] && source venv/bin/activate

# Start AI Core API (port 8000)
echo -e "${GREEN}▶ Starting AI Core API (port 8000)...${NC}"
cd backend/ai_core && uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Start Frontend (port 3000) if it exists
if [ -d "../../frontend" ] && [ -f "../../frontend/package.json" ]; then
    echo -e "${GREEN}▶ Starting Next.js Frontend (port 3000)...${NC}"
    cd ../../frontend && npm run dev &
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Σ SIGMA AGENT RUNNING!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Dashboard:  http://localhost:3000"
echo -e "  API Docs:   http://localhost:8000/docs"
echo -e "  Standalone: open dashboard.html"
echo ""
echo -e "Press Ctrl+C to stop all services."
wait
