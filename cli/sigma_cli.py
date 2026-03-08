#!/usr/bin/env python3
"""
SIGMA Testing AI Agent — CLI
Usage: python sigma_cli.py [command] [options]
"""
import typer, httpx, json, sys, os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from typing import Optional

app = typer.Typer(name="sigma", help="⚡ Sigma Testing AI Agent CLI")
console = Console()
API_BASE = os.getenv("SIGMA_API", "http://localhost:8000")

def api(method, path, **kwargs):
    try:
        r = httpx.request(method, f"{API_BASE}{path}", timeout=30, **kwargs)
        return r.json()
    except Exception as e:
        rprint(f"[red]✗ API Error: {e}[/red]")
        sys.exit(1)

@app.command()
def status():
    """Check all Sigma services health"""
    rprint("\n[bold cyan]⚡ SIGMA TESTING AI AGENT[/bold cyan]\n")
    try:
        data = api("GET", "/health")
        table = Table(show_header=True)
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        for name, st in data["services"].items():
            color = "green" if st == "online" else "yellow" if st in ("busy","ready") else "red"
            table.add_row(name.replace("_"," ").title(), f"[{color}]● {st.upper()}[/{color}]")
        console.print(table)
        agents = api("GET", "/api/agents/status")
        rprint(f"\n[dim]LLM Provider: [bold cyan]{agents['llm_provider']}[/bold cyan] | Uptime: {agents['uptime_hours']}h[/dim]\n")
    except:
        rprint("[red]✗ Services offline. Run: ./scripts/start.sh[/red]")

@app.command()
def generate(
    url: str = typer.Option(..., "--url", help="Target URL"),
    framework: str = typer.Option("playwright", "--framework", help="Test framework"),
    language: str = typer.Option("python", "--language", help="Language"),
    run: bool = typer.Option(False, "--run", help="Run after generating"),
):
    """Generate AI-powered tests for a URL"""
    rprint(f"\n[bold]🤖 Generating tests for[/bold] [cyan]{url}[/cyan]\n")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as p:
        task = p.add_task("AI analyzing URL...", total=None)
        result = api("POST", "/api/generate-tests", json={"url": url, "framework": framework, "language": language})
        p.update(task, description="[green]✓ Generated!")
    
    panel = Panel(result["code"][:800]+"...", title=f"Generated {framework} Tests ({language})", border_style="cyan")
    console.print(panel)
    rprint(f"\n[green]✓ {result['test_count']} test cases generated[/green]")
    if run:
        rprint("\n[yellow]▶ Running generated tests...[/yellow]")

@app.command()
def scan(
    url: str = typer.Option(..., "--url", help="URL to scan"),
    scan_type: str = typer.Option("full", "--type", help="Scan type"),
):
    """Scan URL for bugs and vulnerabilities"""
    rprint(f"\n[bold red]🔥 Bug scanning:[/bold red] [cyan]{url}[/cyan]\n")
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as p:
        task = p.add_task("Running AI deep scan...", total=None)
        result = api("POST", "/api/scan-bugs", json={"url": url, "scan_type": scan_type})
        p.update(task, description="[green]✓ Scan complete!")

    table = Table(title=f"Bugs Found in {url}", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Severity")
    table.add_column("Confidence")
    table.add_column("Fix")

    for bug in result["bugs"]:
        sev_color = {"critical": "red", "high": "yellow", "medium": "blue", "low": "green"}.get(bug["severity"], "white")
        table.add_row(
            bug["id"], bug["title"],
            f"[{sev_color}]{bug['severity'].upper()}[/{sev_color}]",
            f"{int(bug['confidence']*100)}%",
            bug["fix"]
        )
    console.print(table)

@app.command()
def heal(
    locator: str = typer.Option(..., "--locator", help="Broken locator"),
    dom: Optional[str] = typer.Option(None, "--dom", help="DOM snapshot file"),
):
    """AI-powered locator healing"""
    rprint(f"\n[bold]🔧 Healing locator:[/bold] [red]{locator}[/red]\n")
    dom_content = open(dom).read() if dom and os.path.exists(dom) else None
    result = api("POST", "/api/heal-locator", json={"locator": locator, "dom_snapshot": dom_content})
    
    for i, alt in enumerate(result["alternatives"]):
        color = ["bright_green","green","yellow","cyan","dim"][i] if i < 5 else "dim"
        rprint(f"[{color}]{i+1}. [{int(alt['confidence']*100)}%] {alt['locator']}[/{color}]  [dim]({alt['strategy']})[/dim]")

@app.command()
def crawl(
    url: str = typer.Option(..., "--url", help="URL to crawl"),
    depth: int = typer.Option(3, "--depth", help="Crawl depth"),
    output: Optional[str] = typer.Option(None, "--output", help="Output CSV file"),
):
    """Crawl URLs and validate SEO, links, tracking"""
    rprint(f"\n[bold]🕷 Crawling:[/bold] [cyan]{url}[/cyan] depth={depth}\n")
    result = api("POST", "/api/crawl", json={"url": url, "depth": depth})
    
    rprint(f"[green]✓ Total URLs: {result['total_urls']}[/green]")
    rprint(f"[red]✗ Broken links: {result['broken_links']}[/red]")
    rprint(f"[yellow]⚠ Missing alt text: {result['missing_alt']}[/yellow]")
    rprint(f"[yellow]⚠ SEO issues: {result['seo_issues']}[/yellow]")
    if output:
        rprint(f"\n[dim]Output saved to: {output}[/dim]")

@app.command()
def chat(message: str = typer.Argument(..., help="Message to Sigma AI")):
    """Chat with Sigma AI assistant"""
    result = api("POST", "/api/chat", json={"message": message})
    panel = Panel(result["response"], title=f"[cyan]Σ Sigma AI ({result['model']})[/cyan]", border_style="cyan")
    console.print("\n")
    console.print(panel)

@app.command()
def run(
    framework: str = typer.Option("playwright", "--framework"),
    file: Optional[str] = typer.Option(None, "--file"),
    parallel: bool = typer.Option(False, "--parallel"),
    workers: int = typer.Option(4, "--workers"),
):
    """Execute test suites"""
    rprint(f"\n[bold]▶ Running tests[/bold] [{framework}]\n")
    cmds = {
        "playwright": f"pytest {file or 'tests/'} --browser chromium -v",
        "selenium": f"pytest {file or 'tests/'} -v",
        "cypress": "npx cypress run",
    }
    cmd = cmds.get(framework, f"pytest {file or 'tests/'}")
    if parallel: cmd += f" -n {workers}"
    rprint(f"[dim]$ {cmd}[/dim]\n")
    os.system(cmd)

if __name__ == "__main__":
    app()
