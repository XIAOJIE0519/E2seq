"""CLI application for E2sc."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import scanpy as sc

from e2sc import E2scAgent
from e2sc.data import initialize_databases
from e2sc.utils import get_config, get_logger, get_security_manager

app = typer.Typer(help="E2sc: Easy to Explore Single-Cell via Agentic RAG")
console = Console()
logger = get_logger(__name__)


@app.command()
def chat(
    data_file: Optional[Path] = typer.Option(None, "--data", "-d", help="Path to h5ad file"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key"),
):
    """Start interactive chat session."""
    console.print(Panel.fit(
        "[bold cyan]E2sc - Single Cell Explorer[/bold cyan]\n"
        "Type your questions about single-cell data analysis.\n"
        "Commands: /load <file>, /stats, /tools, /help, /exit",
        border_style="cyan"
    ))
    
    # Initialize agent
    agent = None
    adata = None
    
    # Load data if provided
    if data_file:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Loading {data_file}...", total=None)
            try:
                adata = sc.read_h5ad(data_file)
                console.print(f"[green]✓[/green] Loaded: {adata.n_obs} cells, {adata.n_vars} genes")
            except Exception as e:
                console.print(f"[red]✗[/red] Error loading data: {e}")
                return
    
    # Initialize agent
    try:
        agent = E2scAgent(adata=adata, llm_provider=provider, api_key=api_key)
        console.print("[green]✓[/green] Agent initialized\n")
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing agent: {e}")
        console.print("Please configure your LLM provider using: e2sc config")
        return
    
    # Chat loop
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                if user_input == "/exit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif user_input == "/help":
                    show_help()
                    continue
                elif user_input == "/stats":
                    show_stats(agent)
                    continue
                elif user_input == "/tools":
                    show_tools(agent)
                    continue
                elif user_input.startswith("/load "):
                    file_path = user_input[6:].strip()
                    try:
                        adata = sc.read_h5ad(file_path)
                        agent.load_data(adata)
                        console.print(f"[green]✓[/green] Loaded: {adata.n_obs} cells, {adata.n_vars} genes")
                    except Exception as e:
                        console.print(f"[red]✗[/red] Error: {e}")
                    continue
                else:
                    console.print("[red]Unknown command[/red]")
                    continue
            
            # Process question
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing...", total=None)
                
                try:
                    response = agent.chat(user_input)
                    
                    # Display response
                    console.print("\n[bold green]E2sc:[/bold green]")
                    console.print(Markdown(response["text"]))
                    
                    # Display plots
                    if response.get("plots"):
                        console.print(f"\n[cyan]Generated {len(response['plots'])} plots[/cyan]")
                        for plot_name, fig in response["plots"]:
                            output_file = f"{plot_name}_plot.html"
                            fig.write_html(output_file)
                            console.print(f"  - Saved: {output_file}")
                    
                    console.print()
                    
                except Exception as e:
                    console.print(f"[red]✗[/red] Error: {e}")
                    logger.error(f"Chat error: {e}", exc_info=True)
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except EOFError:
            break


@app.command()
def web(
    port: int = typer.Option(8501, "--port", "-p", help="Port number"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host address"),
):
    """Compatibility alias for the supported ``python start.py`` launcher."""
    import subprocess

    project_root = Path(__file__).resolve().parents[2]
    start_script = project_root / "start.py"
    if host != "localhost" or port != 8501:
        console.print(
            "[yellow]--host/--port are deprecated here; start.py will ask for "
            "an available port and bind the supported local Web server.[/yellow]"
        )
    console.print(f"[cyan]Delegating to: {sys.executable} {start_script}[/cyan]")

    try:
        subprocess.run([sys.executable, str(start_script)], cwd=str(project_root), check=False)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")


@app.command()
def config(
    provider: Optional[str] = typer.Option(None, help="LLM provider"),
    api_key: Optional[str] = typer.Option(None, help="API key"),
    model: Optional[str] = typer.Option(None, help="Model name"),
):
    """Configure E2sc settings."""
    cfg = get_config()
    security = get_security_manager()
    
    if not any([provider, api_key, model]):
        # Interactive configuration
        console.print("[bold cyan]E2sc Configuration[/bold cyan]\n")
        
        provider = typer.prompt(
            "LLM Provider",
            default=cfg.llm.provider,
            type=typer.Choice(["openai", "anthropic", "deepseek", "ollama"])
        )
        
        if provider != "ollama":
            api_key = typer.prompt("API Key", hide_input=True)
        
        model = typer.prompt("Model", default=cfg.llm.model)
    
    # Encrypt API key
    if api_key:
        api_key = security.encrypt(api_key)
    
    # Update configuration
    cfg.update_llm(provider, api_key or cfg.llm.api_key, model)
    
    console.print("[green]✓[/green] Configuration saved")


@app.command()
def init_db(
    data_dir: Path = typer.Argument(..., help="Directory containing CSV files"),
):
    """Initialize databases from CSV files."""
    console.print(f"[cyan]Initializing databases from {data_dir}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating databases...", total=None)
        
        try:
            initialize_databases(data_dir)
            console.print("[green]✓[/green] Databases initialized successfully")
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            logger.error(f"Database initialization error: {e}", exc_info=True)


@app.command()
def version():
    """Show version information."""
    from e2sc import __version__
    console.print(f"E2sc version {__version__}")


def show_help():
    """Show help message."""
    help_text = """
