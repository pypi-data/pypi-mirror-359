"""toml command implementation - UV project creation helper."""

from pathlib import Path
from datetime import datetime
import click

from ..contents import (
    get_pyproject_template,
    get_uv_toml_template,
    get_project_readme_template,
    get_checked_template
)
from ..tools.system_diagnostics import collect_system_info
from ..tools.file_operations import (
    check_directory_status,
    show_project_confirmation,
    create_directory_and_files
)


def execute_toml(project_name: str, base_dir: str, python_version: str = '3.11.13') -> bool:
    """Execute toml command to create uv-friendly project structure.
    
    Args:
        project_name: Name of the project directory to create
        base_dir: Base directory path (default: /tmp)
        python_version: Python version to use (default: 3.11.13)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare target directory path
    target_dir = Path(base_dir) / project_name
    
    # Collect system information for diagnostic file
    sys_info = collect_system_info()
    
    # Check directory status
    dir_status = check_directory_status(target_dir)
    
    # Prepare file list
    files_to_create = _get_files_to_create(project_name, sys_info, python_version)
    
    # Show interactive confirmation with absolute paths
    if not show_project_confirmation(target_dir, dir_status, files_to_create):
        return False
    
    try:
        # Create directory and files
        create_directory_and_files(target_dir, files_to_create)
        
        click.echo(f"\n✓ 成功建立專案目錄: {target_dir}")
        click.echo(f"✓ 已產生 {len(files_to_create)} 個檔案")
        click.echo(f"\n使用方式 Usage:")
        click.echo(f"  cd {target_dir}")
        click.echo(f"  uv sync")
        click.echo(f"  uv run python your_script.py")
        click.echo(f"\n或從外部執行 Or run from outside:")
        click.echo(f"  uv run --project {target_dir} python your_script.py")
        
        return True
        
    except Exception as e:
        click.echo(f"\n❌ 建立失敗: {e}", err=True)
        return False


def _get_files_to_create(project_name: str, sys_info: dict, python_version: str) -> list[tuple[str, str]]:
    """Get all files to create for the uv project.
    
    Args:
        project_name: Name of the project
        sys_info: System information dictionary
        python_version: Python version to use
        
    Returns:
        list[tuple[str, str]]: List of (relative_path, content) tuples
    """
    # Generate templates
    pyproject_content = get_pyproject_template(project_name, python_version=python_version)
    uv_toml_content = get_uv_toml_template(project_name)
    readme_content = get_project_readme_template(project_name, sys_info['timestamp'])
    
    # Generate diagnostic content using existing template
    diagnostic_content = get_checked_template(
        timestamp=sys_info['timestamp'],
        user=sys_info['user'],
        hostname=sys_info['hostname'],
        pwd=sys_info['pwd'],
        python_version=sys_info['python_version'],
        environment=sys_info['environment'],
        os_system=sys_info['os_system'],
        os_release=sys_info['os_release'],
        os_version=sys_info['os_version'],
        machine=sys_info['machine'],
        processor=sys_info['processor'],
        cpu_cores=sys_info['cpu_cores'],
        memory=sys_info['memory'],
        gpu=sys_info['gpu']
    )
    
    # Python version file with specified version
    python_version_content = f"{python_version}\n"
    
    return [
        ('pyproject.toml', pyproject_content),
        ('uv.toml', uv_toml_content),
        ('README.md', readme_content),
        ('.python-version', python_version_content),
        ('notes/diagnostic.md', diagnostic_content)
    ]