"""CLI application for E2seq."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import scanpy as sc

from e2seq import E2seqAgent
from e2seq.data import initialize_databases
from e2seq.utils import get_config, get_logger, get_security_manager

app = typer.Typer(help="E2seq: Easy to Chat with Sequencing via Agentic RAG / 面向测序分析的智能 RAG 工具")
console = Console()
logger = get_logger(__name__)


@app.command()
def chat(
    data_file: Optional[Path] = typer.Option(None, "--data", "-d", help="Path to h5ad file / h5ad 文件路径"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider / LLM 服务商"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key / API 密钥"),
):
    """Start an interactive chat session / 启动交互式对话。"""
    console.print(Panel.fit(
        "[bold cyan]E2seq - Expression Profile Explorer[/bold cyan]\n"
        "Ask questions about expression-profile or single-cell data / 输入表达谱或单细胞数据问题。\n"
        "Commands / 命令: /load <file>, /stats, /tools, /help, /exit",
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
                console.print(f"[green]OK / 完成[/green] Loaded / 已加载: {adata.n_obs} cells, {adata.n_vars} genes / 个细胞、{adata.n_vars} 个基因")
            except Exception as e:
                console.print(f"[red]ERROR / 错误[/red] Error loading data / 加载数据失败: {e}")
                return

    # Initialize agent
    try:
        agent = E2seqAgent(adata=adata, llm_provider=provider, api_key=api_key)
        console.print("[green]OK / 完成[/green] Agent initialized / Agent 已初始化\n")
    except Exception as e:
        console.print(f"[red]ERROR / 错误[/red] Error initializing agent / Agent 初始化失败: {e}")
        console.print("Configure an LLM provider with `e2seq config` / 使用 `e2seq config` 配置 LLM 服务商")
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
                    console.print("[yellow]Goodbye / 再见![/yellow]")
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
                        console.print(f"[green]OK / 完成[/green] Loaded / 已加载: {adata.n_obs} cells, {adata.n_vars} genes / 个细胞、{adata.n_vars} 个基因")
                    except Exception as e:
                        console.print(f"[red]ERROR / 错误[/red] Error / 失败: {e}")
                    continue
                else:
                    console.print("[red]Unknown command / 未知命令[/red]")
                    continue

            # Process question
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing / 分析中...", total=None)

                try:
                    response = agent.chat(user_input)

                    # Display response
                    console.print("\n[bold green]E2seq:[/bold green]")
                    console.print(Markdown(response["text"]))

                    # Display plots
                    if response.get("plots"):
                        console.print(f"\n[cyan]Generated / 已生成 {len(response['plots'])} plot(s) / 个图表[/cyan]")
                        for plot_name, fig in response["plots"]:
                            output_file = f"{plot_name}_plot.html"
                            fig.write_html(output_file)
                            console.print(f"  - Saved / 已保存: {output_file}")

                    console.print()

                except Exception as e:
                    console.print(f"[red]ERROR / 错误[/red] Error / 失败: {e}")
                    logger.error(f"Chat error: {e}", exc_info=True)

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye / 再见![/yellow]")
            break
        except EOFError:
            break


@app.command()
def web(
    port: int = typer.Option(8521, "--port", "-p", help="Port number / 端口"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host address"),
):
    """Start the FastAPI web interface / 启动 FastAPI 网页界面。"""
    console.print(f"[cyan]Starting web interface / 启动网页界面: http://{host}:{port}[/cyan]")

    import subprocess

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "e2seq.api.server:app",
            "--host", host,
            "--port", str(port),
        ])
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down / 正在停止...[/yellow]")


@app.command()
def config(
    provider: Optional[str] = typer.Option(None, help="LLM provider"),
    api_key: Optional[str] = typer.Option(None, help="API key"),
    model: Optional[str] = typer.Option(None, help="Model name"),
):
    """Configure E2seq settings / 配置 E2seq 设置。"""
    cfg = get_config()
    security = get_security_manager()

    if not any([provider, api_key, model]):
        # Interactive configuration
        console.print("[bold cyan]E2seq Configuration / E2seq 配置[/bold cyan]\n")

        provider = typer.prompt(
            "LLM Provider / LLM 服务商",
            default=cfg.llm.provider,
            type=typer.Choice(["openai", "anthropic", "deepseek", "ollama"])
        )

        if provider != "ollama":
            api_key = typer.prompt("API Key / API 密钥", hide_input=True)

        model = typer.prompt("Model / 模型", default=cfg.llm.model)

    # Encrypt API key
    if api_key:
        api_key = security.encrypt(api_key)

    # Update configuration
    cfg.update_llm(provider, api_key or cfg.llm.api_key, model)

    console.print("[green]OK / 完成[/green] Configuration saved / 配置已保存")


@app.command()
def init_db(
    data_dir: Path = typer.Argument(..., help="Directory containing CSV files"),
):
    """Initialize databases from CSV files / 从 CSV 文件初始化数据库。"""
    console.print(f"[cyan]Initializing databases / 初始化数据库: {data_dir}[/cyan]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating databases...", total=None)

        try:
            initialize_databases(data_dir)
            console.print("[green]OK / 完成[/green] Databases initialized successfully / 数据库初始化成功")
        except Exception as e:
            console.print(f"[red]ERROR / 错误[/red] Error / 失败: {e}")
            logger.error(f"Database initialization error: {e}", exc_info=True)


@app.command()
def version():
    """Show version information / 显示版本信息。"""
    from e2seq import __version__
    console.print(f"E2seq version {__version__}")


def show_help():
    """Show help message."""
    help_text = """
