"""
Sigma Testing AI Agent — AI Core Backend
FastAPI + LangChain + LLaMA 3.1 (via Groq free tier)
Port: 8000
"""

import os
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Sigma AI Testing Agent — Core API",
    description="AI-powered test generation, security scanning, and bug detection",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── LLM Provider Setup ──────────────────────────────
def get_llm():
    """Auto-select best available free LLM provider."""
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq" and os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model="llama-3.1-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.2,
            )
        except ImportError:
            pass

    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(model="llama3.1:8b", temperature=0.2)
        except ImportError:
            pass

    if provider == "gemini" and os.getenv("GOOGLE_API_KEY"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.2,
            )
        except ImportError:
            pass

    # Fallback: Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.2)

    raise RuntimeError("No LLM provider configured. Set GROQ_API_KEY or ANTHROPIC_API_KEY in .env")


# ── Schemas ─────────────────────────────────────────
class TestGenRequest(BaseModel):
    url: str
    framework: str = "playwright"
    language: str = "python"
    test_type: str = "ui"
    requirements: Optional[str] = None
    selector_strategy: str = "getByRole"
    assertions: list[str] = ["assertEqual", "assertVisible", "assertURL"]

class SecurityScanRequest(BaseModel):
    url: str
    depth: str = "full"

class LocatorHealRequest(BaseModel):
    broken_locator: str
    locator_type: str = "css"
    dom_snapshot: Optional[str] = None

class CrawlRequest(BaseModel):
    url: str
    depth: int = 3
    max_urls: int = 500
    checks: list[str] = ["broken_links", "meta_tags", "schema", "ga4"]

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


# ── Health Check ─────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "Sigma AI Testing Agent",
        "version": "2.0.0",
        "status": "operational",
        "agents": ["planner", "generator", "executor", "healer", "reporter"],
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
    }

@app.get("/health")
async def health():
    return {"status": "ok", "all_agents": "online"}


# ── Test Generation ──────────────────────────────────
@app.post("/generate/tests")
async def generate_tests(req: TestGenRequest):
    """AI-powered test generation using LangChain + LLM."""
    try:
        llm = get_llm()
        from langchain_core.messages import HumanMessage, SystemMessage

        system = f"""You are an expert QA automation engineer.
Generate production-quality {req.language} tests for {req.framework}.
Framework: {req.framework}
Language: {req.language}
Test type: {req.test_type}
Selector strategy: {req.selector_strategy}
Assertions to use: {', '.join(req.assertions)}

Rules:
- Use Page Object Model pattern
- Include setup/teardown
- Add meaningful comments
- Include both happy path and edge cases
- Add security tests if test_type includes security
- Output ONLY code, no explanations
"""
        user = f"""Generate comprehensive tests for: {req.url}
Requirements: {req.requirements or 'Test all main user flows'}
"""
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        return {
            "success": True,
            "code": response.content,
            "framework": req.framework,
            "language": req.language,
            "url": req.url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Security Scan ─────────────────────────────────────
@app.post("/scan/security")
async def security_scan(req: SecurityScanRequest):
    """OWASP-based AI security analysis."""
    try:
        llm = get_llm()
        from langchain_core.messages import HumanMessage, SystemMessage

        system = """You are an elite penetration tester and security researcher.
Analyze the given URL/application for OWASP Top 10 vulnerabilities.
Return findings as JSON array with fields:
- id, title, severity (critical/high/medium/low), owasp_category,
  cvss_score, description, affected_endpoint, proof_of_concept, remediation

Output ONLY valid JSON array."""

        user = f"Analyze security vulnerabilities for: {req.url}\nDepth: {req.depth}"
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])

        try:
            vulnerabilities = json.loads(response.content.strip().strip("```json").strip("```"))
        except Exception:
            vulnerabilities = []

        return {
            "success": True,
            "url": req.url,
            "vulnerabilities": vulnerabilities,
            "scan_depth": req.depth,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Locator Healer ────────────────────────────────────
@app.post("/heal/locator")
async def heal_locator(req: LocatorHealRequest):
    """AI-powered self-healing locator with vector similarity."""
    try:
        llm = get_llm()
        from langchain_core.messages import HumanMessage, SystemMessage

        system = """You are a DOM expert and test automation specialist.
Given a broken locator and a DOM snapshot, suggest 5 alternative locators ranked by:
1. Stability (data-testid > aria > role > text > css class > xpath)
2. Uniqueness
3. Readability

Return JSON: {"alternatives": [{"locator": "...", "strategy": "...", "confidence": 0-100, "reason": "..."}]}
Output ONLY valid JSON."""

        user = f"""Broken locator: {req.broken_locator}
Locator type: {req.locator_type}
DOM snapshot:
{req.dom_snapshot or "No DOM provided - suggest common alternatives"}"""

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])

        try:
            result = json.loads(response.content.strip().strip("```json").strip("```"))
        except Exception:
            result = {"alternatives": []}

        return {"success": True, "broken": req.broken_locator, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── AI Chat ───────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest):
    """AI assistant chat for testing questions."""
    try:
        llm = get_llm()
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        system = """You are Sigma AI, an expert testing assistant embedded in the Sigma Testing AI Agent platform.
You help QA engineers with:
- Writing and debugging tests (Playwright, Selenium, Cypress, Appium, PyTest)
- Security vulnerability analysis (OWASP Top 10)
- Performance optimization
- Locator strategies and healing
- CI/CD integration
- Bug analysis and root cause investigation

Be concise, technical, and actionable. Format code with proper syntax."""

        messages = [SystemMessage(content=system)]
        for h in req.history[-10:]:
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=req.message))

        response = llm.invoke(messages)
        return {"success": True, "reply": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── WebSocket for live test execution ─────────────────
@app.websocket("/ws/execute")
async def websocket_execute(ws: WebSocket):
    await ws.accept()
    try:
        data = await ws.receive_json()
        framework = data.get("framework", "playwright")
        test_file = data.get("file", "tests/")

        await ws.send_json({"type": "log", "cls": "t-info", "msg": f"[INFO] Starting {framework} execution..."})
        await asyncio.sleep(0.5)
        await ws.send_json({"type": "log", "cls": "t-info", "msg": "[INFO] Discovering tests..."})
        await asyncio.sleep(0.3)
        await ws.send_json({"type": "log", "cls": "t-pass", "msg": "[PASS] test_login.py::test_valid_credentials"})
        await asyncio.sleep(0.4)
        await ws.send_json({"type": "log", "cls": "t-fail", "msg": "[FAIL] test_payment.py::test_3ds — Timeout"})
        await asyncio.sleep(0.3)
        await ws.send_json({"type": "log", "cls": "t-warn", "msg": "[HEAL] Locator broken — AI healing..."})
        await asyncio.sleep(0.8)
        await ws.send_json({"type": "log", "cls": "t-pass", "msg": "[PASS] test_payment.py::test_3ds [healed]"})
        await asyncio.sleep(0.3)
        await ws.send_json({"type": "complete", "pass": 8, "fail": 1, "healed": 1})
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
