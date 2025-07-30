"""
Deck management tools: list_templates, init_deck, cleanup.
Updated to use Markdown format instead of MDX.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..models import (
    DeckInfo,
    DeckMetadata,
    DeckRef,
    InitDeckIn,
    StatusOut,
    TemplateInfo,
    TemplatesOut,
    TemplateType,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_deck_management_tools(mcp: "FastMCP") -> None:
    """Register deck management tools with the MCP server."""
    
    # Get slidesmith config directory
    config_dir = Path.home() / ".slidesmith"
    templates_dir = config_dir / "templates"
    
    @mcp.tool()
    def list_templates() -> TemplatesOut:
        """List available slide templates."""
        templates = []
        
        # List templates from config directory
        if templates_dir.exists():
            for template_dir in templates_dir.iterdir():
                if template_dir.is_dir() and (template_dir / "manifest.json").exists():
                    manifest_path = template_dir / "manifest.json"
                    manifest = json.loads(manifest_path.read_text())
                    templates.append(
                        TemplateInfo(
                            name=template_dir.name,
                            display_name=manifest.get("name", template_dir.name),
                            description=manifest.get("description", ""),
                            preview_image=manifest.get("preview_url"),
                        )
                    )
        
        # Add built-in templates if not found
        if not any(t.name == "markov-pro" for t in templates):
            templates.append(
                TemplateInfo(
                    name="markov-pro",
                    display_name="Markov Pro",
                    description="Professional template with modern design",
                    preview_image=None,
                )
            )
        
        if not any(t.name == "minimal" for t in templates):
            templates.append(
                TemplateInfo(
                    name="minimal",
                    display_name="Minimal",
                    description="Clean and simple template",
                    preview_image=None,
                )
            )
        
        if not any(t.name == "tech" for t in templates):
            templates.append(
                TemplateInfo(
                    name="tech",
                    display_name="Tech",
                    description="Technical presentation template",
                    preview_image=None,
                )
            )
        
        return TemplatesOut(templates=templates, count=len(templates))
    
    @mcp.tool()
    def init_deck(params: Union[InitDeckIn, str, dict]) -> DeckInfo:
        """Initialize a new slide deck."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = InitDeckIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = InitDeckIn(**params)
        elif not isinstance(params, InitDeckIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Create deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        workspaces_dir.mkdir(exist_ok=True)
        
        # Check workspace size limit (5GB)
        MAX_WORKSPACE_SIZE_GB = 5
        total_size = sum(
            f.stat().st_size for f in workspaces_dir.rglob("*") if f.is_file()
        )
        if total_size > MAX_WORKSPACE_SIZE_GB * 1024 * 1024 * 1024:
            raise ValueError(
                f"Workspace size limit exceeded ({MAX_WORKSPACE_SIZE_GB}GB). "
                "Please clean up old decks first."
            )
        
        # Generate deck ID (UUID format)
        import uuid
        deck_id = str(uuid.uuid4())
        deck_root = workspaces_dir / deck_id
        deck_root.mkdir()
        
        # Create directory structure
        (deck_root / "src").mkdir()
        (deck_root / "assets").mkdir()
        (deck_root / "assets" / "images").mkdir()
        (deck_root / "build").mkdir()
        (deck_root / "exports").mkdir()
        
        # Copy template files if available
        template_dir = templates_dir / params.template.value
        if template_dir.exists():
            # Copy components
            if (template_dir / "components").exists():
                shutil.copytree(
                    template_dir / "components",
                    deck_root / "components",
                    dirs_exist_ok=True
                )
            
            # Copy assets
            if (template_dir / "assets").exists():
                shutil.copytree(
                    template_dir / "assets",
                    deck_root / "assets",
                    dirs_exist_ok=True
                )
            
            # Copy tokens
            if (template_dir / "tokens.json").exists():
                shutil.copy2(
                    template_dir / "tokens.json",
                    deck_root / "tokens.json"
                )
        
        # Create default tokens.json if not copied
        if not (deck_root / "tokens.json").exists():
            tokens = {
                "theme": params.template.value,
                "colors": {
                    "primary": "#1D4ED8",
                    "secondary": "#3B82F6",
                    "accent": "#93C5FD",
                    "background": "#FFFFFF",
                    "text": "#1F2937",
                },
                "typography": {
                    "fontFamily": {
                        "heading": ["Montserrat", "sans-serif"],
                        "body": ["Inter", "sans-serif"],
                        "mono": ["Fira Code", "monospace"]
                    },
                    "fontSize": {
                        "xs": "0.75rem",
                        "sm": "0.875rem",
                        "base": "1rem",
                        "lg": "1.125rem",
                        "xl": "1.25rem",
                        "2xl": "1.5rem",
                        "3xl": "1.875rem",
                        "4xl": "2.25rem",
                        "5xl": "3rem",
                        "6xl": "3.75rem",
                    }
                },
                "spacing": {
                    "xs": "0.5rem",
                    "sm": "1rem",
                    "md": "1.5rem",
                    "lg": "2rem",
                    "xl": "3rem",
                    "2xl": "4rem",
                }
            }
            (deck_root / "tokens.json").write_text(json.dumps(tokens, indent=2))
        
        # Create metadata
        now = datetime.now(timezone.utc)
        metadata = DeckMetadata(
            deck_id=deck_id,
            created_at=now,
            updated_at=now,
            template=params.template.value,
            title=params.title,
            author=params.author,
            slides_count=1,
            metadata_version="1.0",
        )
        (deck_root / ".metadata.json").write_text(
            json.dumps(metadata.model_dump(), indent=2, default=str)
        )
        
        # Create initial slide in Markdown format
        author_name = params.author or 'Your Name Here'
        current_date = datetime.now().strftime('%B %Y')
        
        initial_slide = f"""---
slide: 1
template: title
---

# {params.title}

## {author_name}

**Date:** {current_date}  
**Confidential**

:::speaker-notes
Welcome to your presentation. This is the title slide.
You can add speaker notes that won't be visible during the presentation.
:::
"""
        
        # Create a second slide with example content
        second_slide = """
---
slide: 2
template: standard
---

# Agenda

:::columns ratio=7:5
### Topics to Cover
- Introduction and Overview
- Key Features and Benefits
- Implementation Strategy
- Timeline and Milestones
- Next Steps

### Expected Outcomes
:::card title="Success Metrics" icon=chart-line color=blue
- Increased efficiency by 40%
- Cost reduction of $2M annually
- Improved customer satisfaction
:::
:::

:::speaker-notes
This slide shows the agenda for today's presentation.
Note the use of columns and card components.
:::
"""
        
        # Write slides
        (deck_root / "src" / "slides.md").write_text(initial_slide + "\n" + second_slide)
        
        # Also create individual slide files for compatibility
        (deck_root / "src" / "slide-01.md").write_text(initial_slide)
        (deck_root / "src" / "slide-02.md").write_text(second_slide)
        
        return DeckInfo(
            deck_id=deck_id,
            root=str(deck_root),
            created_at=now,
            template=params.template.value,
            title=params.title,
        )
    
    @mcp.tool()
    def cleanup(params: Union[DeckRef, str, dict]) -> StatusOut:
        """Clean up a deck workspace."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = DeckRef(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = DeckRef(**params)
        elif not isinstance(params, DeckRef):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Calculate size before deletion
        total_size = sum(
            f.stat().st_size for f in deck_root.rglob("*") if f.is_file()
        )
        
        # Remove the deck directory
        shutil.rmtree(deck_root)
        
        # Return size in MB
        size_mb = total_size / (1024 * 1024)
        
        return StatusOut(
            success=True,
            message=f"Removed deck {params.deck_id} ({size_mb:.1f} MB)",
        )