import subprocess
import os
from typing import List
from ..state import CICDState, ValidationResult


def run_command(cmd: List[str], cwd: str = None) -> tuple:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def validate_terraform(state: CICDState) -> CICDState:
    files = state["files"]["terraform"]
    results = []
    
    if not files:
        print("No Terraform files to validate")
        state["validation_results"]["terraform"] = results
        return state
    
    tf_dirs = set()
    for f in files:
        tf_dirs.add(os.path.dirname(f))
    
    for tf_dir in tf_dirs:
        print(f"Validating Terraform in: {tf_dir}")
        
        # terraform validate
        passed, stdout, stderr = run_command(["terraform", "validate"], cwd=tf_dir)
        results.append({
            "file_path": tf_dir,
            "tool": "terraform_validate",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": []
        })
        
        # tflint
        passed, stdout, stderr = run_command(["tflint"], cwd=tf_dir)
        results.append({
            "file_path": tf_dir,
            "tool": "tflint",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": [] if passed else [stdout]
        })
        
        # checkov
        passed, stdout, stderr = run_command(
            ["checkov", "-d", ".", "--framework", "terraform", "--quiet"],
            cwd=tf_dir
        )
        results.append({
            "file_path": tf_dir,
            "tool": "checkov",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": []
        })
    
    state["validation_results"]["terraform"] = results
    return state


def validate_docker(state: CICDState) -> CICDState:
    files = state["files"]["docker"]
    results = []
    
    if not files:
        print("No Docker files to validate")
        state["validation_results"]["docker"] = results
        return state
    
    for dockerfile in files:
        print(f"Validating Docker file: {dockerfile}")
        docker_dir = os.path.dirname(dockerfile) or "."
        
        # hadolint
        passed, stdout, stderr = run_command(["hadolint", dockerfile])
        results.append({
            "file_path": dockerfile,
            "tool": "hadolint",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": [] if passed else [stdout]
        })
        
        # docker build test
        passed, stdout, stderr = run_command(
            ["docker", "build", "--no-cache", "-t", "test-build", "."],
            cwd=docker_dir
        )
        results.append({
            "file_path": dockerfile,
            "tool": "docker_build",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": []
        })
        
        # Clean up test image
        if passed:
            run_command(["docker", "rmi", "test-build"], cwd=docker_dir)
    
    state["validation_results"]["docker"] = results
    return state


def validate_helm(state: CICDState) -> CICDState:
    files = state["files"]["helm"]
    results = []
    
    if not files:
        print("No Helm files to validate")
        state["validation_results"]["helm"] = results
        return state
    
    chart_dirs = set()
    for f in files:
        chart_dir = os.path.dirname(f)
        while chart_dir and not os.path.exists(os.path.join(chart_dir, "Chart.yaml")):
            chart_dir = os.path.dirname(chart_dir)
        if chart_dir:
            chart_dirs.add(chart_dir)
    
    for chart_dir in chart_dirs:
        print(f"Validating Helm chart: {chart_dir}")
        
        # helm lint
        passed, stdout, stderr = run_command(["helm", "lint", chart_dir])
        results.append({
            "file_path": chart_dir,
            "tool": "helm_lint",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": [] if passed else [stdout]
        })
        
        # helm template
        passed, stdout, stderr = run_command(["helm", "template", chart_dir])
        results.append({
            "file_path": chart_dir,
            "tool": "helm_template",
            "passed": passed,
            "errors": [] if passed else [stderr or stdout],
            "warnings": []
        })
    
    state["validation_results"]["helm"] = results
    return state
