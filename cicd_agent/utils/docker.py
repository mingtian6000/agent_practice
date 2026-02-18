import re


def parse_dockerfile(dockerfile_path: str) -> dict:
    """Parse Dockerfile and extract key information"""
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    info = {
        'base_image': None,
        'exposed_ports': [],
        'commands': [],
        'has_workdir': False,
        'has_user': False,
        'has_healthcheck': False
    }
    
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('FROM'):
            info['base_image'] = line.split()[1] if len(line.split()) > 1 else None
        elif line.startswith('EXPOSE'):
            info['exposed_ports'].extend(line.split()[1:])
        elif line.startswith('WORKDIR'):
            info['has_workdir'] = True
        elif line.startswith('USER'):
            info['has_user'] = True
        elif line.startswith('HEALTHCHECK'):
            info['has_healthcheck'] = True
        elif line.startswith(('RUN', 'CMD', 'ENTRYPOINT')):
            info['commands'].append(line)
    
    return info


def suggest_base_image_update(current_image: str) -> str:
    """Suggest a newer, stable base image"""
    updates = {
        'python:3.8': 'python:3.11-slim',
        'python:3.9': 'python:3.11-slim',
        'python:3.10': 'python:3.11-slim',
        'node:14': 'node:20-alpine',
        'node:16': 'node:20-alpine',
        'node:18': 'node:20-alpine',
        'ubuntu:18.04': 'ubuntu:22.04',
        'ubuntu:20.04': 'ubuntu:22.04',
        'alpine:3.12': 'alpine:3.18',
        'alpine:3.14': 'alpine:3.18',
        'alpine:3.16': 'alpine:3.18',
    }
    
    for old, new in updates.items():
        if old in current_image:
            return new
    
    return current_image
