"""Static content templates for soldcli."""

# Import all template functions
from .hint import get_hint_template
from .diagnostic import (
    get_checked_template,
    get_diagnostic_readme_template,
    get_docker_platform
)
from .uv_templates import (
    get_pyproject_template,
    get_uv_toml_template,
    get_project_readme_template
)

# Export public interface
__all__ = [
    "get_hint_template",
    "get_checked_template", 
    "get_diagnostic_readme_template",
    "get_docker_platform",
    "get_pyproject_template",
    "get_uv_toml_template",
    "get_project_readme_template"
]