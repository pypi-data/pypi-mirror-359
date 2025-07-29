import pytest
from unittest.mock import MagicMock, patch
from dacp.orchestrator import Orchestrator, Agent
from dacp.tools import register_tool


class TestAgent:
    """Test agent implementation."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
    def handle_message(self, message):
        return {"agent_id": self.agent_id, "received": message}


class ToolRequestAgent:
    """Test agent that makes tool requests."""
    
    def handle_message(self, message):
        if message.get("request_tool"):
            return {
                "tool_request": {
                    "name": "file_writer",
                    "args": {"path": "./test.txt", "content": "Hello!"}
                }
            }
        return {"response": "normal response"}


class FinalResponseAgent:
    """Test agent that sends final responses."""
    
    def handle_message(self, message):
        return {
            "final_response": {
                "content": "This is a final response",
                "status": "completed"
            }
        }


def test_orchestrator_init():
    """Test orchestrator initialization."""
    orchestrator = Orchestrator()
    assert len(orchestrator.agents) == 0
    assert len(orchestrator.conversation_history) == 0
    assert orchestrator.session_id is not None


def test_register_agent():
    """Test agent registration."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    
    assert "test-agent" in orchestrator.agents
    assert orchestrator.agents["test-agent"] == agent


def test_register_agent_without_handle_message():
    """Test that agents must implement handle_message."""
    orchestrator = Orchestrator()
    
    class BadAgent:
        pass
    
    bad_agent = BadAgent()
    
    with pytest.raises(ValueError, match="must implement handle_message method"):
        orchestrator.register_agent("bad-agent", bad_agent)


def test_unregister_agent():
    """Test agent unregistration."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    assert "test-agent" in orchestrator.agents
    
    result = orchestrator.unregister_agent("test-agent")
    assert result is True
    assert "test-agent" not in orchestrator.agents
    
    # Try to unregister non-existent agent
    result = orchestrator.unregister_agent("non-existent")
    assert result is False


def test_get_agent():
    """Test getting agent by ID."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    
    retrieved_agent = orchestrator.get_agent("test-agent")
    assert retrieved_agent == agent
    
    non_existent = orchestrator.get_agent("non-existent")
    assert non_existent is None


def test_list_agents():
    """Test listing registered agents."""
    orchestrator = Orchestrator()
    
    assert orchestrator.list_agents() == []
    
    agent1 = TestAgent("agent1")
    agent2 = TestAgent("agent2")
    
    orchestrator.register_agent("agent1", agent1)
    orchestrator.register_agent("agent2", agent2)
    
    agents = orchestrator.list_agents()
    assert set(agents) == {"agent1", "agent2"}


