"""
Theming tools: theme_base, apply_tokens.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Union

import jsonpatch

from ..models import ApplyTokensIn, ThemeBaseIn, Tokens, StatusOut

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_theming_tools(mcp: "FastMCP") -> None:
    """Register theming tools with the MCP server."""
    
    @mcp.tool()
    def theme_base(params: Union[ThemeBaseIn, str, dict]) -> Tokens:
        """Get base theme tokens for a template."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ThemeBaseIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ThemeBaseIn(**params)
        elif not isinstance(params, ThemeBaseIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Look for template tokens
        templates_dir = Path(__file__).parent.parent.parent / "templates" / params.template
        tokens_file = templates_dir / "tokens.json"
        
        if tokens_file.exists():
            # Load and parse tokens
            tokens_data = json.loads(tokens_file.read_text())
            return Tokens(**tokens_data)
        
        # Return default tokens if template not found
        return Tokens(
            colors={
                "primary": "#1D4ED8",
                "secondary": "#3B82F6",
                "accent": "#93C5FD",
                "neutral": {
                    "50": "#F9FAFB",
                    "100": "#F3F4F6",
                    "200": "#E5E7EB",
                    "300": "#D1D5DB",
                    "400": "#9CA3AF",
                    "500": "#6B7280",
                    "600": "#4B5563",
                    "700": "#374151",
                    "800": "#1F2937",
                    "900": "#111827"
                }
            },
            typography={
                "fontFamily": {
                    "heading": ["Montserrat", "system-ui", "-apple-system", "sans-serif"],
                    "body": ["Inter", "system-ui", "-apple-system", "sans-serif"],
                    "sans": ["Montserrat", "system-ui", "-apple-system", "sans-serif"],
                    "mono": ["JetBrains Mono", "Consolas", "Monaco", "monospace"]
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
                    "5xl": "3rem"
                },
                "fontWeight": {
                    "light": 300,
                    "normal": 400,
                    "medium": 500,
                    "semibold": 600,
                    "bold": 700,
                    "extrabold": 800
                }
            },
            spacing={
                "0": "0",
                "1": "0.25rem",
                "2": "0.5rem",
                "3": "0.75rem",
                "4": "1rem",
                "6": "1.5rem",
                "8": "2rem",
                "12": "3rem",
                "16": "4rem",
                "24": "6rem",
                "32": "8rem"
            }
        )
    
    @mcp.tool()
    def apply_tokens(params: Union[ApplyTokensIn, str, dict]) -> StatusOut:
        """Apply token patches to a deck."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ApplyTokensIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ApplyTokensIn(**params)
        elif not isinstance(params, ApplyTokensIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Load current tokens
        tokens_file = deck_root / "tokens.json"
        if tokens_file.exists():
            current_tokens = json.loads(tokens_file.read_text())
        else:
            # Load from template if no tokens exist
            metadata_file = deck_root / ".metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                template = metadata.get("template", "markov-pro")
                # Get base tokens from template
                base_params = ThemeBaseIn(template=template)
                base_tokens = theme_base(base_params)
                current_tokens = base_tokens.model_dump(exclude_unset=True)
            else:
                current_tokens = {}
        
        # Apply JSON patch
        try:
            # Convert patches dict to JSON patch format
            patch_ops = []
            for path, value in params.patches.items():
                patch_ops.append({
                    "op": "replace",
                    "path": f"/{path.replace('.', '/')}",
                    "value": value
                })
            patch = jsonpatch.JsonPatch(patch_ops)
            patched_tokens = patch.apply(current_tokens)
        except Exception as e:
            raise ValueError(f"Failed to apply token patch: {e}")
        
        # Validate the patched tokens
        try:
            validated_tokens = Tokens(**patched_tokens)
        except Exception as e:
            raise ValueError(f"Invalid tokens after patch: {e}")
        
        # Save the updated tokens
        tokens_file.write_text(json.dumps(patched_tokens, indent=2))
        
        # Also generate Tailwind config if needed
        _generate_tailwind_config(deck_root, validated_tokens)
        
        return StatusOut(
            success=True,
            message=f"Applied token patches to deck {params.deck_id}",
            details={"patches_applied": len(params.patches)}
        )


def _generate_tailwind_config(deck_root: Path, tokens: Tokens) -> None:
    """Generate Tailwind configuration from tokens."""
    # Create tailwind.config.js
    config_content = f"""module.exports = {{
  content: [
    './src/**/*.{{js,jsx,ts,tsx,mdx}}',
    './components/**/*.{{js,jsx,ts,tsx}}'
  ],
  theme: {{
    extend: {{
      colors: {json.dumps(tokens.colors.model_dump(exclude_unset=True) if tokens.colors else {}, indent=8).strip()},
      fontFamily: {json.dumps(tokens.typography.fontFamily if tokens.typography and tokens.typography.fontFamily else {}, indent=8).strip()},
      fontSize: {json.dumps(tokens.typography.fontSize if tokens.typography and tokens.typography.fontSize else {}, indent=8).strip()},
      fontWeight: {json.dumps(tokens.typography.fontWeight if tokens.typography and tokens.typography.fontWeight else {}, indent=8).strip()},
      spacing: {json.dumps(tokens.spacing or {}, indent=8).strip()},
      borderRadius: {json.dumps(tokens.borders.radius if tokens.borders and tokens.borders.radius else {}, indent=8).strip()},
      boxShadow: {json.dumps(tokens.shadows or {}, indent=8).strip()},
      transitionDuration: {json.dumps(tokens.transitions.duration if tokens.transitions and tokens.transitions.duration else {}, indent=8).strip()},
    }}
  }},
  plugins: [],
}}"""
    
    config_file = deck_root / "tailwind.config.js"
    config_file.write_text(config_content)