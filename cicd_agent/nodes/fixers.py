import os
import re
from datetime import datetime
from typing import Dict
from ..state import CICDState, FixAttempt


def get_or_create_fix_attempt(state: CICDState, file_type: str) -> FixAttempt:
    if file_type not in state["fix_attempts"]:
        state["fix_attempts"][file_type] = {
            "file_type": file_type,
            "attempts": 0,
            "max_attempts": 3,
            "last_fix_time": None
        }
    return state["fix_attempts"][file_type]


def can_attempt_fix(state: CICDState, file_type: str) -> bool:
    attempt = get_or_create_fix_attempt(state, file_type)
    return attempt["attempts"] < attempt["max_attempts"]


def increment_fix_attempt(state: CICDState, file_type: str):
    attempt = get_or_create_fix_attempt(state, file_type)
    attempt["attempts"] += 1
    attempt["last_fix_time"] = datetime.now().isoformat()


def fix_terraform(state: CICDState) -> CICDState:
    if not can_attempt_fix(state, "terraform"):
        print("Max fix attempts reached for Terraform")
        return state
    
    files = state["files"]["terraform"]
    if not files:
        return state
    
    print(f"Attempting to fix Terraform files (attempt {state['fix_attempts']['terraform']['attempts'] + 1}/3)")
    
    tf_dirs = set(os.path.dirname(f) for f in files)
    
    for tf_dir in tf_dirs:
        # terraform fmt
        import subprocess
        subprocess.run(["terraform", "fmt", "-recursive"], cwd=tf_dir, capture_output=True)
        
        # Fix provider version constraints
        for root, dirs, files in os.walk(tf_dir):
            for file in files:
                if file.endswith('.tf'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Add required_providers block if missing
                    if 'required_providers' not in content and 'provider ' in content:
                        content = content.replace(
                            'provider "',
                            'terraform {\n  required_providers {\n    # Providers will be auto-detected\n  }\n}\n\nprovider "'
                        )
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
    
    increment_fix_attempt(state, "terraform")
    state["files_fixed"].extend(files)
    state["fix_applied"] = True
    print(f"Fixed {len(files)} Terraform files")
    
    return state


def fix_docker(state: CICDState) -> CICDState:
    if not can_attempt_fix(state, "docker"):
        print("Max fix attempts reached for Docker")
        return state
    
    files = state["files"]["docker"]
    if not files:
        return state
    
    print(f"Attempting to fix Docker files (attempt {state['fix_attempts']['docker']['attempts'] + 1}/3)")
    
    base_image_updates = {
        'FROM python:': 'FROM python:3.11-slim',
        'FROM node:': 'FROM node:20-alpine',
        'FROM ubuntu:': 'FROM ubuntu:22.04',
        'FROM alpine:': 'FROM alpine:3.18',
    }
    
    for dockerfile in files:
        with open(dockerfile, 'r') as f:
            lines = f.readlines()
        
        fixed_lines = []
        for line in lines:
            original_line = line
            
            # Fix base images to latest stable
            for old, new in base_image_updates.items():
                if line.strip().startswith('FROM') and old in line:
                    if 'latest' not in line and ':' not in line.split(old)[1].split()[0]:
                        line = line.replace(old.split(':')[0] + ':', new)
                        print(f"  Updated base image in {dockerfile}")
            
            # Add WORKDIR if missing
            if line.strip().startswith('FROM') and not any('WORKDIR' in l for l in lines):
                fixed_lines.append(line)
                fixed_lines.append('WORKDIR /app\n')
                continue
            
            # Add USER if missing (security fix)
            if line.strip().startswith('CMD') or line.strip().startswith('ENTRYPOINT'):
                if not any('USER' in l for l in lines):
                    fixed_lines.append('USER 1000\n')
            
            fixed_lines.append(line)
        
        with open(dockerfile, 'w') as f:
            f.writelines(fixed_lines)
    
    increment_fix_attempt(state, "docker")
    state["files_fixed"].extend(files)
    state["fix_applied"] = True
    print(f"Fixed {len(files)} Docker files")
    
    return state


def fix_helm(state: CICDState) -> CICDState:
    if not can_attempt_fix(state, "helm"):
        print("Max fix attempts reached for Helm")
        return state
    
    files = state["files"]["helm"]
    if not files:
        return state
    
    print(f"Attempting to fix Helm files (attempt {state['fix_attempts']['helm']['attempts'] + 1}/3)")
    
    chart_dirs = set()
    for f in files:
        chart_dir = os.path.dirname(f)
        while chart_dir and not os.path.exists(os.path.join(chart_dir, "Chart.yaml")):
            chart_dir = os.path.dirname(chart_dir)
        if chart_dir:
            chart_dirs.add(chart_dir)
    
    for chart_dir in chart_dirs:
        chart_yaml = os.path.join(chart_dir, "Chart.yaml")
        
        if os.path.exists(chart_yaml):
            with open(chart_yaml, 'r') as f:
                content = f.read()
            
            # Ensure required fields exist
            required_fields = ['apiVersion:', 'name:', 'version:']
            for field in required_fields:
                if field not in content:
                    if field == 'apiVersion:':
                        content = f"apiVersion: v2\n{content}"
                    elif field == 'name:':
                        chart_name = os.path.basename(chart_dir)
                        content = f"{content}\nname: {chart_name}\n"
                    elif field == 'version:':
                        content = f"{content}\nversion: 0.1.0\n"
            
            with open(chart_yaml, 'w') as f:
                f.write(content)
            
            print(f"  Fixed Chart.yaml in {chart_dir}")
    
    increment_fix_attempt(state, "helm")
    state["files_fixed"].extend(files)
    state["fix_applied"] = True
    print(f"Fixed {len(files)} Helm files")
    
    return state
