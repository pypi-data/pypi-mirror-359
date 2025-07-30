"""
Deck management tools: list_templates, init_deck, cleanup.
"""

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from ..models import (
    DeckInfo,
    DeckMetadata,
    DeckRef,
    InitDeckIn,
    StatusOut,
    TemplateInfo,
    TemplatesOut,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_deck_management_tools(mcp: "FastMCP") -> None:
    """Register deck management tools with the MCP server."""
    
    @mcp.tool()
    def list_templates() -> TemplatesOut:
        """List available slide templates."""
        templates = []
        
        # Check both local and user templates directories
        template_dirs = [
            Path(__file__).parent.parent.parent / "templates",  # Local templates
            Path.home() / ".slidesmith" / "templates"  # User templates
        ]
        
        seen_templates = set()
        
        for templates_dir in template_dirs:
            if templates_dir.exists():
                for template_dir in templates_dir.iterdir():
                    if template_dir.is_dir() and template_dir.name not in seen_templates:
                        manifest_path = template_dir / "manifest.json"
                        if manifest_path.exists():
                            manifest = json.loads(manifest_path.read_text())
                            templates.append(
                                TemplateInfo(
                                    name=manifest["name"],
                                    display_name=manifest.get("display_name", manifest["name"]),
                                    description=manifest.get("description", ""),
                                    preview_image=manifest.get("preview_image"),
                                    components=manifest.get("components", []),
                                )
                            )
                            seen_templates.add(template_dir.name)
        
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
        # Generate deck ID
        deck_id = str(uuid.uuid4())
        
        # Create workspace directory
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        
        # Check total workspace size (limit: 5GB)
        MAX_WORKSPACE_SIZE_GB = 5
        total_workspace_size = 0
        if workspaces_dir.exists():
            for deck_dir in workspaces_dir.iterdir():
                if deck_dir.is_dir():
                    for path in deck_dir.rglob("*"):
                        if path.is_file():
                            total_workspace_size += path.stat().st_size
        
        # Convert to GB
        workspace_size_gb = total_workspace_size / (1024 * 1024 * 1024)
        if workspace_size_gb > MAX_WORKSPACE_SIZE_GB:
            raise ValueError(
                f"Workspace size limit exceeded: {workspace_size_gb:.2f}GB / {MAX_WORKSPACE_SIZE_GB}GB. "
                "Please clean up old decks using the cleanup tool."
            )
        
        deck_root = workspaces_dir / deck_id
        deck_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (deck_root / "src").mkdir(exist_ok=True)
        (deck_root / "public").mkdir(exist_ok=True)
        (deck_root / "build").mkdir(exist_ok=True)
        
        # Copy template files
        # First check local templates directory, then user home
        local_template_dir = Path(__file__).parent.parent.parent / "templates" / params.template.value
        user_template_dir = Path.home() / ".slidesmith" / "templates" / params.template.value
        
        template_dir = local_template_dir if local_template_dir.exists() else user_template_dir
        
        if template_dir.exists():
            # Copy components
            components_src = template_dir / "components"
            if components_src.exists():
                components_dst = deck_root / "components"
                shutil.copytree(components_src, components_dst, dirs_exist_ok=True)
            
            # Copy tokens if exists
            tokens_src = template_dir / "tokens.json"
            if tokens_src.exists():
                shutil.copy2(tokens_src, deck_root / "tokens.json")
            
            # Copy manifest
            manifest_src = template_dir / "manifest.json"
            if manifest_src.exists():
                shutil.copy2(manifest_src, deck_root / "template-manifest.json")
        
        # Copy package.json for npm dependencies
        package_json_src = Path(__file__).parent.parent / "package.json"
        if package_json_src.exists():
            shutil.copy2(package_json_src, deck_root / "package.json")
        else:
            # Create a minimal package.json
            package_data = {
                "name": f"slidesmith-deck-{deck_id}",
                "private": True,
                "type": "module",
                "dependencies": {
                    "@mdx-js/esbuild": "^3.0.1",
                    "esbuild": "^0.21.5",
                    "react": "^18.3.1",
                    "react-dom": "^18.3.1",
                    "tailwindcss": "^3.4.4",
                    "chart.js": "^4.4.3"
                }
            }
            (deck_root / "package.json").write_text(json.dumps(package_data, indent=2))
        
        # Copy scripts directory
        scripts_src = Path(__file__).parent.parent / "scripts"
        if scripts_src.exists():
            scripts_dst = deck_root / "scripts"
            shutil.copytree(scripts_src, scripts_dst, dirs_exist_ok=True)
        
        # Create initial tokens.json
        tokens = {
            "colors": {
                "primary": "#1D4ED8",
                "secondary": "#3B82F6",
                "accent": "#93C5FD",
                "background": "#FFFFFF",
                "text": "#1F2937",
            },
            "typography": {
                "fontFamily": "Montserrat, sans-serif",
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
                },
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "1rem",
                "md": "1.5rem",
                "lg": "2rem",
                "xl": "3rem",
                "2xl": "4rem",
            },
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
            slides_count=0,
            metadata_version="1.0",
        )
        (deck_root / ".metadata.json").write_text(
            json.dumps(metadata.model_dump(), indent=2, default=str)
        )
        
        # Create initial slide
        initial_slide = f"""import {{ SlideBase, Header, Footer }} from '../components';

export default function Slide01() {{
  return (
    <SlideBase>
      <Header 
        logo="MARKOV AI"
        date="{datetime.now().strftime('%B %Y')}"
        confidentiality="Confidential"
      />
      
      <div className="flex-grow w-full px-32 py-8">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-blue-800 mb-6">
              {params.title}
            </h1>
            <h2 className="text-3xl font-semibold text-blue-600">
              {params.author or 'Your Name Here'}
            </h2>
            <div className="h-1 w-32 bg-blue-700 mx-auto mt-8"></div>
          </div>
        </div>
      </div>
      
      <Footer 
        pageNumber={{1}}
        tagline="Transform. Automate. Scale."
      />
    </SlideBase>
  );
}}
"""
        (deck_root / "src" / "slide-01.mdx").write_text(initial_slide)
        
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
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            return StatusOut(
                success=False,
                message=f"Deck {params.deck_id} not found",
            )
        
        try:
            # Calculate workspace size before deletion
            total_size = 0
            file_count = 0
            for path in deck_root.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
                    file_count += 1
            
            # Convert to MB
            size_mb = total_size / (1024 * 1024)
            
            # Remove the entire deck directory
            shutil.rmtree(deck_root)
            
            return StatusOut(
                success=True,
                message=f"Successfully removed deck {params.deck_id}",
                details={
                    "path": str(deck_root),
                    "size_mb": round(size_mb, 2),
                    "file_count": file_count,
                },
            )
        except Exception as e:
            return StatusOut(
                success=False,
                message=f"Failed to remove deck: {str(e)}",
            )