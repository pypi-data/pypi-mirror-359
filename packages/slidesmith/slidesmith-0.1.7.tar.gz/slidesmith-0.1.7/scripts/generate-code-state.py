#!/usr/bin/env python3
"""
Generate CODE_STATE.md documentation by analyzing the codebase using Gemini 2.5 API.
This script exports all Python source files and sends them to Gemini for analysis.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env file")
    sys.exit(1)

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Directories and files to exclude
EXCLUDE_DIRS = {
    '__pycache__', '.pytest_cache', 'dist', 'build', '*.egg-info',
    '.git', '.venv', 'venv', 'slidesmith-env', 'node_modules',
    'coverage', '.tox', '.mypy_cache', '.ruff_cache',
    # Additional exclusions for cleaner codebase
    '.local', '.cache', '.npm', '.yarn', '.pnpm-store',
    'htmlcov', 'site-packages', 'pip-wheel-metadata',
    '.idea', '.vscode', '.vs', '.sublime',
    'logs', 'tmp', 'temp', 'target', 'out',
    # Exclude all slidesmith workspace directories
    'slidesmith_workspaces',
    # Exclude pipx environments
    '.local/pipx', 'pipx',
    # Exclude package manager caches
    'bower_components', 'jspm_packages',
    # Exclude Python package directories
    'lib', 'lib64', 'include', 'bin', 'Scripts',
    # Exclude macOS specific
    '.Trash', 'Library'
}

EXCLUDE_FILES = {
    '.DS_Store', '.env', '.env.local', '.pypirc', 
    'poetry.lock', 'Pipfile.lock', '*.pyc', '*.pyo',
    # Additional file exclusions
    '*.log', '*.pid', '*.seed', '*.pid.lock',
    'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    # Build outputs
    '*.min.js', '*.min.css', 'bundle.js', 'bundle.css',
    # Test outputs
    '.coverage', 'coverage.xml', '*.cover', '.hypothesis',
    # IDE files
    '*.swp', '*.swo', '*~', '*.bak',
    # Compiled files
    '*.so', '*.dylib', '*.dll', '*.exe', '*.o', '*.a',
    # Archives
    '*.zip', '*.tar.gz', '*.tgz', '*.rar', '*.7z'
}

# File extensions to include (only source code and essential configs)
INCLUDE_EXTENSIONS = {
    '.py', '.pyi',  # Python source
    '.toml',  # pyproject.toml
    '.yaml', '.yml',  # Config files
    '.json',  # package.json, manifest.json (but NOT package-lock.json)
    '.md',  # Documentation (only key ones)
    '.js', '.jsx',  # JavaScript source (components, scripts)
    '.mdx',  # MDX slides (only examples, not generated)
}

# Important files to always include
PRIORITY_FILES = {
    'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt'
}

def should_include_file(file_path: Path) -> bool:
    """Check if a file should be included in the export."""
    # Always include priority files
    if file_path.name in PRIORITY_FILES:
        return True
    
    # Skip if in excluded directory
    for parent in file_path.parents:
        if parent.name in EXCLUDE_DIRS or any(parent.name.endswith(pattern) for pattern in ['egg-info']):
            return False
        # Also check for patterns in path
        path_str = str(parent)
        if any(excluded in path_str for excluded in ['node_modules', '.git', '__pycache__', 'venv', 'slidesmith_workspaces']):
            return False
    
    # Skip if excluded file
    if file_path.name in EXCLUDE_FILES:
        return False
    # Check file patterns
    for pattern in ['*.pyc', '*.pyo', '*.log', '*.pid', 'package-lock.json', 'yarn.lock']:
        if file_path.match(pattern):
            return False
    
    # Skip if not in included extensions
    if file_path.suffix not in INCLUDE_EXTENSIONS:
        return False
    
    # Skip test files unless they're part of the main tests directory
    if 'test_' in file_path.name and file_path.parent.name != 'tests':
        return False
    
    # Skip generated or temporary MDX files
    if file_path.suffix == '.mdx' and 'workspaces' in str(file_path):
        return False
    
    # Only include specific markdown files
    if file_path.suffix == '.md':
        important_md_files = {'README.md', 'CHANGELOG.md', 'CLAUDE.md', 'PLAN.md', 'CODE_STATE.md'}
        if file_path.name not in important_md_files:
            return False
    
    # Skip JavaScript files that are clearly build outputs or node_modules
    if file_path.suffix in ['.js', '.jsx']:
        path_str = str(file_path)
        if 'dist/' in path_str or 'build/' in path_str or '.min.' in file_path.name:
            return False
    
    # Skip files that are too large (over 100KB)
    try:
        if file_path.stat().st_size > 100 * 1024:  # 100KB
            return False
    except:
        pass
    
    return True

def export_codebase(project_root: Path) -> str:
    """Export all source files to a markdown format."""
    files_content = []
    file_count = 0
    
    print(f"Scanning {project_root}...")
    
    # Collect all files
    all_files = []
    
    # First, add priority files if they exist
    for priority_file in PRIORITY_FILES:
        file_path = project_root / priority_file
        if file_path.exists() and file_path.is_file():
            all_files.append(file_path)
    
    # Then add all other matching files
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and should_include_file(file_path) and file_path not in all_files:
            all_files.append(file_path)
    
    # Sort files for consistent output (keeping priority files first)
    priority_count = len([f for f in all_files if f.name in PRIORITY_FILES])
    all_files = all_files[:priority_count] + sorted(all_files[priority_count:])
    
    print(f"Found {len(all_files)} files to analyze")
    
    # Process each file
    for file_path in all_files:
        relative_path = file_path.relative_to(project_root)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                continue
            
            # Determine language for syntax highlighting
            lang = file_path.suffix[1:] if file_path.suffix else 'text'
            if lang == 'yml':
                lang = 'yaml'
            elif file_path.name in ['requirements.txt', 'constraints.txt']:
                lang = 'text'
            
            files_content.append(f"## File: {relative_path}\n")
            files_content.append(f"```{lang}\n{content}\n```\n")
            file_count += 1
            
            if file_count % 10 == 0:
                print(f"Processed {file_count} files...")
                
        except Exception as e:
            print(f"Warning: Could not read {relative_path}: {e}")
    
    print(f"Successfully exported {file_count} files")
    
    # Create the full export
    export_content = f"""# Slidesmith MCP Server - Codebase Export
