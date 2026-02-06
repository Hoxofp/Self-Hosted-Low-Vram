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
from rich.markdown import Markdown
import typer

from agent.smol_agent import SmolAgent, Tool
from agent.core import OllamaClient
from memory.memory import ConversationMemory

console = Console()
app = typer.Typer()

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


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


# Built-in tools
def python_exec(code: str) -> str:
    """Execute Python code."""
    import subprocess
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output or "Code executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (30s limit)"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def read_file(path: str) -> str:
    """Read file contents."""
    try:
        return Path(path).read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding='utf-8')
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_files(directory: str = ".") -> str:
    """List files in directory."""
    try:
        files = list(Path(directory).iterdir())
        return "\n".join([f"{'[DIR]' if f.is_dir() else '[FILE]'} {f.name}" for f in files])
    except Exception as e:
        return f"Error: {e}"


def create_agent() -> SmolAgent:
    """Create agent with tools."""
    agent = SmolAgent(model="qwen2.5-coder:7b-instruct-q4_K_M")
    
    # Register tools
    agent.register_tool(Tool(
        name="python_exec",
        description="Execute Python code and return the output",
        parameters={"code": {"type": "string", "description": "Python code to execute"}},
        function=python_exec
    ))
    
    agent.register_tool(Tool(
        name="read_file",
        description="Read contents of a file",
        parameters={"path": {"type": "string", "description": "Path to file"}},
        function=read_file
    ))
    
    agent.register_tool(Tool(
        name="write_file",
        description="Write content to a file",
        parameters={
            "path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to write"}
        },
        function=write_file
    ))
    
    agent.register_tool(Tool(
        name="list_files",
        description="List files in a directory",
        parameters={"directory": {"type": "string", "description": "Directory path", "default": "."}},
        function=list_files
    ))
    
    return agent


@app.command()
def chat(use_tools: bool = True):
    """Start interactive chat mode."""
    print_banner()
    
    if not check_ollama():
        console.print("[red]❌ Ollama is not running![/red]")
        console.print("Start it with: [bold]ollama serve[/bold]")
        raise typer.Exit(1)
    
    console.print("[green]✅ Ollama connected[/green]")
    
    # Initialize
    agent = create_agent()
    memory = ConversationMemory(persist_path=str(DATA_DIR / "memory.json"))
    
    tools_status = "enabled" if use_tools else "disabled"
    console.print(f"[dim]Tools: {tools_status} | Type 'exit' to quit, 'help' for commands[/dim]\n")
    
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
            
            if not user_input.strip():
                continue
            
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            if user_input.lower() == "help":
                console.print("""
[bold]Commands:[/bold]
  exit     - Quit the agent
  help     - Show this help
  clear    - Clear conversation history
  tools    - List available tools
                """)
                continue
            
            if user_input.lower() == "clear":
                memory.clear()
                console.print("[dim]Conversation cleared.[/dim]")
                continue
            
            if user_input.lower() == "tools":
                console.print("[bold]Available tools:[/bold]")
                for name, tool in agent.tools.items():
                    console.print(f"  • [cyan]{name}[/cyan]: {tool.description}")
                continue
            
            # Process with agent
            memory.add_message("user", user_input)
            
            with console.status("[bold green]Thinking...[/bold green]"):
                if use_tools:
                    response = agent.run(user_input)
                else:
                    response = agent.chat(user_input)
            
            memory.add_message("assistant", response)
            
            # Display response
            console.print(f"\n[bold green]Agent:[/bold green]")
            console.print(Markdown(response))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye! 👋[/yellow]")
            break


@app.command()
def run(prompt: str, use_tools: bool = True):
    """Run a single prompt and exit."""
    if not check_ollama():
        console.print("[red]❌ Ollama is not running![/red]")
        raise typer.Exit(1)
    
    agent = create_agent()
    
    with console.status("[bold green]Processing...[/bold green]"):
        if use_tools:
            response = agent.run(prompt)
        else:
            response = agent.chat(prompt)
    
    console.print(Markdown(response))


@app.command()
def version():
    """Show version info."""
    console.print("AI Agent v0.1.0")
    console.print("Model: Qwen 2.5 Coder 3B")
    console.print("Features: SmolAgent, Tools, Memory")


if __name__ == "__main__":
    app()

