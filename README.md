# AI Practice - LangGraph Demos & CI/CD Automation

This repository contains practical examples of using **LangGraph** for building AI-powered workflows, from simple demos to complex CI/CD automation agents.

## 📁 Repository Structure

```
agent_practice/
├── simple-demos/          # Basic LangGraph examples
│   ├── hello_world.py     # Your first graph
│   ├── conditional_graph.py  # Graphs with loops
│   ├── chatbot.py         # Simple chatbot with tools
│   └── annotated_demo.py  # Using Annotated types with reducers
│
├── langgraph-demos/       # Production-grade examples
│   └── cicd_agent/        # CI/CD automation agent
│       ├── state.py
│       ├── graph.py
│       ├── nodes/
│       │   ├── discovery.py
│       │   ├── validators.py
│       │   ├── fixers.py
│       │   ├── decision.py
│       │   └── release.py
│       └── utils/
│
└── README.md              # This file
```

---

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/mingtian6000/agent_practice.git
cd agent_practice

# Install dependencies
pip install -r requirements.txt

# For CI/CD agent only
cd langgraph-demos/cicd_agent
pip install -r requirements.txt
```

### Quick Start - Run Simple Demos

```bash
cd simple-demos

# Run basic hello world
python hello_world.py

# Run conditional graph with loops
python conditional_graph.py

# Run chatbot demo
python chatbot.py

# Run annotated types demo (shows reducers)
python annotated_demo.py
```

---

## 📚 What is LangGraph?

**LangGraph** is a library for building stateful, multi-step workflows using graph-based structures. It's built on top of LangChain and enables you to create complex AI applications with:

- **Stateful execution** - Memory persists across steps
- **Conditional logic** - Dynamic routing based on state
- **Loops & cycles** - Repeating steps until conditions are met
- **Parallel execution** - Multiple nodes running simultaneously

### Core Concepts

#### 1. **State** - Shared Memory
The state is a dictionary that flows through your graph, carrying data between nodes.

```python
from typing import TypedDict

class GraphState(TypedDict):
    message: str
    count: int

# State flows: START → Node A → Node B → END
# Each node reads/writes to the same state object
```

#### 2. **Nodes** - Processing Units
Nodes are Python functions that receive state, process it, and return updated state.

```python
def greeting_node(state: GraphState) -> GraphState:
    state["message"] = "Hello World!"
    state["count"] = state.get("count", 0) + 1
    return state  # Return updated state
```

#### 3. **Edges** - Flow Control
Edges connect nodes and define execution order:
- **Sequential**: A → B → C
- **Conditional**: A → [B if X else C]
- **Parallel**: A → [B, C, D] simultaneously

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(GraphState)
workflow.add_node("greeting", greeting_node)
workflow.add_edge(START, "greeting")
workflow.add_edge("greeting", END)

app = workflow.compile()
result = app.invoke({"message": "", "count": 0})
```

#### 4. **Annotated Types** - State Reducers (Advanced)

`Annotated` lets you control how state fields are merged when multiple nodes update them. This is crucial for parallel execution and message accumulation.

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Custom reducers
def concat_lists(existing: list, new: list) -> list:
    """Merge two lists by concatenation"""
    return existing + new

def sum_numbers(existing: int, new: int) -> int:
    """Merge two numbers by addition"""
    return existing + new

class AnnotatedState(TypedDict):
    # Built-in reducer: accumulates messages
    messages: Annotated[list, add_messages]
    
    # Custom reducer: concatenates lists
    logs: Annotated[list, concat_lists]
    
    # Custom reducer: sums numbers
    total_count: Annotated[int, sum_numbers]
    
    # No reducer: overwrites (default behavior)
    current_status: str
```

**How it works:**

When nodes run in parallel or sequence:

```python
def node_a(state):
    state["messages"] = [HumanMessage(content="From A")]
    state["logs"] = ["A executed"]
    state["total_count"] = 1
    return state

def node_b(state):
    state["messages"] = [AIMessage(content="From B")]
    state["logs"] = ["B executed"]
    state["total_count"] = 1
    return state

# After both nodes run:
# messages: [HumanMessage("From A"), AIMessage("From B")]  # ← Accumulated!
# logs: ["A executed", "B executed"]                       # ← Concatenated!
# total_count: 2                                           # ← Summed!
# current_status: Only shows last node's value             # ← Overwritten
```

**Common reducers:**

| Reducer | Behavior | Use Case |
|---------|----------|----------|
| `add_messages` | Appends messages | Chat history |
| `operator.add` | Sums numbers | Counters |
| Custom function | Your logic | Any merge strategy |

**Run the demo:**
```bash
cd simple-demos
python annotated_demo.py
```

---

## 🎯 Simple Demos Explained

### 1. Hello World (`simple-demos/hello_world.py`)

**Concept**: Basic graph with sequential nodes

```python
# Define state
class GraphState(TypedDict):
    message: str
    count: int