Generated: {datetime.now().isoformat()}
Total Files: {file_count}

{chr(10).join(files_content)}
"""
    
    return export_content

def generate_documentation(codebase_export: str) -> str:
    """Send codebase to Gemini via OpenRouter and get documentation."""
    print("Sending codebase to Gemini 2.5 for analysis...")
    
    # Prepare the prompt
    prompt = """You are a technical documentation expert. Analyze this Python/FastMCP codebase for the Slidesmith MCP Server project and create a comprehensive CODE_STATE.md documentation file.

This is an MCP (Model Context Protocol) server that converts Markdown to slide decks using FastMCP, React, and Tailwind.

Focus on:
1. Current implementation status of the 11 MCP tools (list_templates, init_deck, theme_base, apply_tokens, html_preview, slide_lint, snapshot, pdf_export, get_component_doc, svg_icon, cleanup)
2. Phase completion status (P0-P10 from PLAN.md)
3. Project structure and architecture
4. Key modules and their purposes
5. FastMCP tool implementations
6. Component library status (React/MDX components)
7. Build pipeline implementation
8. Testing coverage
9. Technical debt or known issues
10. Next steps for incomplete features

Format the documentation with:
- Clear markdown structure
- Percentage completion for each phase
- Status of each MCP tool (not started/in progress/complete)
- File paths for key implementations
- Breaking changes or migration notes
- Specific next actions for continuing development

Be concise but thorough. Focus on what a developer needs to know to continue work on this MCP server."""

    try:
        # Use Gemini 2.5 Flash Preview
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash-preview-05-20",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical documentation expert specializing in Python MCP servers and FastMCP framework."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{codebase_export}"
                }
            ],
            temperature=0.7,  # Higher temperature for more comprehensive analysis
        )
        
        documentation = response.choices[0].message.content
        
        # Add metadata header
        header = f"""# Slidesmith MCP Server - Current Codebase State
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*
*Generated by: scripts/generate-code-state.py*
*Model: Gemini 2.5 Flash Preview*

---

"""
        
        return header + documentation
        
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

def main():
    """Main function to generate CODE_STATE.md"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate CODE_STATE.md documentation for Slidesmith')
    parser.add_argument('-y', '--yes', action='store_true', 
                       help='Automatically proceed with large codebases')
    parser.add_argument('--max-tokens', type=int, default=150000,
                       help='Maximum tokens before warning (default: 150000)')
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    # Create docs directory if it doesn't exist
    docs_dir.mkdir(exist_ok=True)
    
    print("Starting CODE_STATE.md generation for Slidesmith...")
    
    # Step 1: Export codebase
    codebase_export = export_codebase(project_root)
    
    # Check token count estimate (rough: 1 token ≈ 4 chars)
    estimated_tokens = len(codebase_export) / 4
    print(f"Estimated tokens: {estimated_tokens:,.0f}")
    
    if estimated_tokens > args.max_tokens:
        print(f"Warning: Large codebase may exceed token limits ({estimated_tokens:,.0f} > {args.max_tokens:,})")
        if not args.yes:
            try:
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    sys.exit(0)
            except EOFError:
                print("\nNon-interactive mode detected. Use -y flag to auto-proceed.")
                sys.exit(1)
    
    # Step 2: Generate documentation
    documentation = generate_documentation(codebase_export)
    
    if not documentation:
        print("Failed to generate documentation")
        sys.exit(1)
    
    # Step 3: Save documentation
    output_path = docs_dir / "CODE_STATE.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print(f"\n✅ Successfully generated {output_path}")
    print(f"Documentation length: {len(documentation):,} characters")
    
    # Also save a copy with timestamp for history
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_dir = docs_dir / "code_state_history"
    history_dir.mkdir(exist_ok=True)
    history_path = history_dir / f"CODE_STATE_{timestamp}.md"
    with open(history_path, 'w', encoding='utf-8') as f:
        f.write(documentation)
    print(f"History saved to: {history_path}")

if __name__ == "__main__":
    main()