def test_send_message():
    """Test sending message to agent."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    
    message = {"task": "greet", "name": "Alice"}
    response = orchestrator.send_message("test-agent", message)
    
    assert response["agent_id"] == "test-agent"
    assert "received" in response
    assert response["received"]["task"] == "greet"
    assert "session_id" in response["received"]
    assert "timestamp" in response["received"]


def test_send_message_to_nonexistent_agent():
    """Test sending message to non-existent agent."""
    orchestrator = Orchestrator()
    
    with pytest.raises(ValueError, match="Agent non-existent not found"):
        orchestrator.send_message("non-existent", {"task": "test"})


def test_send_message_agent_error():
    """Test handling agent errors."""
    orchestrator = Orchestrator()
    
    class ErrorAgent:
        def handle_message(self, message):
            raise Exception("Agent error")
    
    error_agent = ErrorAgent()
    orchestrator.register_agent("error-agent", error_agent)
    
    response = orchestrator.send_message("error-agent", {"task": "test"})
    
    assert "error" in response
    assert "Agent error-agent failed to handle message" in response["error"]


def test_broadcast_message():
    """Test broadcasting message to all agents."""
    orchestrator = Orchestrator()
    
    agent1 = TestAgent("agent1")
    agent2 = TestAgent("agent2")
    agent3 = TestAgent("agent3")
    
    orchestrator.register_agent("agent1", agent1)
    orchestrator.register_agent("agent2", agent2)
    orchestrator.register_agent("agent3", agent3)
    
    message = {"task": "broadcast"}
    responses = orchestrator.broadcast_message(message)
    
    assert len(responses) == 3
    assert all(agent_id in responses for agent_id in ["agent1", "agent2", "agent3"])
    
    # Test with exclusions
    responses = orchestrator.broadcast_message(message, exclude_agents=["agent2"])
    assert len(responses) == 2
    assert "agent1" in responses
    assert "agent3" in responses
    assert "agent2" not in responses


def test_handle_tool_request():
    """Test handling tool requests."""
    orchestrator = Orchestrator()
    
    # Register a test tool
    def test_tool(message: str) -> dict:
        return {"result": f"Processed: {message}"}
    
    register_tool("test_tool", test_tool)
    
    result = orchestrator.handle_tool_request("test_tool", {"message": "hello"})
    
    assert "tool_result" in result
    assert result["tool_result"]["name"] == "test_tool"
    assert "Processed: hello" in str(result["tool_result"]["result"])


def test_handle_tool_request_error():
    """Test handling tool request errors."""
    orchestrator = Orchestrator()
    
    result = orchestrator.handle_tool_request("nonexistent_tool", {})
    
    assert "tool_result" in result
    assert result["tool_result"]["result"]["success"] is False
    assert "error" in result["tool_result"]["result"]


def test_process_agent_response_tool_request():
    """Test processing agent response with tool request."""
    orchestrator = Orchestrator()
    agent = ToolRequestAgent()
    
    orchestrator.register_agent("tool-agent", agent)
    
    # Send message that triggers tool request
    response = orchestrator.send_message("tool-agent", {"request_tool": True})
    
    # Process the tool request response
    processed = orchestrator.process_agent_response("tool-agent", response)
    
    assert "tool_result" in processed


def test_process_agent_response_final_response():
    """Test processing agent response with final response."""
    orchestrator = Orchestrator()
    agent = FinalResponseAgent()
    
    orchestrator.register_agent("final-agent", agent)
    
    response = orchestrator.send_message("final-agent", {"task": "test"})
    processed = orchestrator.process_agent_response("final-agent", response)
    
    assert "content" in processed
    assert processed["content"] == "This is a final response"


def test_conversation_history():
    """Test conversation history tracking."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    
    # Send a message
    orchestrator.send_message("test-agent", {"task": "test1"})
    orchestrator.send_message("test-agent", {"task": "test2"})
    
    history = orchestrator.get_conversation_history()
    assert len(history) == 2
    
    # Test filtered history
    agent_history = orchestrator.get_conversation_history("test-agent")
    assert len(agent_history) == 2
    assert all(entry["agent_id"] == "test-agent" for entry in agent_history)
    
    # Test non-existent agent filter
    empty_history = orchestrator.get_conversation_history("non-existent")
    assert len(empty_history) == 0


def test_clear_history():
    """Test clearing conversation history."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    orchestrator.send_message("test-agent", {"task": "test"})
    
    assert len(orchestrator.conversation_history) == 1
    
    orchestrator.clear_history()
    assert len(orchestrator.conversation_history) == 0


def test_get_session_info():
    """Test getting session information."""
    orchestrator = Orchestrator()
    agent = TestAgent("test-agent")
    
    orchestrator.register_agent("test-agent", agent)
    orchestrator.send_message("test-agent", {"task": "test"})
    
    session_info = orchestrator.get_session_info()
    
    assert "session_id" in session_info
    assert "registered_agents" in session_info
    assert "conversation_length" in session_info
    assert "timestamp" in session_info
    
    assert session_info["registered_agents"] == ["test-agent"]
    assert session_info["conversation_length"] == 1


def test_agent_base_class():
    """Test Agent base class."""
    agent = Agent()
    
    with pytest.raises(NotImplementedError):
        agent.handle_message({"test": "message"}) 