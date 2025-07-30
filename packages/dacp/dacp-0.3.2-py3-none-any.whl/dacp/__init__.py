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
from .tools import register_tool, execute_tool, TOOL_REGISTRY, file_writer
from .llm import call_llm
from .intelligence import invoke_intelligence
from .orchestrator import Orchestrator, Agent
from .logging_config import (
    setup_dacp_logging,
    enable_debug_logging,
    enable_info_logging,
    enable_quiet_logging,
    set_dacp_log_level,
    disable_dacp_logging,
    enable_dacp_logging,
)

__version__ = "0.3.0"

__all__ = [
    # Protocol functions
    "parse_agent_response",
    "is_tool_request",
    "get_tool_request",
    "wrap_tool_result",
    "is_final_response",
    "get_final_response",
    # Tool functions
    "register_tool",
    "execute_tool",
    "TOOL_REGISTRY",
    "file_writer",
    # LLM functions
    "call_llm",
    "invoke_intelligence",
    # Agent orchestration
    "Orchestrator",
    "Agent",
    # Logging configuration
    "setup_dacp_logging",
    "enable_debug_logging",
    "enable_info_logging",
    "enable_quiet_logging",
    "set_dacp_log_level",
    "disable_dacp_logging",
    "enable_dacp_logging",
]
