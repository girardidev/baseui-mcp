import json
from pathlib import Path
from typing import List, Dict, Optional
from fastmcp import FastMCP

INDEX_PATH = Path(__file__).parent / "components_index.json"


def _load_components_index() -> dict:
    """
    Load the components index from components_index.json.
    
    Returns:
        dict with components data, or empty dict if file not found.
    """
    if not INDEX_PATH.exists():
        return {}
    
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _get_component(name: str) -> Optional[Dict]:
    """
    Get the full component data for a specific component.
    
    Args:
        name: The component name (case-insensitive).
        
    Returns:
        The component data dict, or None if not found.
    """
    normalized_name = name.lower().strip()
    data = COMPONENTS_INDEX.get("components", {})
    return data.get(normalized_name)


def _search_components(query: str) -> List[Dict]:
    """
    Search components by name, description, props, or dataAttributes.
    
    Args:
        query: The search query (case-insensitive).
        
    Returns:
        List of matching component data dicts.
    """
    query_lower = query.lower().strip()
    results = []
    data = COMPONENTS_INDEX.get("components", {})
    
    for comp_name, comp_data in data.items():
        # Search in name
        if query_lower in comp_name.lower():
            results.append(comp_data)
            continue
        
        # Search in description
        desc = comp_data.get("description", "")
        if query_lower in desc.lower():
            results.append(comp_data)
            continue
        
        # Search in props
        props = comp_data.get("props", [])
        if any(query_lower in prop.lower() for prop in props):
            results.append(comp_data)
            continue
        
        # Search in dataAttributes
        data_attrs = comp_data.get("dataAttributes", [])
        if any(query_lower in attr.lower() for attr in data_attrs):
            results.append(comp_data)
            continue
    
    return results


# Load the components index at startup
COMPONENTS_INDEX: dict = _load_components_index()

mcp = FastMCP(name="BaseUI MCP Server")


@mcp.tool
def list_components() -> str:
    """
    List all available BaseUI components.
    
    Returns a formatted list of all BaseUI components with their names and 
    brief descriptions. Use this to discover what components are available
    before calling get_component() for detailed documentation.
    
    Returns:
        A formatted string listing all available components with descriptions.
    """
    components = COMPONENTS_INDEX.get("components", {})
    
    if not components:
        return "No components found. Ensure the components_index.json file exists."
    
    sorted_components = sorted(components.items())
    
    lines = [
        f"Available BaseUI Components ({len(sorted_components)} total):",
        "",
    ]
    
    for name, data in sorted_components:
        desc = data.get("description", "")
        lines.append(f"  • {name} - {desc}")
    
    lines.append("")
    lines.append("Use get_component(name) to get detailed documentation for any component.")
    lines.append("Use search_components(query) to search components by name, description, props, or dataAttributes.")
    
    return "\n".join(lines)


