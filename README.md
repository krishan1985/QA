# ⚡ SIGMA Testing AI Agent
### The Alpha & Omega of AI-Powered Software Testing

> Break systems before users do. Powered by LLaMA 3.1, LangChain, FastAPI & Playwright.

---

## 🚀 Quick Start (5 minutes)

### Step 1 — Clone & Setup
```bash
git clone https://github.com/yourorg/sigma-testing-agent
cd sigma-testing-agent
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

### Step 2 — Add FREE API Key
```bash
# OPTION A: Groq (FREE LLaMA 3.1 70B) — Recommended
# Get instantly at: https://console.groq.com (no credit card)
echo "GROQ_API_KEY=your_key" >> .env

# OPTION B: 100% FREE Local AI (no internet needed)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1
echo "LLM_PROVIDER=ollama" >> .env

# OPTION C: Google Gemini FREE tier
# Get at: https://aistudio.google.com/app/apikey
echo "GOOGLE_API_KEY=your_key" >> .env
```

### Step 3 — Run
```bash
./scripts/start.sh

# Dashboard:  Open frontend/index.html in browser or VS Code
# API Docs:   http://localhost:8000/docs
# CLI:        python cli/sigma_cli.py status
```

---

## 🎯 In VS Code

1. Open folder: `code sigma-testing-agent`
2. **Run API**: `Ctrl+Shift+P` → `Tasks: Run Task` → `▶ Start Backend API`
3. **Open Dashboard**: Open `frontend/index.html` → Right-click → `Open with Live Server`
4. **Debugger**: `F5` → Select `⚡ Sigma Backend (FastAPI)`

---

## 🖥 CLI Commands

```bash
# Check system health
python cli/sigma_cli.py status

# Generate AI tests
python cli/sigma_cli.py generate --url https://yoursite.com --framework playwright --language python

# Scan for bugs & vulnerabilities
python cli/sigma_cli.py scan --url https://yoursite.com

# Crawl & validate URLs
python cli/sigma_cli.py crawl --url https://yoursite.com --depth 3 --output results.csv

# Heal broken locators
python cli/sigma_cli.py heal --locator "#old-submit-btn"

# Chat with AI
python cli/sigma_cli.py chat "How do I test authentication flows?"

# Run test suite
python cli/sigma_cli.py run --framework playwright --parallel --workers 4
```

---

## 🏗 Architecture

```
sigma-testing-agent/
├── frontend/
│   └── index.html          ← Dashboard (runs in ANY browser)
├── backend/
│   ├── main.py             ← FastAPI + AI Agent Core
│   └── requirements.txt
├── cli/
│   └── sigma_cli.py        ← Full CLI tool
├── scripts/
│   ├── setup.sh            ← One-command setup
│   └── start.sh            ← Start all services
└── .vscode/
    ├── launch.json         ← Debug profiles
    └── tasks.json          ← VS Code tasks
```

---

## 🤖 What Can Sigma Do?

| Feature | Description |
|---------|-------------|
| **Bug Detection** | AI scans DOM, API, security, UX — finds issues before users |
| **Test Generation** | LLM writes Playwright/Selenium/Cypress tests from a URL |
| **Security Scanning** | OWASP Top 10, XSS, SQLi, Auth issues, CORS, CVEs |
| **URL Crawler** | Validates 1000s of URLs for SEO, tracking, broken links |
| **Locator Healing** | AI fixes broken CSS/XPath selectors automatically |
| **AI Debugger** | Paste stack trace → instant root cause + fix |
| **Network Monitor** | Intercepts all requests, detects GTM/GA4/GPT.js |
| **Visual Testing** | Pixel-perfect screenshot comparison |
| **Performance** | k6 load testing, Core Web Vitals, Lighthouse CI |
| **Accessibility** | WCAG 2.1 AA/AAA with axe-core |

---

## 🆓 100% Free to Run

All core AI features work with zero cost:
- **Groq** (LLaMA 3.1 70B): Free tier, instant API key
- **Ollama** (local LLaMA): No internet, no limits, fully private
- **Google Gemini**: Free 15 req/min tier
- **ChromaDB**: Free local vector store
- **sentence-transformers**: Free local embeddings

---

## Competing With

| Tool | Sigma Advantage |
|------|----------------|
| KaneAI | Full source access, free AI, customizable |
| TestRigor | LLM-powered, not just pattern matching |
| Testim | Multi-framework, not locked to one runner |
| Virtuoso | Open source, self-hosted option |
| Tosca | Free to start, Python/JS/Java all supported |

---

*⚡ Sigma — Break systems before users do.*
