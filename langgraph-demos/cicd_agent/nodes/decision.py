from ..state import CICDState


def collect_errors(state: CICDState) -> CICDState:
    collected = {"terraform": [], "docker": [], "helm": []}
    errors_by_file = {}
    
    for file_type, results in state["validation_results"].items():
        for result in results:
            if not result["passed"]:
                error_msg = f"[{result['tool']}] {result['file_path']}: {', '.join(result['errors'])}"
                collected[file_type].append(error_msg)
                
                if result['file_path'] not in errors_by_file:
                    errors_by_file[result['file_path']] = []
                errors_by_file[result['file_path']].extend(result['errors'])
    
    state["collected_errors"] = collected
    state["errors_by_file"] = errors_by_file
    state["all_validations_complete"] = True
    
    total_errors = sum(len(errs) for errs in collected.values())
    print(f"\nValidation complete. Total errors found: {total_errors}")
    for ft, errs in collected.items():
        if errs:
            print(f"  {ft}: {len(errs)} errors")
    
    return state


def decide_next_action(state: CICDState) -> str:
    total_errors = sum(len(errs) for errs in state["collected_errors"].values())
    
    if total_errors == 0:
        print("All validations passed! Proceeding to release...")
        state["release_ready"] = True
        return "release"
    
    print(f"\nErrors found: {total_errors}")
    
    # Check if we can attempt fixes
    needs_fix = False
    for file_type in ["terraform", "docker", "helm"]:
        errors = state["collected_errors"].get(file_type, [])
        if errors:
            attempts = state["fix_attempts"].get(file_type, {}).get("attempts", 0)
            max_attempts = state["fix_attempts"].get(file_type, {}).get("max_attempts", 3)
            
            if attempts < max_attempts:
                print(f"  {file_type}: {len(errors)} errors, will attempt fix ({attempts + 1}/{max_attempts})")
                needs_fix = True
            else:
                print(f"  {file_type}: {len(errors)} errors, max attempts reached")
    
    if needs_fix:
        state["status"] = "fixing"
        return "fix"
    else:
        state["status"] = "failed"
        state["error_message"] = f"Max fix attempts reached. Errors remain: {total_errors}"
        print(f"\nFAILED: {state['error_message']}")
        return "fail"


def prepare_release(state: CICDState) -> CICDState:
    print("\nPreparing for release...")
    state["release_ready"] = True
    state["status"] = "releasing"
    return state


def fail_workflow(state: CICDState) -> CICDState:
    state["status"] = "failed"
    print(f"\nWorkflow failed with errors:")
    for ft, errs in state["collected_errors"].items():
        if errs:
            print(f"\n{ft.upper()}:")
            for err in errs[:5]:
                print(f"  - {err}")
            if len(errs) > 5:
                print(f"  ... and {len(errs) - 5} more errors")
    return state
