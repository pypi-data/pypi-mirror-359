"""
Setup utilities for Slidesmith.

Handles initial configuration, template installation, and browser setup.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console


def setup_slidesmith(force: bool = False, console: Optional[Console] = None) -> None:
    """
    Perform initial setup for Slidesmith.
    
    Args:
        force: Force setup even if already configured
        console: Rich console for output
    """
    if console is None:
        console = Console()
    
    home_dir = Path.home()
    slidesmith_dir = home_dir / ".slidesmith"
    workspaces_dir = home_dir / "slidesmith_workspaces"
    
    # Create directories
    if slidesmith_dir.exists() and not force:
        console.print("[yellow]Slidesmith is already set up.[/yellow]")
        console.print("Use --force to reconfigure.")
        return
    
    console.print("Creating directories...")
    slidesmith_dir.mkdir(exist_ok=True)
    workspaces_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (slidesmith_dir / "templates").mkdir(exist_ok=True)
    (slidesmith_dir / "components").mkdir(exist_ok=True)
    (slidesmith_dir / "icons").mkdir(exist_ok=True)
    
    # Copy bundled templates and components
    # Templates should be inside the slidesmith package
    templates_src = Path(__file__).parent / "templates"
    
    # If not found in package, try relative to script (development mode)
    if not templates_src.exists():
        templates_src = Path(__file__).parent.parent.parent / "templates"
    
    if templates_src.exists():
        console.print("Copying templates...")
        for template_src in templates_src.glob("*"):
            if template_src.is_dir():
                template_dst = slidesmith_dir / "templates" / template_src.name
                if template_dst.exists() and not force:
                    console.print(f"[yellow]Template {template_src.name} already exists, skipping...[/yellow]")
                else:
                    shutil.copytree(template_src, template_dst, dirs_exist_ok=True)
                    console.print(f"[green]✓[/green] Copied template: {template_src.name}")
    else:
        # Fallback: create minimal markov-pro template
        console.print("[yellow]Templates not found in package, creating minimal template...[/yellow]")
        template_dir = slidesmith_dir / "templates" / "markov-pro"
        template_dir.mkdir(exist_ok=True)
        
        manifest_content = """{
    "name": "markov-pro",
    "display_name": "Markov Professional",
    "description": "Professional template with Markov branding",
    "version": "1.0.0",
    "components": [
        "SlideBase",
        "Header",
        "Footer",
        "Columns",
        "BarChart",
        "PieChart",
        "MetricSection",
        "ImpactBox"
    ]
}"""
        (template_dir / "manifest.json").write_text(manifest_content)
    
    console.print("[green]✓[/green] Created directory structure")
    
    # Install Playwright browsers if needed
    try:
        console.print("Checking Playwright browsers...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run"],
            capture_output=True,
            text=True,
        )
        
        if "chromium" not in result.stdout.lower():
            console.print("Installing Playwright browsers...")
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
            console.print("[green]✓[/green] Installed Playwright browsers")
        else:
            console.print("[green]✓[/green] Playwright browsers already installed")
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install Playwright browsers: {e}[/red]")
        raise
    
    # Create example configuration
    config_content = """{
    "default_template": "markov-pro",
    "output_quality": 95,
    "lint_threshold": 80
}"""
    (slidesmith_dir / "config.json").write_text(config_content)
    
    console.print("[green]✓[/green] Created default configuration")
    console.print(f"\nSetup complete! Files created in: {slidesmith_dir}")