@mcp.tool
def get_component(name: str) -> str:
    """
    Get detailed documentation for a specific BaseUI component.
    
    Returns the full documentation including description, URL, props, and
    dataAttributes for the specified component.
    
    Args:
        name: The name of the BaseUI component (e.g., 'button', 'accordion', 'checkbox').
              Case-insensitive.
    
    Returns:
        The full component documentation in Markdown format, or an error message
        if the component is not found.
    """
    normalized_name = name.lower().strip()
    components = COMPONENTS_INDEX.get("components", {})
    
    # Check if component exists
    if normalized_name not in components:
        # Find similar component names for suggestions
        suggestions = [
            comp_name for comp_name in components.keys()
            if normalized_name in comp_name or comp_name in normalized_name
        ]
        
        if not suggestions and len(normalized_name) >= 2:
            suggestions = [
                comp_name for comp_name in components.keys()
                if comp_name.startswith(normalized_name[:2])
            ]
        
        suggestion_text = ""
        if suggestions:
            suggestions = sorted(suggestions)[:5]  # Limit to 5 suggestions to minimize token usage
            suggestion_text = f"\n\nDid you mean one of these?\n  • " + "\n  • ".join(suggestions)
        
        return f"Component '{name}' not found.{suggestion_text}\n\nUse list_components() to see all available components."
    
    comp_data = components[normalized_name]
    
    lines = [
        f"# {comp_data.get('name', normalized_name)}",
        "",
        comp_data.get("description", ""),
        "",
        f"URL: {comp_data.get('url', 'N/A')}",
        "",
    ]
    
    props = comp_data.get("props", [])
    if props:
        lines.append("## Props")
        for prop in props:
            lines.append(f"  - {prop}")
        lines.append("")
    
    data_attrs = comp_data.get("dataAttributes", [])
    if data_attrs:
        lines.append("## Data Attributes")
        for attr in data_attrs:
            lines.append(f"  - {attr}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool
def search_components(query: str) -> str:
    """
    Search for BaseUI components by name, description, props, or dataAttributes.
    
    Use this to find components that match a specific prop, data attribute, or
    keyword in their description.
    
    Args:
        query: The search query (e.g., 'disabled', 'popup', 'checkbox', 'onChange').
               Case-insensitive.
    
    Returns:
        A formatted list of matching components with their names and descriptions.
    """
    if not query or not query.strip():
        return "Please provide a search query."
    
    results = _search_components(query)
    
    if not results:
        return f"No components found matching '{query}'.\n\nTry a different search term or use list_components() to see all available components."
    
    lines = [
        f"Search results for '{query}' ({len(results)} found):",
        "",
    ]
    
    for comp in results:
        lines.append(f"  • {comp.get('name', 'Unknown')} - {comp.get('description', '')}")
    
    lines.append("")
    lines.append("Use get_component(name) for detailed documentation on any result.")
    
    return "\n".join(lines)


@mcp.tool
def get_component_api(name: str) -> str:
    """
    Get the API reference for a specific BaseUI component.
    
    Returns the props and dataAttributes for the specified component,
    useful for understanding what parameters are available.
    
    Args:
        name: The name of the BaseUI component (e.g., 'button', 'accordion', 'checkbox').
              Case-insensitive.
    
    Returns:
        A formatted string with the component's props and dataAttributes,
        or an error message if the component is not found.
    """
    normalized_name = name.lower().strip()
    components = COMPONENTS_INDEX.get("components", {})
    
    # Check if component exists
    if normalized_name not in components:
        # Find similar component names for suggestions
        suggestions = [
            comp_name for comp_name in components.keys()
            if normalized_name in comp_name or comp_name in normalized_name
        ]
        
        if not suggestions and len(normalized_name) >= 2:
            suggestions = [
                comp_name for comp_name in components.keys()
                if comp_name.startswith(normalized_name[:2])
            ]
        
        suggestion_text = ""
        if suggestions:
            suggestions = sorted(suggestions)[:5]
            suggestion_text = f"\n\nDid you mean one of these?\n  • " + "\n  • ".join(suggestions)
        
        return f"Component '{name}' not found.{suggestion_text}\n\nUse list_components() to see all available components."
    
    comp_data = components[normalized_name]
    comp_name = comp_data.get("name", normalized_name)
    
    lines = [
        f"# {comp_name} API",
        "",
    ]
    
    props = comp_data.get("props", [])
    if props:
        lines.append("## Props")
        lines.append("")
        lines.append("```")
        for prop in props:
            lines.append(prop)
        lines.append("```")
        lines.append("")
    else:
        lines.append("## Props")
        lines.append("_(none)_")
        lines.append("")
    
    data_attrs = comp_data.get("dataAttributes", [])
    if data_attrs:
        lines.append("## Data Attributes")
        lines.append("")
        lines.append("```")
        for attr in data_attrs:
            lines.append(attr)
        lines.append("```")
        lines.append("")
    else:
        lines.append("## Data Attributes")
        lines.append("_(none)_")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
