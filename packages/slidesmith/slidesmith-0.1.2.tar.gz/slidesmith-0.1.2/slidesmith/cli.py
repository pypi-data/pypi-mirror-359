"""
CLI interface for Slidesmith MCP Server.

Provides commands for:
- serve: Run the MCP server in stdio mode
- setup: Initial setup (copy templates, install browsers)
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .server import create_server, run_server
from .setup import setup_slidesmith

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="slidesmith")
def cli() -> None:
    """Slidesmith MCP Server - Create pixel-perfect slide decks from Markdown."""
    pass


@cli.command()
@click.option(
    "--host",
    default="localhost",
    help="Host to bind to (for HTTP mode)",
)
@click.option(
    "--port",
    default=5858,
    type=int,
    help="Port to bind to (for HTTP mode)",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport mode for MCP server",
)
def serve(host: str, port: int, transport: str) -> None:
    """Run the Slidesmith MCP server."""
    try:
        console.print(
            Panel.fit(
                f"[bold blue]Slidesmith MCP Server v{__version__}[/bold blue]\n"
                f"Transport: [green]{transport}[/green]",
                title="Starting Server",
                border_style="blue",
            )
        )
        
        if transport == "stdio":
            console.print("[dim]Running in stdio mode (for Claude Code)[/dim]")
        else:
            console.print(f"[dim]Running on http://{host}:{port}[/dim]")
        
        # Create and run the server
        server = create_server()
        run_server(server, transport=transport, host=host, port=port)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force setup even if already configured",
)
def setup(force: bool) -> None:
    """Set up Slidesmith (install templates, browsers, etc.)."""
    try:
        console.print(
            Panel.fit(
                "[bold blue]Slidesmith Setup[/bold blue]\n"
                "This will install templates and required browsers",
                title="Setup",
                border_style="blue",
            )
        )
        
        setup_slidesmith(force=force, console=console)
        
        console.print("\n[green]✓[/green] Setup complete!")
        console.print("\nYou can now run: [bold]slidesmith serve[/bold]")
        
    except Exception as e:
        console.print(f"[red]Setup failed: {e}[/red]")
        sys.exit(1)


@cli.command()
def info() -> None:
    """Show information about the Slidesmith installation."""
    home_dir = Path.home()
    slidesmith_dir = home_dir / ".slidesmith"
    workspaces_dir = home_dir / "slidesmith_workspaces"
    
    console.print(
        Panel.fit(
            f"[bold]Slidesmith MCP Server v{__version__}[/bold]\n\n"
            f"[blue]Directories:[/blue]\n"
            f"  Config: {slidesmith_dir}\n"
            f"  Workspaces: {workspaces_dir}\n\n"
            f"[blue]Status:[/blue]\n"
            f"  Templates: {'✓' if (slidesmith_dir / 'templates').exists() else '✗'}\n"
            f"  Components: {'✓' if (slidesmith_dir / 'components').exists() else '✗'}",
            title="Installation Info",
            border_style="blue",
        )
    )


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()