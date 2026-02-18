from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    message: str
    count: int


def greeting_node(state: GraphState) -> GraphState:
    state["message"] = "Hello! Processing item 0"
    state["count"] = state.get("count", 0) + 1
    return state


def processing_node(state: GraphState) -> GraphState:
    state["message"] = state["message"] + " - processed!"
    state["count"] = state.get("count", 0) + 1
    return state


workflow = StateGraph(GraphState)
workflow.add_node("greeting", greeting_node)
workflow.add_node("processing", processing_node)
workflow.add_edge(START, "greeting")
workflow.add_edge("greeting", "processing")
workflow.add_edge("processing", END)

app = workflow.compile()

if __name__ == "__main__":
    initial_state = {"message": "", "count": 0}
    result = app.invoke(initial_state)
    print(result)
