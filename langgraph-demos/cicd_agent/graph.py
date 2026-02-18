from langgraph.graph import StateGraph, START, END
from ..state import CICDState, create_initial_state
from .discovery import discover_files
from .validators import validate_terraform, validate_docker, validate_helm
from .fixers import fix_terraform, fix_docker, fix_helm
from .decision import collect_errors, decide_next_action, prepare_release, fail_workflow
from .release import release_docker, release_helm, release_terraform


def build_cicd_graph():
    workflow = StateGraph(CICDState)
    
    # Add nodes
    workflow.add_node("discover", discover_files)
    workflow.add_node("validate_terraform", validate_terraform)
    workflow.add_node("validate_docker", validate_docker)
    workflow.add_node("validate_helm", validate_helm)
    workflow.add_node("collect_errors", collect_errors)
    workflow.add_node("decide", decide_next_action)
    workflow.add_node("fix_terraform", fix_terraform)
    workflow.add_node("fix_docker", fix_docker)
    workflow.add_node("fix_helm", fix_helm)
    workflow.add_node("prepare_release", prepare_release)
    workflow.add_node("release_docker", release_docker)
    workflow.add_node("release_helm", release_helm)
    workflow.add_node("release_terraform", release_terraform)
    workflow.add_node("fail", fail_workflow)
    
    # Add edges
    workflow.add_edge(START, "discover")
    
    # Parallel validation
    workflow.add_edge("discover", "validate_terraform")
    workflow.add_edge("discover", "validate_docker")
    workflow.add_edge("discover", "validate_helm")
    
    # After all validations
    workflow.add_edge("validate_terraform", "collect_errors")
    workflow.add_edge("validate_docker", "collect_errors")
    workflow.add_edge("validate_helm", "collect_errors")
    
    # Decision point
    workflow.add_edge("collect_errors", "decide")
    
    # Conditional edges from decision
    workflow.add_conditional_edges(
        "decide",
        decide_next_action,
        {
            "release": "prepare_release",
            "fix": "fix_terraform",
            "fail": "fail"
        }
    )
    
    # Fix nodes chain
    workflow.add_edge("fix_terraform", "fix_docker")
    workflow.add_edge("fix_docker", "fix_helm")
    
    # After fixes, loop back to validation
    workflow.add_edge("fix_helm", "validate_terraform")
    
    # Release chain
    workflow.add_edge("prepare_release", "release_docker")
    workflow.add_edge("release_docker", "release_helm")
    workflow.add_edge("release_helm", "release_terraform")
    workflow.add_edge("release_terraform", END)
    
    # Fail end
    workflow.add_edge("fail", END)
    
    return workflow.compile()


def run_cicd_agent(user_paths: list, max_fix_attempts: int = 3):
    graph = build_cicd_graph()
    initial_state = create_initial_state(user_paths)
    
    # Set max attempts
    for ft in ["terraform", "docker", "helm"]:
        initial_state["fix_attempts"][ft] = {
            "file_type": ft,
            "attempts": 0,
            "max_attempts": max_fix_attempts,
            "last_fix_time": None
        }
    
    result = graph.invoke(initial_state)
    return result
