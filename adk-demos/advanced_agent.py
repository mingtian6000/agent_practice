"""
Advanced ADK Agent Example
Demonstrates multi-tool orchestration and complex workflows
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.agent import ADKAgent
from src.tools import get_all_tools


def demonstrate_tool_orchestration():
    """
    Demonstrates how an agent can use multiple tools in sequence
    to solve complex problems
    """
    print("=" * 70)
    print("Advanced ADK Agent - Multi-Tool Orchestration Demo")
    print("=" * 70)
    
    # Create agent with all tools
    tools = get_all_tools()
    agent = ADKAgent(
        name="orchestrator-agent",
        model="gemini-pro",
        tools=tools,
        system_prompt="""You are an advanced AI assistant that can orchestrate multiple tools.
        When given a complex request, break it down and use the appropriate tools."""
    )
    
    print(f"\nAgent: {agent.name}")
    print(f"Model: {agent.model}")
    print(f"Tools: {[t.name for t in tools]}")
    
    # Example 1: Sequential tool usage
    print("\n" + "-" * 70)
    print("Example 1: Planning a Trip")
    print("-" * 70)
    
    queries = [
        "What's the weather in San Francisco?",
        "What time is it there now?",
        "If I have $500 and the hotel costs $120 per night, how many nights can I stay?"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        result = agent.invoke(query)
        print(f"Agent: {result['output']}")
    
    # Example 2: Memory and context
    print("\n" + "-" * 70)
    print("Example 2: Conversation Memory")
    print("-" * 70)
    
    context_queries = [
        "My name is Alice",
        "What's my name?",
        "What's the weather like?",
        "What was my name again?"
    ]
    
    for query in context_queries:
        print(f"\nUser: {query}")
        result = agent.invoke(query)
        print(f"Agent: {result['output']}")
    
    # Show conversation history
    print("\n" + "-" * 70)
    print("Conversation Memory:")
    print("-" * 70)
    memory = agent.get_memory()
    for i, msg in enumerate(memory, 1):
        role = msg['role'].upper()
        content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
        print(f"{i}. {role}: {content}")
    
    # Example 3: Error handling
    print("\n" + "-" * 70)
    print("Example 3: Tool Parameter Handling")
    print("-" * 70)
    
    test_queries = [
        "Calculate 100 / 0",  # Division by zero
        "Search for Python programming",  # Search tool
        "What's 15 * 23 + 8?",  # Complex calculation
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        result = agent.invoke(query)
        print(f"Agent: {result['output']}")
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)


def demonstrate_configuration():
    """Show different configuration options"""
    print("\n" + "=" * 70)
    print("Agent Configuration Examples")
    print("=" * 70)
    
    # Minimal configuration
    minimal_agent = ADKAgent(name="minimal")
    print(f"\n1. Minimal Agent:")
    print(f"   Name: {minimal_agent.name}")
    print(f"   Tools: {len(minimal_agent.tools)}")
    
    # Full configuration
    full_agent = ADKAgent(
        name="full-featured",
        model="gemini-pro",
        tools=get_all_tools(),
        system_prompt="You are a specialized agent for data analysis."
    )
    print(f"\n2. Full-Featured Agent:")
    print(f"   Name: {full_agent.name}")
    print(f"   Model: {full_agent.model}")
    print(f"   Tools: {len(full_agent.tools)}")
    print(f"   Tool Names: {[t.name for t in full_agent.tools]}")


if __name__ == "__main__":
    # Check environment
    print("Environment Check:")
    print(f"  GOOGLE_API_KEY: {'*' * 8}{os.getenv('GOOGLE_API_KEY', 'NOT SET')[-4:] if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}")
    print(f"  Working Directory: {os.getcwd()}")
    print()
    
    # Run demonstrations
    demonstrate_configuration()
    print()
    demonstrate_tool_orchestration()
