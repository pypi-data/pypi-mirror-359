"""pack2 command implementation - Unix-like environment diagnostic tool."""

from pathlib import Path
import click

from ..contents import get_checked_template, get_diagnostic_readme_template
from ..tools.system_diagnostics import collect_system_info
from ..tools.file_operations import (
    check_directory_status,
    show_diagnostic_confirmation,
    create_directory_and_files
)


def execute_pack2(project_name: str, base_dir: str) -> bool:
    """Execute pack2 command to create diagnostic project directory.
    
    Args:
        project_name: Name of the project directory to create
        base_dir: Base directory path (default: /tmp)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare target directory path
    target_dir = Path(base_dir) / project_name
    
    # Collect system information
    sys_info = collect_system_info()
    
    # Check directory status
    dir_status = check_directory_status(target_dir)
    
    # Prepare file list
    files_to_create = _get_files_to_create(sys_info)
    
    # Show interactive confirmation
    if not show_diagnostic_confirmation(sys_info, target_dir, dir_status, files_to_create):
        return False
    
    try:
        # Create directory and files
        create_directory_and_files(target_dir, files_to_create)
        
        click.echo(f"\n✓ 成功建立專案目錄: {target_dir}")
        click.echo(f"✓ 已產生 {len(files_to_create)} 個輔助檔案")
        return True
        
    except Exception as e:
        click.echo(f"\n❌ 建立失敗: {e}", err=True)
        return False


def _get_files_to_create(sys_info: dict) -> list[tuple[str, str]]:
    """Get all files to create for the diagnostic project.
    
    Args:
        sys_info: System information dictionary
        
    Returns:
        list[tuple[str, str]]: List of (filename, content) tuples
    """
    # Generate checked.md content using template
    checked_content = get_checked_template(
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
    
    # Get README content using template
    readme_content = get_diagnostic_readme_template()
    
    return [
        ('checked.md', checked_content),
        ('README.md', readme_content)
    ]