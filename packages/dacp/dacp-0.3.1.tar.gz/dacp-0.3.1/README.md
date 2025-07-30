# DACP - Declarative Agent Communication Protocol

A Python library for managing LLM/agent communications and tool function calls following the OAS Open Agent Specification.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import dacp

# Create an orchestrator to manage agents
orchestrator = dacp.Orchestrator()

# Create and register an agent
class MyAgent:
    def handle_message(self, message):
        return {"response": f"Hello {message.get('name', 'World')}!"}

agent = MyAgent()
orchestrator.register_agent("my-agent", agent)

# Send a message to the agent
response = orchestrator.send_message("my-agent", {"name": "Alice"})
print(response)  # {"response": "Hello Alice!"}

# Use built-in tools
result = dacp.file_writer("./output/greeting.txt", "Hello, World!")
print(result["message"])  # "Successfully wrote 13 characters to ./output/greeting.txt"

# Use intelligence providers (supports multiple LLM providers)
intelligence_config = {
    "engine": "anthropic",
    "model": "claude-3-haiku-20240307",
    "api_key": "your-api-key"  # or set ANTHROPIC_API_KEY env var
}
response = dacp.invoke_intelligence("What is the weather like today?", intelligence_config)

# Or use the legacy call_llm function for OpenAI
response = dacp.call_llm("What is the weather like today?")
```

## Features

- **Agent Orchestration**: Central management of multiple agents with message routing
- **Tool Registry**: Register and manage custom tools for LLM agents
- **Built-in Tools**: Includes a `file_writer` tool that automatically creates parent directories
- **LLM Integration**: Built-in support for OpenAI models (extensible)
- **Protocol Parsing**: Parse and validate agent responses
- **Tool Execution**: Safe execution of registered tools
- **Conversation History**: Track and query agent interactions
- **OAS Compliance**: Follows Open Agent Specification standards

## API Reference

### Orchestrator

- `Orchestrator()`: Create a new orchestrator instance
- `register_agent(agent_id: str, agent) -> None`: Register an agent
- `unregister_agent(agent_id: str) -> bool`: Remove an agent
- `send_message(agent_id: str, message: Dict) -> Dict`: Send message to specific agent
- `broadcast_message(message: Dict, exclude_agents: List[str] = None) -> Dict`: Send message to all agents
- `get_conversation_history(agent_id: str = None) -> List[Dict]`: Get conversation history
- `clear_history() -> None`: Clear conversation history
- `get_session_info() -> Dict`: Get current session information

### Tools

- `register_tool(tool_id: str, func)`: Register a new tool
- `run_tool(tool_id: str, args: Dict) -> dict`: Execute a registered tool
- `TOOL_REGISTRY`: Access the current tool registry
- `file_writer(path: str, content: str) -> dict`: Write content to file, creating directories automatically

### Intelligence (Multi-Provider LLM Support)

- `invoke_intelligence(prompt: str, config: dict) -> str`: Call any supported LLM provider
- `validate_config(config: dict) -> bool`: Validate intelligence configuration
- `get_supported_engines() -> list`: Get list of supported engines

### LLM (Legacy)

- `call_llm(prompt: str, model: str = "gpt-4") -> str`: Call OpenAI (legacy function)

### Logging

- `enable_info_logging(log_file: str = None) -> None`: Enable info-level logging with emoji format
- `enable_debug_logging(log_file: str = None) -> None`: Enable debug logging with detailed format  
- `enable_quiet_logging() -> None`: Enable only error and critical logging
- `setup_dacp_logging(level, format_style, include_timestamp, log_file) -> None`: Custom logging setup
- `set_dacp_log_level(level: str) -> None`: Change log level dynamically
- `disable_dacp_logging() -> None`: Disable all DACP logging
- `enable_dacp_logging() -> None`: Re-enable DACP logging

### Protocol

- `parse_agent_response(response: str | dict) -> dict`: Parse agent response
- `is_tool_request(msg: dict) -> bool`: Check if message is a tool request
- `get_tool_request(msg: dict) -> tuple[str, dict]`: Extract tool request details
- `wrap_tool_result(name: str, result: dict) -> dict`: Wrap tool result for agent
- `is_final_response(msg: dict) -> bool`: Check if message is a final response
- `get_final_response(msg: dict) -> dict`: Extract final response

## Agent Development

### Creating an Agent

Agents must implement a `handle_message` method:

```python
import dacp

