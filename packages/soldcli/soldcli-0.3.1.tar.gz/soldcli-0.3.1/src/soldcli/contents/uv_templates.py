"""UV project template generators."""

from datetime import datetime


def get_pyproject_template(project_name: str, python_version: str, description: str = None) -> str:
    """Generate pyproject.toml template content for uv projects.
    
    Args:
        project_name: Name of the project
        python_version: python_version
        description: Optional project description
        
    Returns:
        str: pyproject.toml template content
    """
    if description is None:
        description = f"A uv-managed Python project created by soldcli"
    
    return f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = "=={python_version}"
dependencies = []

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

# [tool.uv]
# Project-specific uv configuration
# Reference: https://docs.astral.sh/uv/configuration/

'''


def get_uv_toml_template(project_name: str) -> str:
    """Generate uv.toml template content.
    
    Args:
        project_name: Name of the project
        
    Returns:
        str: uv.toml template content
    """
    return f'''# uv configuration for {project_name}
# This file takes precedence over pyproject.toml [tool.uv] section
# Reference: https://docs.astral.sh/uv/configuration/

# Example configurations:
# 
# [sources]
# torch = {{ index = "pytorch" }}
#
# [[index]]
# name = "pytorch"
# url = "https://download.pytorch.org/whl/cpu"
#
# [pip]
# index-url = "https://pypi.org/simple"
'''


def get_project_readme_template(project_name: str, created_at: str) -> str:
    """Generate README.md template for uv project.
    
    Args:
        project_name: Name of the project
        created_at: Creation timestamp
        
    Returns:
        str: README.md template content
    """
    return f'''# {project_name}

A uv-managed Python project created by soldcli on {created_at}.

## Quick Start (by qtwu)

```bash
uv venv
uv add nodeenv
uv run nodeenv -n 22.16.0 .node22 --prompt NODE22 --verbose
. ./.node22/bin/activate

```

## Quick Start (by Claude Code)

```bash
# Run scripts within this project environment
uv run python your_script.py

# Run from outside the project directory
uv run --project {project_name} python your_script.py

# Add dependencies
uv add requests pandas

# Install development dependencies
uv add --dev pytest ruff

# Sync environment with lockfile
uv sync
```

## Project Structure

```
{project_name}/
├── pyproject.toml    # Project metadata and dependencies
├── uv.toml          # uv-specific configuration
├── uv.lock          # Locked dependency versions
├── .python-version  # Python version for this project
├── README.md        # This file
└── notes/
    └── diagnostic.md # System diagnostic information
```

## Notes

- The virtual environment is automatically managed in `.venv/`
- Dependencies are locked in `uv.lock` for reproducibility
- Use `uv run` to execute commands in the project environment

## References

- [uv Documentation](https://docs.astral.sh/uv/)
- [Working with uv Projects](https://docs.astral.sh/uv/guides/projects/)
'''