"""
Simple ADK Agent Example
Demonstrates basic agent with tool use and conversation memory.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock ADK imports (since ADK might not be installed)
# In real usage: from google.adk import Agent, Tool
class MockAgent:
    """Mock ADK Agent for demonstration"""
    def __init__(self, name, model, tools=None, system_prompt=None):
        self.name = name
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.conversation_history = []
        
    def run(self, user_input):
        """Mock agent execution"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Simple response logic (in real ADK, this calls LLM)
        if "hello" in user_input.lower():
            response = "Hello! I'm your AI assistant. How can I help you today?"
        elif "weather" in user_input.lower():
            response = self._mock_tool_call("get_weather", user_input)
        elif "time" in user_input.lower():
            response = self._mock_tool_call("get_current_time")
        elif "calculate" in user_input.lower():
            response = self._mock_tool_call("calculator", user_input)
        else:
            response = f"I received: '{user_input}'. I'm a demo agent. Try asking about weather, time, or calculations!"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _mock_tool_call(self, tool_name, input_data=""):
        """Simulate tool calls"""
        import random
        from datetime import datetime
        
        if tool_name == "get_weather":
            cities = ["New York", "London", "Tokyo", "Sydney"]
            city = random.choice(cities)
            temp = random.randint(15, 30)
            return f"[Tool: get_weather] Current weather in {city}: {temp}°C, Partly Cloudy"
        
        elif tool_name == "get_current_time":
            return f"[Tool: get_current_time] Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        elif tool_name == "calculator":
            return f"[Tool: calculator] I'll help you calculate that! (This is a demo - real implementation would parse and compute)"
        
        return f"[Tool: {tool_name}] Tool executed successfully"


class SimpleTool:
    """Base class for tools"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement __call__")


def create_weather_tool():
    """Create a weather tool"""
    return SimpleTool(
        name="get_weather",
        description="Get current weather for a location"
    )


def create_time_tool():
    """Create a time tool"""
    return SimpleTool(
        name="get_current_time",
        description="Get current date and time"
    )


def create_calculator_tool():
    """Create a calculator tool"""
    return SimpleTool(
        name="calculator",
        description="Perform mathematical calculations"
    )


def main():
    """Main function to run the agent"""
    print("=" * 60)
    print("ADK Simple Agent Demo")
    print("=" * 60)
    
    # Check for API keys (masked)
    google_key = os.getenv("GOOGLE_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    print("\nEnvironment Setup:")
    print(f"  GOOGLE_API_KEY: {'*' * 8}{google_key[-4:] if google_key else 'NOT SET'}")
    print(f"  OPENAI_API_KEY: {'*' * 8}{openai_key[-4:] if openai_key else 'NOT SET'}")
    print(f"  AGENT_NAME: {os.getenv('AGENT_NAME', 'simple-assistant')}")
    print(f"  AGENT_MODEL: {os.getenv('AGENT_MODEL', 'gemini-pro')}")
    
    # Create tools
    tools = [
        create_weather_tool(),
        create_time_tool(),
        create_calculator_tool()
    ]
    
    # Initialize agent
    agent = MockAgent(
        name=os.getenv("AGENT_NAME", "simple-assistant"),
        model=os.getenv("AGENT_MODEL", "gemini-pro"),
        tools=tools,
        system_prompt="You are a helpful AI assistant with access to weather, time, and calculator tools."
    )
    
    print("\n" + "=" * 60)
    print("Agent initialized!")
    print(f"Name: {agent.name}")
    print(f"Model: {agent.model}")
    print(f"Tools: {[t.name for t in agent.tools]}")
    print("=" * 60)
    
    # Interactive loop
    print("\nInteractive Mode (type 'exit' to quit):\n")
    
    test_inputs = [
        "Hello!",
        "What's the weather like today?",
        "What time is it now?",
        "Can you calculate 15 * 23?",
        "Tell me a joke"
    ]
    
    for user_input in test_inputs:
        print(f"User: {user_input}")
        response = agent.run(user_input)
        print(f"Agent: {response}\n")
    
    print("=" * 60)
    print("Demo completed!")
    print("\nConversation History:")
    for msg in agent.conversation_history:
        print(f"  {msg['role'].upper()}: {msg['content'][:50]}...")
    print("=" * 60)


if __name__ == "__main__":
    main()