# Define nodes
def greeting_node(state):
    state["message"] = "Hello! Processing item 0"
    state["count"] += 1
    return state

# Build graph
workflow = StateGraph(GraphState)
workflow.add_node("greeting", greeting_node)
workflow.add_edge(START, "greeting")
workflow.add_edge("greeting", END)

# Run
app = workflow.compile()
result = app.invoke({"message": "", "count": 0})
print(result)  # {'message': 'Hello! Processing item 0', 'count': 1}
```

**What you'll learn**:
- Defining state with TypedDict
- Creating simple nodes
- Building linear workflows

### 2. Conditional Graph (`simple-demos/conditional_graph.py`)

**Concept**: Graphs with loops and conditional routing

```python
def should_continue(state):
    """Decide whether to loop or end"""
    if len(state["messages"]) < 3:
        return "continue"  # Keep looping
    return "end"  # Exit loop

# Build with conditional edges
workflow.add_conditional_edges(
    "node_b",
    should_continue,
    {
        "continue": "node_c",  # Loop back
        "end": END             # Finish
    }
)
workflow.add_edge("node_c", "node_a")  # Creates cycle
```

**What you'll learn**:
- Conditional routing with `add_conditional_edges`
- Creating loops and cycles
- Loop termination conditions

### 3. Chatbot (`simple-demos/chatbot.py`)

**Concept**: Simple AI agent with tool use

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# State tracks conversation
class ChatState(TypedDict):
    messages: list

# Node processes messages
# Uses LangChain tools for calculations
```

**What you'll learn**:
- Integrating LangChain tools
- Maintaining conversation state
- Simple agent patterns

---

## 🏭 Production Example: CI/CD Agent

The **CI/CD Agent** (`langgraph-demos/cicd_agent/`) demonstrates how to build a complex, production-grade workflow using LangGraph.

### What It Does

Automatically validates and releases infrastructure code:

1. **Discovery** - Finds all `.tf`, `Dockerfile`, and Helm files
2. **Validation** - Runs multiple validators in parallel
3. **Auto-Fix** - Attempts to fix errors (up to 3 times)
4. **Release** - Deploys validated code

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CI/CD AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  START                                                      │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────┐                                        │
│  │  Discover Files │◄── Scan directories for configs        │
│  └────────┬────────┘                                        │
│           │                                                 │
│     ┌─────┴─────┬───────────┐                              │
│     ▼           ▼           ▼                              │
│  ┌──────┐  ┌────────┐  ┌────────┐                         │
│  │Valid.│  │Valid.  │  │Valid.  │                         │
│  │TF    │  │Docker  │  │Helm    │  ← Parallel execution   │
│  └──┬───┘  └───┬────┘  └───┬────┘                         │
│     │          │           │                               │
│     └──────────┼───────────┘                               │
│                ▼                                           │
│  ┌─────────────────────┐                                   │
│  │  Collect All Errors │◄── Wait for all validations       │
│  └──────────┬──────────┘                                   │
│             │                                              │
│             ▼                                              │
│  ┌─────────────────────┐                                   │
│  │   Decision Point    │◄── All passed?                    │
│  └──────────┬──────────┘                                   │
│             │                                              │
│    ┌────────┴────────┬──────────────┐                     │
│    ▼                 ▼              ▼                     │
│  Release          Fix           Fail (max retries)       │
│    │               │                                      │
│    │               └─► Re-validate ─┘ (loop 3x max)      │
│    ▼                                                       │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐            │
│  │ Docker  │ ───► │  Helm   │ ───► │Terraform│            │
│  │ Release │      │ Release │      │ Release │            │
│  └─────────┘      └─────────┘      └─────────┘            │
│                                         │                  │
│                                         ▼                  │
│                                      SUCCESS               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How LangGraph Powers the CI/CD Agent

#### 1. **State Management**

The `CICDState` tracks everything:

```python
class CICDState(TypedDict):
    user_paths: List[str]              # Input paths
    files: Dict[str, List[str]]        # Discovered files
    validation_results: Dict           # All validation results
    fix_attempts: Dict                 # Track retry counts
    docker_images_built: List[str]     # Release tracking
    helm_charts_released: List[str]
    terraform_applied: bool
    status: str                        # Current state
```

#### 2. **Parallel Validation**

All validators run simultaneously:

```python
workflow.add_edge("discover", "validate_terraform")
workflow.add_edge("discover", "validate_docker")
workflow.add_edge("discover", "validate_helm")

# All three validators execute in parallel
# Graph waits for ALL to complete before "collect_errors"
```

#### 3. **Conditional Logic with Retry Loop**

