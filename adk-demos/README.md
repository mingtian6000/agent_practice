# ADK Demos - Agent Development Kit Examples

This directory contains examples using Google's **Agent Development Kit (ADK)** for building AI agents. These examples demonstrate how to create agents that can use tools, maintain memory, and orchestrate complex workflows.

## 📁 Structure

```
adk-demos/
├── .env.example          # Environment variables template (masked keys)
├── requirements.txt      # Python dependencies
├── simple_agent.py       # Basic agent example - START HERE
├── advanced_agent.py     # Multi-tool orchestration demo
├── README.md            # This file
└── src/
    ├── __init__.py      # Package exports
    ├── agent.py         # ADKAgent class implementation
    └── tools.py         # Custom tools (Weather, Time, Calculator, Search)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd adk-demos
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual API keys (masked in example)
# DO NOT commit .env to git!
```

**Example .env file:**
```env
# These are masked - replace with your real keys
GOOGLE_API_KEY=AIzaSyA**********************
OPENAI_API_KEY=sk-**********************
AGENT_NAME=my-assistant
AGENT_MODEL=gemini-pro
```

### 3. Run Examples

```bash
# Simple agent demo
python simple_agent.py

# Advanced multi-tool orchestration
python advanced_agent.py

# Test tools directly
python -c "from src.tools import get_all_tools; print([t.name for t in get_all_tools()])"
```

---

## 📚 What is ADK?

**ADK (Agent Development Kit)** is Google's framework for building AI agents that can:

- **🔧 Use Tools**: Call functions to interact with external systems
- **💭 Maintain Memory**: Remember conversation context
- **🧠 Plan & Reason**: Break down complex tasks into steps
- **🛡️ Safety**: Built-in guardrails and controls

### Core Concepts

#### 1. **Agent** - The Brain
An agent combines an LLM with tools and memory:

```python
from src.agent import ADKAgent
from src.tools import get_all_tools

agent = ADKAgent(
    name="my-agent",
    model="gemini-pro",
    tools=get_all_tools(),
    system_prompt="You are a helpful assistant."
)

# Use the agent
result = agent.invoke("What's the weather in New York?")
print(result['output'])
```

#### 2. **Tools** - The Hands
Tools are functions the agent can call:

```python
from src.tools import WeatherTool, CalculatorTool

# Weather tool
weather = WeatherTool()
print(weather(location="San Francisco", unit="celsius"))
# Output: Weather in San Francisco: 22°C, Partly Cloudy

# Calculator tool
calc = CalculatorTool()
print(calc(expression="15 * 23"))
# Output: 15 * 23 = 345
```

#### 3. **Memory** - The Context
Agents remember conversation history:

```python
# First message
agent.invoke("My name is Alice")

# Later - agent remembers
result = agent.invoke("What's my name?")
# Agent knows you're Alice from memory
```

---

## 🎯 Examples Explained

### Example 1: Simple Agent (`simple_agent.py`)

**What it demonstrates:**
- Basic agent initialization
- Tool registration
- Simple conversation flow
- Environment variable usage with masked keys

**Run it:**
```bash
python simple_agent.py
```

**Output:**
```
============================================================
ADK Simple Agent Demo
============================================================

Environment Setup:
  GOOGLE_API_KEY: ************abcd
  OPENAI_API_KEY: ************wxyz
  AGENT_NAME: simple-assistant
  AGENT_MODEL: gemini-pro

Agent initialized!
Name: simple-assistant
Model: gemini-pro
Tools: ['get_current_weather', 'get_current_datetime', 'calculate', 'search']

Interactive Mode (type 'exit' to quit):

User: Hello!
Agent: Hello! I'm simple-assistant. How can I help you today?

User: What's the weather like today?
Agent: [Using tool: get_current_weather] Current weather in New York: 22°C, Partly Cloudy
```

### Example 2: Custom Tools (`src/tools.py`)

**Available Tools:**

1. **WeatherTool** - Get weather for any location
   ```python
   weather = WeatherTool()
   result = weather(location="London, UK", unit="celsius")
   # Weather in London, UK: 15°C, Rainy
   ```

2. **TimeTool** - Get current date/time
   ```python
   time = TimeTool()
   result = time(timezone="UTC")
   # Current datetime (UTC): 2026-02-18 12:34:56
   ```

3. **CalculatorTool** - Perform calculations
   ```python
   calc = CalculatorTool()
   result = calc(expression="(100 - 20) * 1.5")
   # (100 - 20) * 1.5 = 120.0
   ```

