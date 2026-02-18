from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ValidationResult(TypedDict):
    file_path: str
    tool: str
    passed: bool
    errors: List[str]
    warnings: List[str]


class FixAttempt(TypedDict):
    file_type: str
    attempts: int
    max_attempts: int
    last_fix_time: Optional[str]


class CICDState(TypedDict):
    user_paths: List[str]
    files: Dict[str, List[str]]
    validation_results: Dict[str, List[ValidationResult]]
    all_validations_complete: bool
    collected_errors: Dict[str, List[str]]
    errors_by_file: Dict[str, List[str]]
    fix_attempts: Dict[str, FixAttempt]
    files_fixed: List[str]
    fix_applied: bool
    release_ready: bool
    release_results: Dict[str, Any]
    docker_images_built: List[str]
    helm_charts_released: List[str]
    terraform_applied: bool
    status: str
    error_message: Optional[str]


def create_initial_state(user_paths: List[str]) -> CICDState:
    return {
        "user_paths": user_paths,
        "files": {"terraform": [], "docker": [], "helm": []},
        "validation_results": {},
        "all_validations_complete": False,
        "collected_errors": {},
        "errors_by_file": {},
        "fix_attempts": {},
        "files_fixed": [],
        "fix_applied": False,
        "release_ready": False,
        "release_results": {},
        "docker_images_built": [],
        "helm_charts_released": [],
        "terraform_applied": False,
        "status": "running",
        "error_message": None
    }
