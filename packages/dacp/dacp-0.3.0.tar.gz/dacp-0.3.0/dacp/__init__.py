"""
DACP (Declarative Agent Communication Protocol)
A protocol for managing LLM/agent communications and tool function calls.
"""

from .protocol import (
    parse_agent_response,
    is_tool_request,
    get_tool_request,
    wrap_tool_result,
    is_final_response,
    get_final_response,
)
from .tools import (
    register_tool, run_tool, TOOL_REGISTRY, file_writer
)
from .llm import call_llm
from .intelligence import invoke_intelligence
from .orchestrator import Orchestrator, Agent

__version__ = "0.3.0"

__all__ = [
    "parse_agent_response",
    "is_tool_request",
    "get_tool_request",
    "wrap_tool_result",
    "is_final_response",
    "get_final_response",
    "register_tool",
    "run_tool",
    "TOOL_REGISTRY",
    "file_writer",
    "call_llm",
    "invoke_intelligence",
    "Orchestrator",
    "Agent",
]