# E2seq Commands / E2seq 命令

## Chat Commands / 对话命令
- `/load <file>` - Load an h5ad file / 加载 h5ad 文件
- `/stats` - Show agent statistics / 显示 Agent 统计
- `/tools` - Show available tools / 显示可用工具
- `/help` - Show this help / 显示帮助
- `/exit` - Exit chat / 退出对话

## Example Questions / 示例问题
- "Analyze differential genes in Enterocytes / 分析 Enterocytes 的差异基因"
- "Run GO enrichment for these genes / 对这些基因做 GO 富集分析"
- "Build a protein interaction network and find hub genes / 构建蛋白互作网络并找出 hub 基因"
- "Compare Enterocytes and Goblet cells / 比较 Enterocytes 与 Goblet cells"

## Tips / 提示
- Ask questions in Chinese or English / 支持中文和英文提问
- The agent plans and executes analyses automatically / Agent 会自动规划并执行分析
- Plots are saved as HTML files / 图表会保存为 HTML 文件
"""
    console.print(Markdown(help_text))


def show_stats(agent):
    """Show agent statistics."""
    if agent is None:
        console.print("[yellow]Agent not initialized[/yellow]")
        return

    try:
        console.print("\n[bold cyan]Agent Statistics / Agent 统计[/bold cyan]\n")

        # Memory stats
        memory_stats = agent.get_memory_stats()
        console.print("[bold]Memory / 记忆:[/bold]")
        console.print(f"  Current Messages: {memory_stats['current_session']['messages']}")
        console.print(f"  Context Items: {memory_stats['current_session']['context_items']}")
        console.print(f"  Total Sessions: {memory_stats['long_term']['total_sessions']}")
        console.print(f"  Success Rate: {memory_stats['long_term']['success_rate']:.1%}")

        # State stats
        state_stats = agent.get_state_summary()
        console.print(f"\n[bold]State / 状态:[/bold]")
        console.print(f"  Current State: {state_stats['current_state']}")
        console.print(f"  Tasks Queued: {state_stats['tasks_queued']}")
        console.print(f"  Checkpoints: {state_stats['checkpoints_created']}")

        # Error stats
        error_stats = agent.get_error_stats()
        console.print(f"\n[bold]Errors / 错误:[/bold]")
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
        console.print("\n[bold cyan]Available Tools / 可用工具[/bold cyan]\n")

        tools_summary = agent.tool_registry.get_tools_summary()
        console.print(f"Total Tools: {tools_summary['total_tools']}\n")

        # List all tools
        for tool_name in agent.tool_registry.get_tool_names():
            tool = agent.tool_registry.tools[tool_name]
            console.print(f"[bold green]Tool / 工具[/bold green] {tool_name}")
            console.print(f"  {tool.description}")

        console.print()

    except Exception as e:
        console.print(f"[red]Error getting tools: {e}[/red]")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
