import os
from pathlib import Path
from typing import List, Dict
from ..state import CICDState


def is_terraform_file(file_path: str) -> bool:
    return file_path.endswith(('.tf', '.tfvars'))


def is_docker_file(file_path: str) -> bool:
    basename = os.path.basename(file_path).lower()
    return basename.startswith('dockerfile') or 'docker-compose' in basename


def is_helm_file(file_path: str) -> bool:
    basename = os.path.basename(file_path)
    helm_files = ['chart.yaml', 'values.yaml', 'requirements.yaml']
    return basename.lower() in helm_files or '/templates/' in file_path.lower()


def discover_files(state: CICDState) -> CICDState:
    user_paths = state["user_paths"]
    discovered = {"terraform": [], "docker": [], "helm": []}
    
    for path in user_paths:
        if not os.path.exists(path):
            print(f"Warning: Path does not exist: {path}")
            continue
            
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                full_path = os.path.join(root, file)
                
                if is_terraform_file(full_path):
                    discovered["terraform"].append(full_path)
                elif is_docker_file(full_path):
                    discovered["docker"].append(full_path)
                elif is_helm_file(full_path):
                    discovered["helm"].append(full_path)
    
    state["files"] = discovered
    
    print(f"Discovered files:")
    print(f"  Terraform: {len(discovered['terraform'])} files")
    print(f"  Docker: {len(discovered['docker'])} files")
    print(f"  Helm: {len(discovered['helm'])} files")
    
    return state
