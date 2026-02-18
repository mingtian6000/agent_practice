from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


class ChatState(TypedDict):
    messages: list


def chat_node(state: ChatState) -> ChatState:
    last_message = state["messages"][-1] if state["messages"] else None
    
    if last_message and isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        if "add" in user_input or "sum" in user_input:
            response = "I can help Please provide two you add numbers. numbers."
        elif "multiply" in user_input or "product" in user_input:
            response = "I can help you multiply numbers. Please provide two numbers."
        elif "hello" in user_input or "hi" in user_input:
            response = "Hello! How can I help you today?"
        else:
            response = f"You said: {last_message.content}. I'm a simple demo bot!"
        
        state["messages"] = state["messages"] + [AIMessage(content=response)]
    
    return state


tools = [add, multiply]
tool_node = ToolNode(tools)

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

app = graph.compile()

if __name__ == "__main__":
    test_inputs = [
        "Hello!",
        "What is 5 + 3?",
        "Multiply 4 and 7",
    ]
    
    for user_input in test_inputs:
        result = app.invoke({
            "messages": [HumanMessage(content=user_input)]
        })
        print(f"User: {user_input}")
        print(f"Bot: {result['messages'][-1].content}")
        print()
