"""
Utility functions for Slidesmith.
"""

import re
import yaml
from typing import Dict, Any, Tuple


def safe_yaml_load(yaml_str: str) -> Dict[str, Any]:
    """
    Safely load YAML with special character handling.
    
    Handles common issues like:
    - Unquoted strings with colons
    - Special characters in values
    """
    if not yaml_str.strip():
        return {}
    
    # Pre-process YAML to quote problematic values
    lines = yaml_str.split('\n')
    processed_lines = []
    
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            processed_lines.append(line)
            continue
            
        # Check if line has key: value format
        if ':' in line and not line.strip().startswith('-'):
            # Split on first colon
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Check if value needs quoting
                # If value contains special chars and isn't already quoted
                if value and not (value.startswith('"') and value.endswith('"')):
                    if any(char in value for char in [':', '#', '@', '!', '|', '>', '<', '&', '*', '[', ']', '{', '}', '?']):
                        # Quote the value
                        value = f'"{value}"'
                        line = f"{parts[0]}: {value}"
                
        processed_lines.append(line)
    
    processed_yaml = '\n'.join(processed_lines)
    
    try:
        return yaml.safe_load(processed_yaml) or {}
    except yaml.YAMLError:
        # If still fails, return empty dict
        return {}


def extract_frontmatter_safe(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter from content with special character handling.
    """
    content = content.strip()
    if not content.startswith('---'):
        return {}, content
    
    # Find the end of frontmatter
    lines = content.split('\n')
    end_index = -1
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break
    
    if end_index == -1:
        return {}, content
    
    # Extract frontmatter and remaining content
    frontmatter_lines = lines[1:end_index]
    frontmatter_str = '\n'.join(frontmatter_lines)
    remaining_content = '\n'.join(lines[end_index + 1:]).strip()
    
    # Use safe YAML loader
    metadata = safe_yaml_load(frontmatter_str)
    
    return metadata, remaining_content