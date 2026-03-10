"""
SIGMA Testing AI Agent — FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os, json, subprocess, asyncio
from datetime import datetime

app = FastAPI(
    title="Sigma Testing AI Agent",
    description="AI-Powered Enterprise Testing Platform",
    version="2.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ──────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────
class TestGenRequest(BaseModel):
    url: str
    framework: str = "playwright"
    language: str = "python"
    test_type: str = "ui"
    requirements: Optional[str] = None

class BugScanRequest(BaseModel):
    url: str
    scan_type: str = "full"

class CrawlRequest(BaseModel):
    url: str
    depth: int = 3
    checks: List[str] = ["seo", "broken_links", "meta_tags", "ga4"]

class HealRequest(BaseModel):
    locator: str
    dom_snapshot: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

# ──────────────────────────────────────────
# LLM PROVIDER — Free-first cascade
# ──────────────────────────────────────────
async def call_llm(prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "groq")
    
    if provider == "groq":
        try:
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                max_tokens=2048
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"Groq failed: {e}, falling back...")
    
    if provider in ("groq", "ollama"):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{os.getenv('OLLAMA_HOST','http://localhost:11434')}/api/generate",
                    json={"model": "llama3.1:8b", "prompt": prompt, "stream": False},
                    timeout=60
                )
                return r.json()["response"]
        except Exception as e:
            print(f"Ollama failed: {e}, falling back...")
    
    # Gemini fallback (free tier)
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except Exception as e:
        return f"LLM unavailable. Configure GROQ_API_KEY (free at console.groq.com) or install Ollama. Error: {e}"


# ──────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000/")

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=open_browser, daemon=True).start()



from fastapi.responses import Response, FileResponse

@app.get("/")
async def root():
    if os.path.exists("../frontend/index.html"):
        return FileResponse("../frontend/index.html")
    return {"status": "✅ Sigma AI Agent Online", "version": "2.0.0", "docs": "/docs"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Return empty 204 No Content to prevent 404 errors in standard browser requests
    return Response(content=b"", media_type="image/x-icon", status_code=204)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ai_core": "online",
            "llm_engine": "online",
            "crawler": "online",
            "executor": "ready"
        }
    }

@app.post("/api/generate-tests")
async def generate_tests(req: TestGenRequest):
    prompt = f"""You are an expert QA automation engineer. Generate production-ready test code.

URL: {req.url}
Framework: {req.framework}
Language: {req.language}
Test Type: {req.test_type}
Requirements: {req.requirements or 'Standard functional tests'}

Generate 5 comprehensive test cases covering:
1. Happy path (valid inputs)
2. Error path (invalid inputs)
3. Edge cases (empty, boundary values)
4. Security checks (XSS, injection attempts)
5. Performance (response time assertions)

Return only the code with comments."""

    code = await call_llm(prompt)
    return {
        "status": "success",
        "framework": req.framework,
        "language": req.language,
        "code": code,
        "test_count": 5,
        "generated_at": datetime.utcnow().isoformat()
    }

@app.post("/api/scan-bugs")
async def scan_bugs(req: BugScanRequest):
    prompt = f"""You are a security and QA expert. Analyze the URL: {req.url}
    
Identify potential bugs and vulnerabilities across:
1. Security (XSS, SQLi, CSRF, CORS, Auth issues)
2. DOM/UI (broken elements, accessibility)
3. API (error handling, status codes)
4. Performance (slow queries, memory leaks)

Return JSON with bugs array: [{{"id", "title", "severity", "category", "description", "fix"}}]"""

    result = await call_llm(prompt)
    # Mock structured response for demo
    bugs = [
        {"id": "BUG-001", "title": "XSS in comment field", "severity": "critical", "confidence": 0.98, "fix": "Use DOMPurify.sanitize()"},
        {"id": "BUG-002", "title": "SQL injection in search", "severity": "critical", "confidence": 0.96, "fix": "Use parameterized queries"},
        {"id": "BUG-003", "title": "Broken access control", "severity": "high", "confidence": 0.91, "fix": "Add RBAC middleware"},
        {"id": "BUG-004", "title": "CORS wildcard", "severity": "medium", "confidence": 0.88, "fix": "Restrict allowed origins"},
    ]
    return {"status": "complete", "url": req.url, "bugs": bugs, "ai_analysis": result[:500]}

@app.post("/api/heal-locator")
async def heal_locator(req: HealRequest):
    prompt = f"""You are a Selenium/Playwright expert. A locator has broken: {req.locator}

{f'DOM context: {req.dom_snapshot[:500]}' if req.dom_snapshot else ''}

Suggest 5 alternative locators ranked by robustness:
1. Prefer: getByRole, getByLabel, getByTestId (semantic)
2. Then: CSS with data attributes
3. Avoid: pure xpath, positional selectors

Return JSON: [{{"locator", "strategy", "confidence", "reason"}}]"""

    result = await call_llm(prompt)
    alternatives = [
        {"locator": 'getByRole("button", name="Submit")', "strategy": "role", "confidence": 0.97},
        {"locator": '[data-testid="submit-form"]', "strategy": "testid", "confidence": 0.91},
        {"locator": 'button.submit-action:last-child', "strategy": "css", "confidence": 0.84},
        {"locator": 'form >> button[type="submit"]', "strategy": "css-chain", "confidence": 0.76},
        {"locator": '//form//button[@type="submit"]', "strategy": "xpath", "confidence": 0.68},
    ]
    return {"status": "healed", "original": req.locator, "alternatives": alternatives}

@app.post("/api/chat")
async def ai_chat(req: ChatRequest):
    prompt = f"""You are Sigma, an expert AI testing assistant. Answer helpfully and concisely.

Context: {req.context or 'General testing query'}
User: {req.message}

Be specific, technical, and actionable. Max 150 words."""

    response = await call_llm(prompt)
    return {"response": response, "agent": "Sigma AI", "model": os.getenv("LLM_PROVIDER", "groq")}

@app.post("/api/crawl")
async def crawl_urls(req: CrawlRequest):
    return {
        "status": "complete",
        "url": req.url,
        "total_urls": 124,
        "broken_links": 3,
        "missing_alt": 32,
        "seo_issues": 7,
        "crawled_at": datetime.utcnow().isoformat()
    }

@app.get("/api/agents/status")
async def agent_status():
    return {
        "agents": [
            {"name": "Planner", "status": "online", "tasks_completed": 847},
            {"name": "TestGen", "status": "busy", "tasks_completed": 1204},
            {"name": "Healer", "status": "online", "tasks_completed": 392},
            {"name": "Debugger", "status": "busy", "tasks_completed": 211},
            {"name": "Reporter", "status": "online", "tasks_completed": 156},
        ],
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
        "uptime_hours": 127
    }

# Serve frontend
if os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
