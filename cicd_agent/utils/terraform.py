import os
import re


def find_terraform_dirs(files: list) -> set:
    return set(os.path.dirname(f) for f in files)


def extract_providers(content: str) -> list:
    """Extract provider names from Terraform content"""
    providers = []
    pattern = r'provider\s+"([^"]+)"'
    matches = re.findall(pattern, content)
    providers.extend(matches)
    return providers