class GreetingAgent:
    def handle_message(self, message):
        name = message.get("name", "World")
        task = message.get("task")
        
        if task == "greet":
            return {"response": f"Hello, {name}!"}
        elif task == "farewell":
            return {"response": f"Goodbye, {name}!"}
        else:
            return {"error": f"Unknown task: {task}"}

# Register the agent
orchestrator = dacp.Orchestrator()
agent = GreetingAgent()
orchestrator.register_agent("greeter", agent)

# Use the agent
response = orchestrator.send_message("greeter", {
    "task": "greet", 
    "name": "Alice"
})
print(response)  # {"response": "Hello, Alice!"}
```

### Agent Base Class

You can also inherit from the `Agent` base class:

```python
import dacp

class MyAgent(dacp.Agent):
    def handle_message(self, message):
        return {"processed": message}
```

### Tool Requests from Agents

Agents can request tool execution by returning properly formatted responses:

```python
class ToolUsingAgent:
    def handle_message(self, message):
        if message.get("task") == "write_file":
            return {
                "tool_request": {
                    "name": "file_writer",
                    "args": {
                        "path": "./output/agent_file.txt",
                        "content": "Hello from agent!"
                    }
                }
            }
        return {"response": "Task completed"}

# The orchestrator will automatically execute the tool and return results
orchestrator = dacp.Orchestrator()
agent = ToolUsingAgent()
orchestrator.register_agent("file-agent", agent)

response = orchestrator.send_message("file-agent", {"task": "write_file"})
# Tool will be executed automatically
```

## Intelligence Configuration

DACP supports multiple LLM providers through the `invoke_intelligence` function. Configure different providers using a configuration dictionary:

### OpenAI

```python
import dacp

openai_config = {
    "engine": "openai",
    "model": "gpt-4",  # or "gpt-3.5-turbo", "gpt-4-turbo", etc.
    "api_key": "your-openai-key",  # or set OPENAI_API_KEY env var
    "endpoint": "https://api.openai.com/v1",  # optional, uses default
    "temperature": 0.7,  # optional, default 0.7
    "max_tokens": 150   # optional, default 150
}

response = dacp.invoke_intelligence("Explain quantum computing", openai_config)
```

### Anthropic (Claude)

```python
anthropic_config = {
    "engine": "anthropic", 
    "model": "claude-3-haiku-20240307",  # or other Claude models
    "api_key": "your-anthropic-key",  # or set ANTHROPIC_API_KEY env var
    "endpoint": "https://api.anthropic.com",  # optional, uses default
    "temperature": 0.7,
    "max_tokens": 150
}

response = dacp.invoke_intelligence("Write a poem about AI", anthropic_config)
```

### Azure OpenAI

```python
azure_config = {
    "engine": "azure",
    "model": "gpt-4",  # Your deployed model name
    "api_key": "your-azure-key",  # or set AZURE_OPENAI_API_KEY env var  
    "endpoint": "https://your-resource.openai.azure.com",  # or set AZURE_OPENAI_ENDPOINT env var
    "api_version": "2024-02-01"  # optional, default provided
}

response = dacp.invoke_intelligence("Analyze this data", azure_config)
```

### Local LLMs (Ollama, etc.)

```python
# For Ollama (default local setup)
local_config = {
    "engine": "local",
    "model": "llama2",  # or any model available in Ollama
    "endpoint": "http://localhost:11434/api/generate",  # Ollama default
    "temperature": 0.7,
    "max_tokens": 150
}

# For custom local APIs
custom_local_config = {
    "engine": "local", 
    "model": "custom-model",
    "endpoint": "http://localhost:8080/generate",  # Your API endpoint
    "temperature": 0.7,
    "max_tokens": 150
}

