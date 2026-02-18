"""
Demonstration of Annotated types in LangGraph

Annotated allows you to specify how state should be reduced/merged
when multiple nodes update the same field.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage


# Example 1: Basic Annotated with custom reducer
# ================================================

def concat_lists(existing: list, new: list) -> list:
    """Custom reducer: concatenate two lists"""
    return existing + new


def sum_numbers(existing: int, new: int) -> int:
    """Custom reducer: sum two numbers"""
    return existing + new


class AnnotatedState(TypedDict):
    # Messages use built-in add_messages reducer
    messages: Annotated[list, add_messages]
    
    # Custom list reducer - concatenates
    logs: Annotated[list, concat_lists]
    
    # Custom number reducer - sums
    total_count: Annotated[int, sum_numbers]
    
    # No reducer - overwrites (default behavior)
    current_status: str


def node_a(state: AnnotatedState) -> AnnotatedState:
    """Node A adds messages and logs"""
    state["messages"] = [HumanMessage(content="Hello from A")]
    state["logs"] = ["Node A executed"]
    state["total_count"] = 1
    state["current_status"] = "Running A"
    return state


def node_b(state: AnnotatedState) -> AnnotatedState:
    """Node B also adds messages and logs"""
    state["messages"] = [AIMessage(content="Response from B")]
    state["logs"] = ["Node B executed"]
    state["total_count"] = 1
    state["current_status"] = "Running B"
    return state


def node_c(state: AnnotatedState) -> AnnotatedState:
    """Node C finalizes"""
    state["messages"] = [AIMessage(content="Final from C")]
    state["logs"] = ["Node C executed"]
    state["total_count"] = 1
    state["current_status"] = "Completed"
    return state


# Build graph
workflow = StateGraph(AnnotatedState)
workflow.add_node("A", node_a)
workflow.add_node("B", node_b)
workflow.add_node("C", node_c)

workflow.add_edge(START, "A")
workflow.add_edge("A", "B")
workflow.add_edge("B", "C")
workflow.add_edge("C", END)

app = workflow.compile()


if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph Annotated Types Demo")
    print("=" * 60)
    
    # Run the graph
    result = app.invoke({
        "messages": [],
        "logs": [],
        "total_count": 0,
        "current_status": "Starting"
    })
    
    print("\nResults:")
    print("-" * 60)
    
    # Messages (add_messages reducer) - accumulates
    print(f"\n1. Messages (using add_messages):")
    print(f"   Count: {len(result['messages'])}")
    for msg in result['messages']:
        print(f"   - {msg.type}: {msg.content}")
    
    # Logs (custom concat reducer) - accumulates
    print(f"\n2. Logs (using custom concat_lists):")
    print(f"   Count: {len(result['logs'])}")
    for log in result['logs']:
        print(f"   - {log}")
    
    # Total count (custom sum reducer) - accumulates
    print(f"\n3. Total Count (using custom sum_numbers):")
    print(f"   Value: {result['total_count']}")
    print(f"   (Each node added 1, so 1+1+1=3)")
    
    # Current status (no reducer) - overwrites
    print(f"\n4. Current Status (no reducer - overwrites):")
    print(f"   Value: {result['current_status']}")
    print(f"   (Only shows last value from Node C)")
    
    print("\n" + "=" * 60)
    print("Key Takeaway:")
    print("Annotated lets you control how state updates are merged!")
    print("=" * 60)
