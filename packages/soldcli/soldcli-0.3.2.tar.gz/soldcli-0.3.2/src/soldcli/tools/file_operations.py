"""File operation tools for soldcli."""

import os
from pathlib import Path
from typing import List, Tuple
import click


def write_file(file_path: Path, content: str) -> bool:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        OSError: When unable to write file
        PermissionError: When lacking write permissions
    """
    try:
        file_path.write_text(content, encoding='utf-8')
        return True
    except (OSError | PermissionError) as e:
        raise OSError(f"無法寫入檔案 {file_path}: {e}") from e


def check_directory_status(target_dir: Path) -> dict:
    """Check target directory status.
    
    Args:
        target_dir: Target directory path
        
    Returns:
        dict: Status information including existence and permissions
    """
    status = {
        'exists': target_dir.exists(),
        'is_dir': target_dir.is_dir() if target_dir.exists() else False,
        'parent_writable': os.access(target_dir.parent, os.W_OK),
        'parent_exists': target_dir.parent.exists()
    }
    
    if status['exists']:
        status['writable'] = os.access(target_dir, os.W_OK)
        status['empty'] = not any(target_dir.iterdir()) if status['is_dir'] else False
    
    return status


def create_directory_and_files(target_dir: Path, files_to_create: List[Tuple[str, str]]) -> bool:
    """Create directory and write files to it.
    
    Args:
        target_dir: Directory to create
        files_to_create: List of (filename, content) tuples
                       filename can include subdirectories (e.g., "notes/diagnostic.md")
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If directory creation or file writing fails
    """
    try:
        # Create directory
        target_dir.mkdir(parents=True, exist_ok=False)
        
        # Create files
        for filename, content in files_to_create:
            file_path = target_dir / filename
            
            # Create parent directories if filename contains subdirectories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_path.write_text(content, encoding='utf-8')
        
        return True
        
    except Exception as e:
        raise Exception(f"建立失敗: {e}") from e


def show_diagnostic_confirmation(sys_info: dict, target_dir: Path, dir_status: dict, 
                               files_to_create: List[Tuple[str, str]]) -> bool:
    """Show interactive confirmation prompt for diagnostic project creation.
    
    Args:
        sys_info: System information
        target_dir: Target directory path
        dir_status: Directory status information
        files_to_create: List of files to create
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    click.echo("\n" + "="*60)
    click.echo("診斷專案建立確認 - Diagnostic Project Creation Confirmation")
    click.echo("="*60)
    
    # Show system info
    click.echo(f"\n執行身份 User: {click.style(sys_info['user'], fg='cyan')}")
    click.echo(f"作業環境 Environment: {click.style(sys_info['environment'], fg='cyan')}")
    
    # Show directory info
    click.echo(f"\n目標目錄 Target Directory: {click.style(str(target_dir), fg='yellow')}")
    
    # Check directory status
    if dir_status['exists']:
        if dir_status['is_dir']:
            if dir_status['empty']:
                click.echo(click.style("⚠ 目錄已存在但是空的 (Directory exists but empty)", fg='yellow'))
            else:
                click.echo(click.style("❌ 目錄已存在且包含檔案 (Directory exists with files)", fg='red'))
                return False
        else:
            click.echo(click.style("❌ 路徑已存在但不是目錄 (Path exists but not a directory)", fg='red'))
            return False
    elif not dir_status['parent_exists']:
        click.echo(click.style("❌ 父目錄不存在 (Parent directory doesn't exist)", fg='red'))
        return False
    elif not dir_status['parent_writable']:
        click.echo(click.style("❌ 無權限在父目錄建立檔案 (No permission in parent directory)", fg='red'))
        return False
    else:
        click.echo(click.style("✓ 目錄可以建立 (Directory can be created)", fg='green'))
    
    # Show files to create
    click.echo(f"\n將建立以下檔案 Files to create:")
    for filename, _ in files_to_create:
        click.echo(f"  - {filename}")
    
    # Ask for confirmation
    click.echo("\n" + "="*60)
    return click.confirm("確定要建立診斷專案嗎？Do you want to create the diagnostic project?", default=False)


def show_project_confirmation(target_dir: Path, dir_status: dict, 
                            files_to_create: List[Tuple[str, str]]) -> bool:
    """Show interactive confirmation prompt for project creation with absolute paths.
    
    Args:
        target_dir: Target directory path
        dir_status: Directory status information
        files_to_create: List of (relative_path, content) tuples
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    click.echo("\n" + "="*60)
    click.echo("專案建立確認 - Project Creation Confirmation")
    click.echo("="*60)
    
    # Show target directory
    click.echo(f"\n目標目錄 Target Directory: {click.style(str(target_dir), fg='yellow', bold=True)}")
    
    # Check directory status
    if dir_status['exists']:
        if dir_status['is_dir']:
            if dir_status['empty']:
                click.echo(click.style("⚠ 目錄已存在但是空的 (Directory exists but empty)", fg='yellow'))
            else:
                click.echo(click.style("❌ 目錄已存在且包含檔案 (Directory exists with files)", fg='red'))
                return False
        else:
            click.echo(click.style("❌ 路徑已存在但不是目錄 (Path exists but not a directory)", fg='red'))
            return False
    elif not dir_status['parent_exists']:
        click.echo(click.style("❌ 父目錄不存在 (Parent directory doesn't exist)", fg='red'))
        return False
    elif not dir_status['parent_writable']:
        click.echo(click.style("❌ 無權限在父目錄建立檔案 (No permission in parent directory)", fg='red'))
        return False
    else:
        click.echo(click.style("✓ 目錄可以建立 (Directory can be created)", fg='green'))
    
    # Show files to create with absolute paths
    click.echo(f"\n將建立以下檔案 Files to create:")
    for relative_path, _ in files_to_create:
        absolute_path = (target_dir / relative_path).resolve()
        click.echo(f"  {click.style(str(absolute_path), fg='cyan')}")
    
    # Ask for confirmation
    click.echo("\n" + "="*60)
    return click.confirm("確定要建立專案嗎？Do you want to create the project?", default=False)