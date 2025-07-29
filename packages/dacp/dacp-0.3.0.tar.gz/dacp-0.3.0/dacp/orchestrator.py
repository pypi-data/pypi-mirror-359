"""
DACP Orchestrator - Manages agent registration and message routing.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
import uuid
import json
from .protocol import (
    parse_agent_response,
    is_tool_request,
    get_tool_request,
    wrap_tool_result,
    is_final_response,
    get_final_response,
)
from .tools import run_tool

log = logging.getLogger(__name__)


class Agent:
    """Base agent interface that all agents should implement."""
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages from the orchestrator."""
        raise NotImplementedError("Agents must implement handle_message method")


class Orchestrator:
    """
    Central orchestrator for managing agents and routing messages.
    Handles agent registration, message routing, and tool execution.
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance that implements handle_message method
        """
        if not hasattr(agent, 'handle_message'):
            raise ValueError(f"Agent {agent_id} must implement handle_message method")
        
        self.agents[agent_id] = agent
        log.info(f"Registered agent: {agent_id}")
        
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if agent was found and removed, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            log.info(f"Unregistered agent: {agent_id}")
            return True
        return False
        
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
        
    def list_agents(self) -> List[str]:
        """Get list of registered agent IDs."""
        return list(self.agents.keys())
        
    def send_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a specific agent.
        
        Args:
            agent_id: ID of the target agent
            message: Message to send
            
        Returns:
            Response from the agent
            
        Raises:
            ValueError: If agent_id is not found
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent = self.agents[agent_id]
        
        # Add metadata to message
        enriched_message = {
            "session_id": self.session_id,
            "timestamp": self._get_timestamp(),
            **message
        }
        
        try:
            # Send message to agent
            response = agent.handle_message(enriched_message)
            
            # Log the interaction
            self.conversation_history.append({
                "type": "message",
                "agent_id": agent_id,
                "message": enriched_message,
                "response": response,
                "timestamp": self._get_timestamp()
            })
            
            return response
            
        except Exception as e:
            error_response = {
                "error": f"Agent {agent_id} failed to handle message: {str(e)}",
                "agent_id": agent_id
            }
            log.error(f"Error sending message to agent {agent_id}: {e}")
            return error_response
            
    def broadcast_message(self, message: Dict[str, Any], exclude_agents: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Broadcast a message to all registered agents.
        
        Args:
            message: Message to broadcast
            exclude_agents: List of agent IDs to exclude from broadcast
            
        Returns:
            Dictionary mapping agent_id to response
        """
        exclude_agents = exclude_agents or []
        responses = {}
        
        for agent_id in self.agents:
            if agent_id not in exclude_agents:
                try:
                    responses[agent_id] = self.send_message(agent_id, message)
                except Exception as e:
                    responses[agent_id] = {"error": str(e)}
                    
        return responses
        
    def handle_tool_request(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool execution request.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
            
        Returns:
            Tool execution result wrapped in protocol format
        """
        try:
            result = run_tool(tool_name, args)
            return wrap_tool_result(tool_name, result)
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "args": args
            }
            return wrap_tool_result(tool_name, error_result)
            
    def process_agent_response(self, agent_id: str, response: Any) -> Dict[str, Any]:
        """
        Process an agent response, handling tool requests and final responses.
        
        Args:
            agent_id: ID of the agent that sent the response
            response: Agent response (string or dict)
            
        Returns:
            Processed response
        """
        try:
            # Parse the agent response
            parsed_response = parse_agent_response(response)
            
            # Check if it's a tool request
            if is_tool_request(parsed_response):
                tool_name, args = get_tool_request(parsed_response)
                log.info(f"Agent {agent_id} requested tool: {tool_name}")
                
                # Execute the tool
                tool_result = self.handle_tool_request(tool_name, args)
                
                # Log tool execution
                self.conversation_history.append({
                    "type": "tool_execution",
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "args": args,
                    "result": tool_result,
                    "timestamp": self._get_timestamp()
                })
                
                return tool_result
                
            # Check if it's a final response
            elif is_final_response(parsed_response):
                final_response = get_final_response(parsed_response)
                log.info(f"Agent {agent_id} sent final response")
                return final_response
                
            else:
                # Return the parsed response as-is
                return parsed_response
                
        except Exception as e:
            log.error(f"Error processing agent response from {agent_id}: {e}")
            return {
                "error": f"Failed to process response: {str(e)}",
                "original_response": response
            }
            
    def get_conversation_history(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """
        Get conversation history, optionally filtered by agent.
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            List of conversation entries
        """
        if agent_id:
            return [
                entry for entry in self.conversation_history 
                if entry.get("agent_id") == agent_id
            ]
        return self.conversation_history.copy()
        
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        log.info("Conversation history cleared")
        
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        return {
            "session_id": self.session_id,
            "registered_agents": self.list_agents(),
            "conversation_length": len(self.conversation_history),
            "timestamp": self._get_timestamp()
        }
        
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