Smart routing based on validation results:

```python
def decide_next_action(state: CICDState) -> str:
    total_errors = sum(len(errs) for errs in state["collected_errors"].values())
    
    if total_errors == 0:
        return "release"  # All good, deploy!
    
    # Check if we can retry
    for file_type in ["terraform", "docker", "helm"]:
        attempts = state["fix_attempts"].get(file_type, {}).get("attempts", 0)
        if attempts < 3:  # Max 3 attempts
            return "fix"  # Try to fix
    
    return "fail"  # Max retries exceeded

workflow.add_conditional_edges(
    "decide",
    decide_next_action,
    {
        "release": "prepare_release",
        "fix": "fix_terraform",
        "fail": "fail"
    }
)
```

#### 4. **Stateful Retry Mechanism**

Loop back to validation after fixes:

```python
# Fix chain
workflow.add_edge("fix_terraform", "fix_docker")
workflow.add_edge("fix_docker", "fix_helm")

# Loop back to validation
workflow.add_edge("fix_helm", "validate_terraform")
# This creates: Fix → Re-validate → (Fix again if needed)
```

### Running the CI/CD Agent

```bash
cd langgraph-demos/cicd_agent

# Install dependencies
pip install -r requirements.txt

# Run with your infrastructure code
python -m main ./terraform ./docker ./helm

# Or programmatically
from cicd_agent import run_cicd_agent

result = run_cicd_agent(
    user_paths=["./my-terraform", "./my-docker"],
    max_fix_attempts=3
)

print(f"Status: {result['status']}")
print(f"Images built: {result['docker_images_built']}")
print(f"Terraform applied: {result['terraform_applied']}")
```

### Workflow Visualization

The agent includes automatic workflow visualization:

```bash
cd langgraph-demos/cicd_agent
python generate_workflow_graph.py
```

Generates:
- `cicd_workflow.mmd` - Mermaid diagram (view on GitHub)
- `cicd_workflow.dot` - Graphviz source
- `WORKFLOW_README.md` - Detailed documentation

---

## 🎓 Learning Path

### Beginner
1. **Start here**: `simple-demos/hello_world.py`
   - Understand state and nodes
   - Run your first graph

2. **Next**: `simple-demos/conditional_graph.py`
   - Learn conditional edges
   - Understand loops

### Intermediate
3. **Try**: `simple-demos/chatbot.py`
   - Integrate with LangChain
   - Use tools

4. **Study**: `simple-demos/annotated_demo.py`
   - Learn about state reducers
   - Understand how parallel nodes merge state
   - Master Annotated types

5. **Read**: CI/CD agent code
   - Study the structure
   - Understand parallel execution
   - See Annotated in production use

### Advanced
5. **Modify**: CI/CD agent
   - Add new validators
   - Customize fix strategies
   - Add new release targets

---

## 🔑 Key Patterns

### Pattern 1: State Passing
```python
def node_a(state):
    state["data"] = "from A"
    return state

def node_b(state):
    print(state["data"])  # "from A"
    return state
```

### Pattern 2: Conditional Routing
```python
def router(state):
    if state["condition"]:
        return "path_a"
    return "path_b"

workflow.add_conditional_edges(
    "node",
    router,
    {"path_a": "node_a", "path_b": "node_b"}
)
```

### Pattern 3: Parallel Execution
```python
# These all run simultaneously
workflow.add_edge("start", "node_a")
workflow.add_edge("start", "node_b")
workflow.add_edge("start", "node_c")

# This waits for ALL to complete
workflow.add_edge("node_a", "collector")
workflow.add_edge("node_b", "collector")
workflow.add_edge("node_c", "collector")
```

### Pattern 4: Retry Loops
```python
# Forward edges
workflow.add_edge("validator", "decider")

# Conditional: if failed, go to fixer
workflow.add_conditional_edges(
    "decider",
    lambda s: "fix" if s["failed"] else "proceed",
    {"fix": "fixer", "proceed": "next"}
)

# Loop back
workflow.add_edge("fixer", "validator")
```

---

## 📖 Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://python.langchain.com/
- **Examples**: This repo! Start with `simple-demos/`

---

## 🤝 Contributing

Feel free to:
- Add more demo examples
- Improve the CI/CD agent
- Add tests
- Update documentation

---

## 📄 License

MIT License - feel free to use this code for your projects!

---

## 🆘 Troubleshooting

**Q: Graph won't compile**
- Check that all nodes return the state dict
- Verify all edges connect existing nodes

**Q: Infinite loops**
- Add termination conditions to conditional edges
- Track iteration count in state

**Q: State not persisting**
- Ensure nodes return the state: `return state`
- Don't modify state in-place, create new dict

---

**Happy Graph Building! 🚀**
