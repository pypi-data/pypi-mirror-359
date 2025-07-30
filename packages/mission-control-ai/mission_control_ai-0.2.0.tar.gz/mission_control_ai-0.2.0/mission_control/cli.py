"""Command-line interface for Mission Control"""

import typer
from typing import Optional
from pathlib import Path
import os
from loguru import logger
from rich.console import Console

from .core.config import MissionConfig
from .terminal.interface import TerminalInterface

app = typer.Typer(
    name="mission-control",
    help="AI Development Workflow Orchestration System",
    add_completion=False
)

console = Console()


@app.command()
def build(
    target: str = typer.Argument(
        ...,
        help="What to build (e.g., 'api', 'frontend', 'database', 'full-stack')"
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Additional description or requirements"
    ),
    agents: Optional[str] = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated list of specific agents to use"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file"
    ),
    env_file: Optional[Path] = typer.Option(
        ".env",
        "--env",
        "-e",
        help="Path to environment file"
    )
):
    """Build software components using AI agents
    
    Examples:
        mission-control build api
        mission-control build frontend --description "React app with TypeScript"
        mission-control build full-stack --agents "architect,developer,tester"
    """
    
    # Setup logging
    logger.remove()
    logger.add(
        "mission_control.log",
        rotation="10 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # Load configuration
    if env_file and env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    config = MissionConfig()
    
    # Override with config file if provided
    if config_file and config_file.exists():
        import json
        with open(config_file) as f:
            config_data = json.load(f)
            config = MissionConfig(**config_data)
    
    # Create build description
    build_description = f"Build {target}"
    if description:
        build_description += f": {description}"
    
    # Select agents
    selected_agents = []
    if agents:
        selected_agents = [a.strip() for a in agents.split(",")]
    
    console.print(f"[bold cyan]Mission Control - Build Command[/bold cyan]")
    console.print(f"Target: [green]{target}[/green]")
    if description:
        console.print(f"Description: {description}")
    if selected_agents:
        console.print(f"Agents: {', '.join(selected_agents)}")
    console.print()
    
    # Initialize orchestrator
    from .core.orchestrator import MissionOrchestrator
    orchestrator = MissionOrchestrator(config)
    
    try:
        # Start the build mission
        console.print("[yellow]Starting build mission...[/yellow]")
        
        # Run the mission asynchronously
        import asyncio
        result = asyncio.run(orchestrator.start_mission(build_description, selected_agents))
        
        # Display results
        console.print("\n[bold green]Build mission completed successfully![/bold green]")
        console.print(f"Mission ID: {result['id']}")
        
        # Show summary of what was built
        if "execution" in result["results"]:
            console.print("\n[bold]Build Summary:[/bold]")
            exec_result = result["results"]["execution"]
            if isinstance(exec_result, dict):
                for key, value in exec_result.items():
                    console.print(f"  • {key}: {value}")
        
    except Exception as e:
        console.print(f"\n[red]Build failed: {str(e)}[/red]")
        logger.exception("Build command failed")
        raise typer.Exit(1)


@app.command()
def run(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file"
    ),
    env_file: Optional[Path] = typer.Option(
        ".env",
        "--env",
        "-e",
        help="Path to environment file"
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Logging level"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        "-i/-n",
        help="Run in interactive mode"
    )
):
    """Run Mission Control terminal interface"""
    
    # Setup logging
    logger.remove()  # Remove default handler
    logger.add(
        "mission_control.log",
        rotation="10 MB",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        lambda msg: console.print(f"[dim]{msg}[/dim]"),
        level="ERROR"
    )
    
    # Load configuration
    if env_file and env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    config = MissionConfig()
    
    # Override with config file if provided
    if config_file and config_file.exists():
        import json
        with open(config_file) as f:
            config_data = json.load(f)
            config = MissionConfig(**config_data)
    
    # Create and run terminal interface
    interface = TerminalInterface(config)
    interface.interactive_mode = interactive
    
    try:
        interface.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Mission Control terminated by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        logger.exception("Unhandled exception in Mission Control")
        raise typer.Exit(1)


