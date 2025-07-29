from typing import Dict, Any, Callable
from pathlib import Path

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {}


def register_tool(tool_id: str, func: Callable[..., Dict[str, Any]]) -> None:
    """Register a tool function."""
    TOOL_REGISTRY[tool_id] = func


def run_tool(tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a registered tool with the given arguments."""
    if tool_id not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_id}")

    tool_func = TOOL_REGISTRY[tool_id]
    return tool_func(**args)


def file_writer(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file, creating parent directories if they don't exist.

    Args:
        path: File path to write to
        content: Content to write to the file

    Returns:
        Dict with success status and file path
    """
    try:
        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Write the content to the file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "path": path,
            "message": f"Successfully wrote {len(content)} characters to {path}",
        }
    except Exception as e:
        return {
            "success": False,
            "path": path,
            "error": str(e),
            "message": f"Failed to write to {path}: {e}",
        }


# Register the built-in file_writer tool
register_tool("file_writer", file_writer)
