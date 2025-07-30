"""
Configuration settings for Slidesmith.
"""

import os
from pathlib import Path


def get_workspace_dir() -> Path:
    """
    Get the workspace directory for slidesmith decks.
    
    Returns the slidedecks directory in the current repository if we're in a git repo,
    otherwise falls back to user home directory.
    """
    # Try to find the git root
    current_dir = Path.cwd()
    
    # Walk up the directory tree looking for .git
    while current_dir != current_dir.parent:
        if (current_dir / '.git').exists():
            # Found git root, use slidedecks folder
            workspace_dir = current_dir / 'slidedecks'
            workspace_dir.mkdir(exist_ok=True)
            return workspace_dir
        current_dir = current_dir.parent
    
    # Fallback to home directory if not in a git repo
    workspace_dir = Path.home() / "slidesmith_workspaces"
    workspace_dir.mkdir(exist_ok=True)
    return workspace_dir


# Global workspace directory
WORKSPACES_DIR = get_workspace_dir()