# E2sc Commands

## Chat Commands
- `/load <file>` - Load h5ad data file
- `/stats` - Show agent statistics
- `/tools` - Show available tools
- `/help` - Show this help message
- `/exit` - Exit chat session

## Example Questions
- "分析 Enterocytes 细胞的差异基因"
- "对这些基因进行 GO 富集分析"
- "构建蛋白质互作网络并找出 hub 基因"
- "比较 Enterocytes 和 Goblet cells 的差异"

## Tips
- You can ask questions in Chinese or English
- The agent will automatically plan and execute the analysis
- Plots are saved as HTML files in the current directory
"""
    console.print(Markdown(help_text))


def show_stats(agent):
    """Show agent statistics."""
    if agent is None:
        console.print("[yellow]Agent not initialized[/yellow]")
        return
    
    try:
        console.print("\n[bold cyan]📊 Agent Statistics[/bold cyan]\n")
        
        # Memory stats
        memory_stats = agent.get_memory_stats()
        console.print("[bold]💾 Memory:[/bold]")
        console.print(f"  Current Messages: {memory_stats['current_session']['messages']}")
        console.print(f"  Context Items: {memory_stats['current_session']['context_items']}")
        console.print(f"  Total Sessions: {memory_stats['long_term']['total_sessions']}")
        console.print(f"  Success Rate: {memory_stats['long_term']['success_rate']:.1%}")
        
        # State stats
        state_stats = agent.get_state_summary()
        console.print(f"\n[bold]🔄 State:[/bold]")
        console.print(f"  Current State: {state_stats['current_state']}")
        console.print(f"  Tasks Queued: {state_stats['tasks_queued']}")
        console.print(f"  Checkpoints: {state_stats['checkpoints_created']}")
        
        # Error stats
        error_stats = agent.get_error_stats()
        console.print(f"\n[bold]⚠️ Errors:[/bold]")
        console.print(f"  Total Errors: {error_stats['total_errors']}")
        console.print(f"  Recovered: {error_stats['recovered_errors']}")
        if error_stats['total_errors'] > 0:
            recovery_rate = error_stats['recovered_errors'] / error_stats['total_errors']
            console.print(f"  Recovery Rate: {recovery_rate:.1%}")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error getting stats: {e}[/red]")


def show_tools(agent):
    """Show available tools."""
    if agent is None:
        console.print("[yellow]Agent not initialized[/yellow]")
        return
    
    try:
        console.print("\n[bold cyan]🔧 Available Tools[/bold cyan]\n")
        
        tools_summary = agent.tool_registry.get_tools_summary()
        console.print(f"Total Tools: {tools_summary['total_tools']}\n")
        
        # List all tools
        for tool_name in agent.tool_registry.get_tool_names():
            tool = agent.tool_registry.tools[tool_name]
            console.print(f"[bold green]•[/bold green] {tool_name}")
            console.print(f"  {tool.description}")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error getting tools: {e}[/red]")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
