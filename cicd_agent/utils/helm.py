import os
import yaml


def find_chart_dirs(files: list) -> set:
    """Find all Helm chart directories"""
    chart_dirs = set()
    for f in files:
        chart_dir = os.path.dirname(f)
        while chart_dir and not os.path.exists(os.path.join(chart_dir, "Chart.yaml")):
            parent = os.path.dirname(chart_dir)
            if parent == chart_dir:
                break
            chart_dir = parent
        if chart_dir and os.path.exists(os.path.join(chart_dir, "Chart.yaml")):
            chart_dirs.add(chart_dir)
    return chart_dirs


def read_chart_yaml(chart_dir: str) -> dict:
    """Read and parse Chart.yaml"""
    chart_yaml_path = os.path.join(chart_dir, "Chart.yaml")
    if os.path.exists(chart_yaml_path):
        with open(chart_yaml_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def validate_chart_yaml(chart_data: dict) -> list:
    """Validate Chart.yaml has required fields"""
    errors = []
    required = ['apiVersion', 'name', 'version']
    
    for field in required:
        if field not in chart_data:
            errors.append(f"Missing required field: {field}")
    
    return errors
