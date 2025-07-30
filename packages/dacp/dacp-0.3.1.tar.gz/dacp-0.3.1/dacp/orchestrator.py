"""
DACP Orchestrator - Manages agent registration and message routing.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from .tools import run_tool, TOOL_REGISTRY
from .protocol import (
    parse_agent_response,
    is_tool_request,
    get_tool_request,
    wrap_tool_result,
    is_final_response,
    get_final_response,
)

# Set up logger for this module
logger = logging.getLogger("dacp.orchestrator")


class Agent:
    """Base class for DACP agents."""
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming message. Subclasses should override this method."""
        raise NotImplementedError("Agents must implement handle_message method")


class Orchestrator:
    """
    Central orchestrator for managing agents and routing messages.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = f"session_{int(time.time())}"
        logger.info(f"🎭 Orchestrator initialized with session ID: {self.session_id}")
    
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance that implements handle_message method
        """
        if not hasattr(agent, 'handle_message'):
            logger.error(f"❌ Agent '{agent_id}' does not implement handle_message method")
            raise ValueError(f"Agent must implement handle_message method")
        
        self.agents[agent_id] = agent
        logger.info(f"✅ Agent '{agent_id}' registered successfully (type: {type(agent).__name__})")
        logger.debug(f"📊 Total registered agents: {len(self.agents)}")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if agent was successfully unregistered, False if not found
        """
        if agent_id in self.agents:
            agent_type = type(self.agents[agent_id]).__name__
            del self.agents[agent_id]
            logger.info(f"🗑️  Agent '{agent_id}' unregistered successfully (was type: {agent_type})")
            logger.debug(f"📊 Remaining registered agents: {len(self.agents)}")
            return True
        else:
            logger.warning(f"⚠️  Attempted to unregister unknown agent: '{agent_id}'")
            return False
    
    def send_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a specific agent.
        
        Args:
            agent_id: Target agent identifier
            message: Message to send
            
        Returns:
            Response from the agent (or error if agent not found)
        """
        logger.info(f"📨 Sending message to agent '{agent_id}'")
        logger.debug(f"📋 Message content: {message}")
        
        if agent_id not in self.agents:
            error_msg = f"Agent '{agent_id}' not found"
            logger.error(f"❌ {error_msg}")
            logger.debug(f"📊 Available agents: {list(self.agents.keys())}")
            return {"error": error_msg}
        
        agent = self.agents[agent_id]
        
        try:
            start_time = time.time()
            logger.debug(f"🔄 Calling handle_message on agent '{agent_id}'")
            
            response = agent.handle_message(message)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Agent '{agent_id}' responded in {processing_time:.3f}s")
            logger.debug(f"📤 Agent response: {response}")
            
            # Check if agent requested a tool
            if is_tool_request(response):
                logger.info(f"🔧 Agent '{agent_id}' requested tool execution")
                tool_name, tool_args = get_tool_request(response)
                logger.info(f"🛠️  Executing tool: '{tool_name}' with args: {tool_args}")
                
                if tool_name in TOOL_REGISTRY:
                    try:
                        tool_start_time = time.time()
                        tool_result = run_tool(tool_name, tool_args)
                        tool_execution_time = time.time() - tool_start_time
                        
                        logger.info(f"✅ Tool '{tool_name}' executed successfully in {tool_execution_time:.3f}s")
                        logger.debug(f"🔧 Tool result: {tool_result}")
                        
                        wrapped_result = wrap_tool_result(tool_name, tool_result)
                        
                        # Log the conversation
                        self._log_conversation(agent_id, message, wrapped_result, tool_used=tool_name)
                        
                        return wrapped_result
                        
                    except Exception as e:
                        error_msg = f"Tool '{tool_name}' execution failed: {str(e)}"
                        logger.error(f"❌ {error_msg}")
                        error_response = {"error": error_msg}
                        self._log_conversation(agent_id, message, error_response, tool_used=tool_name)
                        return error_response
                else:
                    error_msg = f"Unknown tool requested: '{tool_name}'"
                    logger.error(f"❌ {error_msg}")
                    logger.debug(f"📊 Available tools: {list(TOOL_REGISTRY.keys())}")
                    error_response = {"error": error_msg}
                    self._log_conversation(agent_id, message, error_response)
                    return error_response
            
            # Log successful conversation
            self._log_conversation(agent_id, message, response)
            return response
            
        except Exception as e:
            error_msg = f"Agent '{agent_id}' error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.debug(f"🐛 Exception details: {type(e).__name__}: {e}")
            error_response = {"error": error_msg}
            self._log_conversation(agent_id, message, error_response)
            return error_response
    
    def broadcast_message(self, message: Dict[str, Any], exclude_agents: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Send a message to all registered agents (optionally excluding some).
        
        Args:
            message: Message to broadcast
            exclude_agents: List of agent IDs to exclude from broadcast
            
        Returns:
            Dict mapping agent IDs to their responses
        """
        exclude_agents = exclude_agents or []
        target_agents = [aid for aid in self.agents.keys() if aid not in exclude_agents]
        
        logger.info(f"📡 Broadcasting message to {len(target_agents)} agents")
        logger.debug(f"🎯 Target agents: {target_agents}")
        if exclude_agents:
            logger.debug(f"🚫 Excluded agents: {exclude_agents}")
        
        responses = {}
        start_time = time.time()
        
        for agent_id in target_agents:
            logger.debug(f"📨 Broadcasting to agent '{agent_id}'")
            responses[agent_id] = self.send_message(agent_id, message)
        
        broadcast_time = time.time() - start_time
        logger.info(f"✅ Broadcast completed in {broadcast_time:.3f}s")
        
        return responses
    
    def get_conversation_history(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history, optionally filtered by agent.
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            List of conversation entries
        """
        if agent_id is None:
            logger.debug(f"📚 Retrieving full conversation history ({len(self.conversation_history)} entries)")
            return self.conversation_history.copy()
        else:
            filtered_history = [
                entry for entry in self.conversation_history 
                if entry.get("agent_id") == agent_id
            ]
            logger.debug(f"📚 Retrieving conversation history for '{agent_id}' ({len(filtered_history)} entries)")
            return filtered_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        old_count = len(self.conversation_history)
        self.conversation_history.clear()
        logger.info(f"🗑️  Conversation history cleared ({old_count} entries removed)")
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dict containing session metadata
        """
        info = {
            "session_id": self.session_id,
            "registered_agents": list(self.agents.keys()),
            "conversation_count": len(self.conversation_history),
            "available_tools": list(TOOL_REGISTRY.keys())
        }
        logger.debug(f"📊 Session info requested: {info}")
        return info
    
    def _log_conversation(self, agent_id: str, message: Dict[str, Any], response: Dict[str, Any], tool_used: Optional[str] = None) -> None:
        """Log a conversation entry."""
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "message": message,
            "response": response,
            "session_id": self.session_id
        }
        
        if tool_used:
            entry["tool_used"] = tool_used
            logger.debug(f"💾 Logging conversation with tool usage: {tool_used}")
        else:
            logger.debug(f"💾 Logging conversation entry")
        
        self.conversation_history.append(entry)
