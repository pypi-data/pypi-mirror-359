from dacp.orchestrator import Orchestrator

def main():
    orchestrator = Orchestrator()

    # Agent registers itself with the orchestrator
    hello_agent = HelloWorldAgent("hello_agent", orchestrator)

    # Orchestrator sends a message to the agent and prints the response
    input_message = {"name": "Alice"}
    response = orchestrator.call_agent("hello_agent", input_message)
    print("Orchestrator received:", response)

if __name__ == "__main__":
    main()