response = dacp.invoke_intelligence("Tell me a story", local_config)
```

### Configuration from OAS YAML

You can load configuration from OAS (Open Agent Specification) YAML files:

```python
import yaml
import dacp

# Load config from YAML file
with open('agent_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

intelligence_config = config.get('intelligence', {})
response = dacp.invoke_intelligence("Hello, AI!", intelligence_config)
```

### Installation for Different Providers

Install optional dependencies for the providers you need:

```bash
# For OpenAI
pip install dacp[openai]

# For Anthropic  
pip install dacp[anthropic]

# For all providers
pip install dacp[all]

# For local providers (requests is already included in base install)
pip install dacp[local]
```

## Built-in Tools

### file_writer

The `file_writer` tool automatically creates parent directories and writes content to files:

```python
import dacp

# This will create the ./output/ directory if it doesn't exist
result = dacp.file_writer("./output/file.txt", "Hello, World!")

if result["success"]:
    print(f"File written: {result['path']}")
    print(f"Message: {result['message']}")
else:
    print(f"Error: {result['error']}")
```

**Features:**
- ✅ Automatically creates parent directories
- ✅ Handles Unicode content properly
- ✅ Returns detailed success/error information
- ✅ Safe error handling

## Logging

DACP includes comprehensive logging to help you monitor agent operations, tool executions, and intelligence calls.

### Quick Setup

```python
import dacp

# Enable info-level logging with emoji format (recommended for production)
dacp.enable_info_logging()

# Enable debug logging for development (shows detailed information)
dacp.enable_debug_logging()

# Enable quiet logging (errors only)
dacp.enable_quiet_logging()
```

### Custom Configuration

```python
# Full control over logging configuration
dacp.setup_dacp_logging(
    level="INFO",                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format_style="emoji",            # "simple", "detailed", "emoji"
    include_timestamp=True,          # Include timestamps
    log_file="dacp.log"              # Optional: also log to file
)

# Change log level dynamically
dacp.set_dacp_log_level("DEBUG")

# Disable/enable logging
dacp.disable_dacp_logging()
dacp.enable_dacp_logging()
```

### What Gets Logged

With logging enabled, you'll see:

- **🎭 Agent Registration**: When agents are registered/unregistered
- **📨 Message Routing**: Messages sent to agents and broadcast operations  
- **🔧 Tool Execution**: Tool calls, execution time, and results
- **🧠 Intelligence Calls**: LLM provider calls, configuration, and performance
- **❌ Errors**: Detailed error information with context
- **📊 Performance**: Execution times for operations

### Log Format Examples

**Emoji Format** (clean, production-friendly):
```
2025-07-02 09:54:58 - 🎭 Orchestrator initialized with session ID: session_1751414098
2025-07-02 09:54:58 - ✅ Agent 'demo-agent' registered successfully (type: MyAgent)
2025-07-02 09:54:58 - 📨 Sending message to agent 'demo-agent'
2025-07-02 09:54:58 - 🔧 Agent 'demo-agent' requested tool execution
2025-07-02 09:54:58 - 🛠️  Executing tool: 'file_writer' with args: {...}
2025-07-02 09:54:58 - ✅ Tool 'file_writer' executed successfully in 0.001s
```

**Detailed Format** (development/debugging):
```
2025-07-02 09:54:58 - dacp.orchestrator:89 - INFO - 📨 Sending message to agent 'demo-agent'
2025-07-02 09:54:58 - dacp.orchestrator:90 - DEBUG - 📋 Message content: {'task': 'greet'}
2025-07-02 09:54:58 - dacp.tools:26 - DEBUG - 🛠️  Executing tool 'file_writer' with args: {...}
```

### Example Usage

```python
import dacp

# Enable logging
dacp.enable_info_logging()

# Create and use components - logging happens automatically
orchestrator = dacp.Orchestrator()
agent = MyAgent()
orchestrator.register_agent("my-agent", agent)

# This will log the message sending, tool execution, etc.
response = orchestrator.send_message("my-agent", {"task": "process"})
```

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License
