from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    messages: list
    step: str


def node_a(state: AgentState) -> AgentState:
    state["messages"] = state.get("messages", []) + ["Executed node A"]
    state["step"] = "a"
    return state


def node_b(state: AgentState) -> AgentState:
    state["messages"] = state.get("messages", []) + ["Executed node B"]
    state["step"] = "b"
    return state


def node_c(state: AgentState) -> AgentState:
    state["messages"] = state.get("messages", []) + ["Executed node C"]
    state["step"] = "c"
    return state


def should_continue(state: AgentState) -> str:
    if len(state.get("messages", [])) < 3:
        return "continue"
    return "end"


graph = StateGraph(AgentState)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_node("c", node_c)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_conditional_edges(
    "b",
    should_continue,
    {
        "continue": "c",
        "end": END
    }
)
graph.add_edge("c", "a")

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [], "step": ""})
    print("Result:", result)
    print("\nExecution path:", result["messages"])
