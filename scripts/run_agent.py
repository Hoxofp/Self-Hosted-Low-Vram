"""
AI Agent - Main Entry Point
Self-hosted coding assistant with Qwen + Skills + RAG
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
import typer

console = Console()
app = typer.Typer()


def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║     🤖 AI Agent - Coding Assistant    ║
    ║         Qwen 2.5 + Skills + RAG       ║
    ╚═══════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))


@app.command()
def chat():
    """Start interactive chat mode."""
    print_banner()
    
    if not check_ollama():
        console.print("[red]❌ Ollama is not running![/red]")
        console.print("Start it with: [bold]ollama serve[/bold]")
        raise typer.Exit(1)
    
    console.print("[green]✅ Ollama connected[/green]")
    console.print("[dim]Type 'exit' to quit, 'help' for commands[/dim]\n")
    
    # TODO: Initialize agent with SmolAgents
    # TODO: Load skills
    # TODO: Initialize RAG
    
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            if user_input.lower() == "help":
                console.print("""
[bold]Commands:[/bold]
  exit     - Quit the agent
  help     - Show this help
  skills   - List available skills
  clear    - Clear conversation history
                """)
                continue
            
            # TODO: Process with agent
            console.print(f"[bold green]Agent:[/bold green] [dim](Agent response will appear here)[/dim]\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye! 👋[/yellow]")
            break


@app.command()
def version():
    """Show version info."""
    console.print("AI Agent v0.1.0")
    console.print("Model: Qwen 2.5 Coder 3B")


if __name__ == "__main__":
    app()