@app.command()
def init(
    project_dir: Path = typer.Argument(
        Path("."),
        help="Project directory to initialize"
    ),
    name: str = typer.Option(
        "my-project",
        "--name",
        "-n",
        help="Project name"
    )
):
    """Initialize a new Mission Control project"""
    
    console.print(f"[bold]Initializing Mission Control project: {name}[/bold]")
    
    # Create project structure
    if project_dir.name != name:
        project_dir = project_dir / name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create directories
    dirs = ["src", "tests", "docs", "config", ".mission_control"]
    for dir_name in dirs:
        (project_dir / dir_name).mkdir(exist_ok=True)
    
    # Create .env file
    env_content = """# Mission Control Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# API Keys
ANTHROPIC_API_KEY=your-api-key-here
OPENAI_API_KEY=your-api-key-here
MEM0_API_KEY=your-api-key-here

# Memory Configuration
MEMORY_PROVIDER=mem0
MEMORY_VECTOR_DB_TYPE=chromadb

# Orchestrator Configuration
ORCHESTRATOR_MAX_CONCURRENT_AGENTS=10
ORCHESTRATOR_ENABLE_MONITORING=true
"""
    
    with open(project_dir / ".env", "w") as f:
        f.write(env_content)
    
    # Create config file
    config_content = {
        "project_name": name,
        "agent_profiles": {
            "architect": {
                "name": "System Architect",
                "capabilities": ["system_design", "architecture_planning"]
            },
            "developer": {
                "name": "Senior Developer",
                "capabilities": ["code_generation", "refactoring"]
            }
        }
    }
    
    import json
    with open(project_dir / "config" / "mission_config.json", "w") as f:
        json.dump(config_content, f, indent=2)
    
    # Create .gitignore
    gitignore_content = """# Mission Control
.mission_control/
mission_control.log
.env

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# IDE
.vscode/
.idea/
"""
    
    with open(project_dir / ".gitignore", "w") as f:
        f.write(gitignore_content)
    
    console.print(f"[green]✓[/green] Created project directory: {project_dir}")
    console.print(f"[green]✓[/green] Created configuration files")
    console.print(f"[green]✓[/green] Created project structure")
    
    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"1. cd {project_dir}")
    console.print(f"2. Edit .env file with your API keys")
    console.print(f"3. Run: mission-control run")


@app.command()
def config():
    """Configure Mission Control settings interactively"""
    from .terminal.config_ui import run_config_ui
    run_config_ui()


@app.command()
def version():
    """Show Mission Control version"""
    from . import __version__
    console.print(f"Mission Control v{__version__}")


@app.command()
def agents():
    """List available agent types"""
    
    agents_info = {
        "architect": "System design and architecture planning",
        "developer": "Code implementation and refactoring",
        "tester": "Testing and quality assurance",
        "debugger": "Error analysis and bug fixing",
        "devops": "Environment setup and deployment",
        "security": "Security audits and vulnerability scanning"
    }
    
    console.print("[bold]Available Agent Types:[/bold]\n")
    
    for agent_type, description in agents_info.items():
        console.print(f"  [cyan]{agent_type:12}[/cyan] {description}")


@app.command()
def mcp(
    action: str = typer.Argument(
        ...,
        help="Action to perform: 'list', 'connect', 'disconnect', 'status'"
    ),
    server: Optional[str] = typer.Argument(
        None,
        help="MCP server name or URL (for connect/disconnect)"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to MCP configuration file"
    )
):
    """Manage MCP (Model Context Protocol) server connections
    
    Examples:
        mission-control mcp list
        mission-control mcp connect github
        mission-control mcp connect custom --config mcp-config.json
        mission-control mcp status
    """
    
    from .mcp import MCPManager
    
    mcp_manager = MCPManager()
    
    if action == "list":
        console.print("[bold]Available MCP Servers:[/bold]\n")
        servers = mcp_manager.list_available_servers()
        for server in servers:
            status = "[green]connected[/green]" if server["connected"] else "[dim]disconnected[/dim]"
            console.print(f"  [cyan]{server['name']:15}[/cyan] {server['description']} {status}")
    
    elif action == "connect":
        if not server:
            console.print("[red]Error: Server name required for connect action[/red]")
            raise typer.Exit(1)
        
        console.print(f"Connecting to MCP server: {server}...")
        try:
            mcp_manager.connect_server(server, config_file)
            console.print(f"[green]Successfully connected to {server}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to connect: {str(e)}[/red]")
            raise typer.Exit(1)
    
    elif action == "disconnect":
        if not server:
            console.print("[red]Error: Server name required for disconnect action[/red]")
            raise typer.Exit(1)
        
        console.print(f"Disconnecting from MCP server: {server}...")
        try:
            mcp_manager.disconnect_server(server)
            console.print(f"[green]Successfully disconnected from {server}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to disconnect: {str(e)}[/red]")
            raise typer.Exit(1)
    
    elif action == "status":
        console.print("[bold]MCP Server Status:[/bold]\n")
        status = mcp_manager.get_status()
        console.print(f"Connected servers: {status['connected_count']}")
        console.print(f"Total servers: {status['total_count']}")
        
        if status['connected_servers']:
            console.print("\n[bold]Connected Servers:[/bold]")
            for server in status['connected_servers']:
                console.print(f"  • {server}")
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Valid actions: list, connect, disconnect, status")
        raise typer.Exit(1)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()