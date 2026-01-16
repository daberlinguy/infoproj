"""
JSON/JSONC utility functions for loading level files
Supports both standard JSON and JSON with comments (JSONC)
"""
import json
import re


def strip_json_comments(text):
    """
    Remove comments from JSON/JSONC text
    Supports both // line comments and /* block comments */
    """
    # Remove single-line comments (// ...)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    
    # Remove multi-line comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # Remove trailing commas (common in JSONC)
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    return text


def load_jsonc(filepath):
    """
    Load a JSON or JSONC file
    
    Args:
        filepath: Path to the JSON/JSONC file
    
    Returns:
        Parsed JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse as standard JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If that fails, strip comments and try again
        cleaned_content = strip_json_comments(content)
        return json.loads(cleaned_content)


def save_json(filepath, data, indent=2, allow_comments=False):
    """
    Save data to a JSON file
    
    Args:
        filepath: Path to save the file
        data: Data to save
        indent: Indentation level (default 2)
        allow_comments: If True, save as .jsonc, otherwise .json
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)
