"""
Agent module for ADK demos
Contains agent definition and configuration
"""
from typing import List, Dict, Any


class ADKAgent:
    """
    Simple ADK-style Agent implementation
    
    This demonstrates the core concepts of ADK:
    - Tools: Functions the agent can call
    - Memory: Maintains conversation history
    - Planning: Decides which tools to use
    """
    
    def __init__(self, 
                 name: str = "adk-agent",
                 model: str = "gemini-pro",
                 tools: List[Any] = None,
                 system_prompt: str = None):
        self.name = name
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.memory = []
        
    def add_tool(self, tool):
        """Add a tool to the agent"""
        self.tools.append(tool)
        
    def invoke(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate response
        
        In real ADK, this would:
        1. Send input to LLM
        2. Parse tool calls
        3. Execute tools
        4. Return final response
        """
        self.memory.append({"role": "user", "content": user_input})
        
        # Mock LLM processing
        response = self._process_input(user_input)
        
        self.memory.append({"role": "assistant", "content": response})
        
        return {
            "output": response,
            "tools_used": [],
            "token_usage": {"prompt": 100, "completion": 50}
        }
    
    def _process_input(self, user_input: str) -> str:
        """Mock processing logic"""
        user_lower = user_input.lower()
        
        # Simple intent detection
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.name}. How can I help you today?"
        
        elif "weather" in user_lower:
            return self._use_tool("weather", user_input)
        
        elif any(word in user_lower for word in ["time", "date", "clock"]):
            return self._use_tool("time", user_input)
        
        elif any(word in user_lower for word in ["calculate", "math", "compute", "+", "-", "*", "/"]):
            return self._use_tool("calculator", user_input)
        
        elif "help" in user_lower:
            tools_list = ", ".join([t.name for t in self.tools])
            return f"I can help you with various tasks. Available tools: {tools_list}"
        
        else:
            return f"I understand you said: '{user_input}'. How can I assist you further?"
    
    def _use_tool(self, tool_type: str, input_data: str) -> str:
        """Simulate tool usage"""
        tool_map = {
            "weather": "get_current_weather",
            "time": "get_current_datetime", 
            "calculator": "calculate"
        }
        
        tool_name = tool_map.get(tool_type, "unknown")
        return f"[Using tool: {tool_name}] I would process your request about '{input_data[:30]}...'"
    
    def get_memory(self) -> List[Dict[str, str]]:
        """Retrieve conversation memory"""
        return self.memory.copy()
    
    def clear_memory(self):
        """Clear conversation history"""
        self.memory = []