4. **SearchTool** - Search for information (mock)
   ```python
   search = SearchTool()
   result = search(query="Python programming", limit=3)
   # Returns mock search results
   ```

**Test all tools:**
```bash
python src/tools.py
```

### Example 3: Advanced Orchestration (`advanced_agent.py`)

**What it demonstrates:**
- Multi-tool sequential usage
- Complex workflow handling
- Conversation memory over multiple turns
- Error handling in tools

**Run it:**
```bash
python advanced_agent.py
```

**Scenarios covered:**
1. **Trip Planning** - Weather → Time → Calculator (sequential)
2. **Memory Context** - Agent remembers user info across messages
3. **Error Handling** - Graceful handling of invalid inputs

---

## 🔑 API Keys & Environment Variables

### Masked Keys in .env.example

The `.env.example` file shows the **structure** but with masked values:

```env
# Template - replace with your actual keys
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Getting Real API Keys

1. **Google AI (Gemini)**
   - Visit: https://makersuite.google.com/app/apikey
   - Create API key
   - Copy to your `.env` file

2. **OpenAI (Optional)**
   - Visit: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy to your `.env` file

3. **Anthropic Claude (Optional)**
   - Visit: https://console.anthropic.com/settings/keys
   - Generate API key
   - Copy to your `.env` file

### Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore` (never commit it)
- Use `.env.example` as a template
- Rotate keys regularly
- Use different keys for dev/prod

❌ **DON'T:**
- Commit real API keys to git
- Share `.env` files
- Hardcode keys in source code
- Use production keys in demos

---

## 🛠️ Creating Custom Tools

Want to add your own tool? Here's the pattern:

```python
from src.tools import Tool

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does",
            parameters={
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            }
        )
    
    def __call__(self, param1: str) -> str:
        # Your tool logic here
        result = do_something(param1)
        return f"Result: {result}"

# Use it
my_tool = MyCustomTool()
agent.add_tool(my_tool)
```

---

## 🎓 Learning Path

### Beginner
1. **Start here**: `simple_agent.py`
   - Understand agent initialization
   - See how tools are registered
   - Learn about environment variables

### Intermediate
2. **Next**: `src/tools.py`
   - Study tool structure
   - Create your own tool
   - Test tool independently

### Advanced
3. **Then**: `advanced_agent.py`
   - Multi-tool orchestration
   - Complex conversation flows
   - Error handling patterns

### Expert
4. **Finally**: Modify and extend
   - Add database integration
   - Implement real APIs (not mocks)
   - Build multi-agent systems

---

## 📖 Code Patterns

### Pattern 1: Basic Agent Usage
```python
from src.agent import ADKAgent
from src.tools import get_all_tools

agent = ADKAgent(
    name="assistant",
    tools=get_all_tools()
)

response = agent.invoke("Hello!")
print(response['output'])
```

### Pattern 2: Using Specific Tools
```python
from src.tools import WeatherTool, CalculatorTool

weather = WeatherTool()
calc = CalculatorTool()

# Use independently
weather_result = weather(location="Tokyo", unit="celsius")
calc_result = calc(expression="25 * 4")
```

### Pattern 3: Conversation Memory
```python
agent = ADKAgent(name="chat-agent")

# Multi-turn conversation
agent.invoke("My name is Bob")
agent.invoke("I like Python")
agent.invoke("What's my name?")  # Agent remembers: "Bob"

# Check memory
memory = agent.get_memory()
```

---

## 🔧 Troubleshooting

**Q: "Module not found" error**
```bash
# Make sure you're in the adk-demos directory
cd adk-demos
pip install -r requirements.txt
python simple_agent.py
```

**Q: "API key not set" error**
- Check that `.env` file exists
- Verify keys are not masked (use real values)
- Make sure `python-dotenv` is installed

**Q: Tool returns mock data**
- This is expected in demo mode
- To use real data, implement actual API calls in tools
- Replace mock implementations with real API clients

**Q: How to use real LLM instead of mock?**
- Install `google-generativeai` or `openai`
- Replace MockAgent with real ADK agent
- Pass actual API keys in `.env`

---

## 📚 Resources

- **Google ADK Docs**: https://developers.google.com/agent-development-kit
- **Google AI Studio**: https://makersuite.google.com/app/apikey
- **OpenAI Docs**: https://platform.openai.com/docs
- **LangChain**: https://python.langchain.com/

---

## 🤝 Contributing

Feel free to:
- Add new tools to `src/tools.py`
- Create new agent examples
- Improve documentation
- Add tests

---

## 📄 License

MIT License - free to use for your projects!

---

**Happy Agent Building! 🤖**
