"""
Custom Tools for ADK Agent

Tools are functions that agents can call to perform specific tasks.
They extend the capabilities of the LLM beyond text generation.
"""
import json
import random
from datetime import datetime
from typing import Dict, Any, Optional


class Tool:
    """Base class for ADK tools"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    def __call__(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        raise NotImplementedError("Subclasses must implement __call__")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class WeatherTool(Tool):
    """Tool to get weather information"""
    
    def __init__(self):
        super().__init__(
            name="get_current_weather",
            description="Get the current weather for a specific location",
            parameters={
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            }
        )
    
    def __call__(self, location: str, unit: str = "celsius") -> str:
        """Mock weather data"""
        # In real implementation, this would call a weather API
        temp = random.randint(-5, 35)
        conditions = random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Snowy"])
        
        if unit == "fahrenheit":
            temp = int(temp * 9/5 + 32)
            temp_unit = "°F"
        else:
            temp_unit = "°C"
        
        return f"Weather in {location}: {temp}{temp_unit}, {conditions}"


class TimeTool(Tool):
    """Tool to get current date and time"""
    
    def __init__(self):
        super().__init__(
            name="get_current_datetime",
            description="Get the current date and time",
            parameters={
                "timezone": {
                    "type": "string",
                    "description": "Timezone (e.g., 'UTC', 'America/New_York')",
                    "default": "UTC"
                }
            }
        )
    
    def __call__(self, timezone: str = "UTC") -> str:
        """Get current datetime"""
        now = datetime.now()
        return f"Current datetime ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


class CalculatorTool(Tool):
    """Tool to perform calculations"""
    
    def __init__(self):
        super().__init__(
            name="calculate",
            description="Perform mathematical calculations",
            parameters={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate, e.g., '15 * 23' or 'sqrt(16)'"
                }
            }
        )
    
    def __call__(self, expression: str) -> str:
        """Evaluate mathematical expression"""
        try:
            # SECURITY WARNING: In production, use a safe evaluation library
            # like numexpr or ast.literal_eval instead of eval()
            # This is just for demo purposes
            
            # Basic whitelist of allowed operations
            allowed_chars = set("0123456789+-*/(). sqrt")
            if not all(c in allowed_chars for c in expression.replace(" ", "")):
                return f"Error: Invalid characters in expression. Only basic math operations allowed."
            
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"


class SearchTool(Tool):
    """Tool to search for information (mock implementation)"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for information on the internet",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5
                }
            }
        )
    
    def __call__(self, query: str, limit: int = 5) -> str:
        """Mock search results"""
        # In real implementation, this would call a search API
        mock_results = [
            f"Result 1 for '{query}': Relevant information about {query}...",
            f"Result 2 for '{query}': More details on {query}...",
            f"Result 3 for '{query}': Additional context about {query}..."
        ]
        
        return f"Search results for '{query}':\n" + "\n".join(mock_results[:limit])


def get_all_tools() -> list:
    """Factory function to get all available tools"""
    return [
        WeatherTool(),
        TimeTool(),
        CalculatorTool(),
        SearchTool()
    ]


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("ADK Tools Demo")
    print("=" * 60)
    
    # Create tools
    weather = WeatherTool()
    time = TimeTool()
    calculator = CalculatorTool()
    
    # Test weather tool
    print("\n1. Weather Tool:")
    print(weather(location="New York, NY", unit="fahrenheit"))
    
    # Test time tool
    print("\n2. Time Tool:")
    print(time(timezone="UTC"))
    
    # Test calculator tool
    print("\n3. Calculator Tool:")
    print(calculator(expression="15 * 23"))
    print(calculator(expression="100 / 4"))
    
    # Show tool definitions
    print("\n4. Tool Definitions (for LLM):")
    tools = get_all_tools()
    for tool in tools:
        print(f"\n{tool.name}:")
        print(json.dumps(tool.to_dict(), indent=2))
    
    print("\n" + "=" * 60)
