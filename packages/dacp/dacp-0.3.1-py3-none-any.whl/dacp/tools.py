import logging
from typing import Dict, Any, Callable
from pathlib import Path

# Set up logger for this module
logger = logging.getLogger("dacp.tools")

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {}


def register_tool(tool_id: str, func: Callable[..., Dict[str, Any]]) -> None:
    """Register a tool function."""
    TOOL_REGISTRY[tool_id] = func
    logger.info(f"🔧 Tool '{tool_id}' registered successfully (function: {func.__name__})")
    logger.debug(f"📊 Total registered tools: {len(TOOL_REGISTRY)}")


def run_tool(tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a registered tool with the given arguments."""
    if tool_id not in TOOL_REGISTRY:
        logger.error(f"❌ Unknown tool requested: '{tool_id}'")
        logger.debug(f"📊 Available tools: {list(TOOL_REGISTRY.keys())}")
        raise ValueError(f"Unknown tool: {tool_id}")

    tool_func = TOOL_REGISTRY[tool_id]
    logger.debug(f"🛠️  Executing tool '{tool_id}' with args: {args}")
    
    import time
    start_time = time.time()
    
    try:
        result = tool_func(**args)
        execution_time = time.time() - start_time
        logger.info(f"✅ Tool '{tool_id}' executed successfully in {execution_time:.3f}s")
        logger.debug(f"🔧 Tool result: {result}")
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Tool '{tool_id}' failed after {execution_time:.3f}s: {type(e).__name__}: {e}")
        raise


def file_writer(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file, creating parent directories if they don't exist.

    Args:
        path: File path to write to
        content: Content to write to the file

    Returns:
        Dict with success status and file path
    """
    logger.debug(f"📝 Writing to file: {path} ({len(content)} characters)")
    
    try:
        # Create parent directories if they don't exist
        parent_dir = Path(path).parent
        if not parent_dir.exists():
            logger.debug(f"📁 Creating parent directories: {parent_dir}")
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Write the content to the file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ File written successfully: {path}")
        return {
            "success": True,
            "path": path,
            "message": f"Successfully wrote {len(content)} characters to {path}",
        }
    except Exception as e:
        logger.error(f"❌ Failed to write file {path}: {type(e).__name__}: {e}")
        return {
            "success": False,
            "path": path,
            "error": str(e),
            "message": f"Failed to write to {path}: {e}",
        }


# Register the built-in file_writer tool
logger.debug("🏗️  Registering built-in tools...")
register_tool("file_writer", file_writer)
logger.debug("✅ Built-in tools registration complete")
