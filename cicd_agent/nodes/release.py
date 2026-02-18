import os
import subprocess
from datetime import datetime
from ..state import CICDState


def run_command(cmd: list, cwd: str = None) -> tuple:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def release_docker(state: CICDState) -> CICDState:
    files = state["files"]["docker"]
    built_images = []
    
    if not files:
        print("No Docker files to release")
        state["release_results"]["docker"] = {"status": "skipped"}
        return state
    
    print(f"\nReleasing Docker images...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for dockerfile in files:
        docker_dir = os.path.dirname(dockerfile) or "."
        image_name = os.path.basename(os.path.abspath(docker_dir)).lower()
        tag = f"{image_name}:{timestamp}"
        
        print(f"  Building {tag}...")
        
        # Build image
        passed, stdout, stderr = run_command(
            ["docker", "build", "-t", tag, "."],
            cwd=docker_dir
        )
        
        if passed:
            built_images.append(tag)
            print(f"    ✓ Built {tag}")
            
            # Optional: Push to registry (configure as needed)
            # run_command(["docker", "push", tag])
        else:
            print(f"    ✗ Failed to build {tag}: {stderr}")
    
    state["docker_images_built"] = built_images
    state["release_results"]["docker"] = {
        "status": "success" if built_images else "failed",
        "images": built_images
    }
    
    print(f"Built {len(built_images)} Docker images")
    return state


def release_helm(state: CICDState) -> CICDState:
    files = state["files"]["helm"]
    released_charts = []
    
    if not files:
        print("No Helm charts to release")
        state["release_results"]["helm"] = {"status": "skipped"}
        return state
    
    print(f"\nReleasing Helm charts...")
    
    chart_dirs = set()
    for f in files:
        chart_dir = os.path.dirname(f)
        while chart_dir and not os.path.exists(os.path.join(chart_dir, "Chart.yaml")):
            chart_dir = os.path.dirname(chart_dir)
        if chart_dir:
            chart_dirs.add(chart_dir)
    
    for chart_dir in chart_dirs:
        chart_name = os.path.basename(chart_dir)
        print(f"  Packaging {chart_name}...")
        
        # Package chart
        passed, stdout, stderr = run_command(
            ["helm", "package", chart_dir, "--destination", "./dist"]
        )
        
        if passed:
            released_charts.append(chart_name)
            print(f"    ✓ Packaged {chart_name}")
            
            # Optional: Push to chart repo
            # run_command(["helm", "push", f"./dist/{chart_name}-*.tgz", "chart-repo"])
        else:
            print(f"    ✗ Failed to package {chart_name}: {stderr}")
    
    state["helm_charts_released"] = released_charts
    state["release_results"]["helm"] = {
        "status": "success" if released_charts else "failed",
        "charts": released_charts
    }
    
    print(f"Released {len(released_charts)} Helm charts")
    return state


def release_terraform(state: CICDState) -> CICDState:
    files = state["files"]["terraform"]
    
    if not files:
        print("No Terraform files to release")
        state["release_results"]["terraform"] = {"status": "skipped"}
        return state
    
    print(f"\nApplying Terraform...")
    
    tf_dirs = set(os.path.dirname(f) for f in files)
    
    for tf_dir in tf_dirs:
        print(f"  Planning in {tf_dir}...")
        
        # terraform plan
        passed, stdout, stderr = run_command(["terraform", "plan", "-out=tfplan"], cwd=tf_dir)
        
        if passed:
            print(f"    ✓ Plan created")
            
            # terraform apply
            print(f"  Applying in {tf_dir}...")
            passed, stdout, stderr = run_command(
                ["terraform", "apply", "-auto-approve", "tfplan"],
                cwd=tf_dir
            )
            
            if passed:
                state["terraform_applied"] = True
                print(f"    ✓ Terraform applied successfully")
            else:
                print(f"    ✗ Terraform apply failed: {stderr}")
                state["release_results"]["terraform"] = {"status": "failed", "error": stderr}
                return state
        else:
            print(f"    ✗ Terraform plan failed: {stderr}")
            state["release_results"]["terraform"] = {"status": "failed", "error": stderr}
            return state
    
    state["release_results"]["terraform"] = {"status": "success"}
    print(f"✓ Terraform infrastructure deployed")
    return state
