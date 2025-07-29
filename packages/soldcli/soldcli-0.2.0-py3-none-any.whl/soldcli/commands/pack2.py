"""pack2 command implementation - Unix-like environment diagnostic tool."""

import os
import platform
import subprocess
import getpass
from datetime import datetime
from pathlib import Path
import click


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
    
    # Collect system information first
    sys_info = check_system_info()
    
    # Check directory status
    dir_status = check_directory_status(target_dir)
    
    # Prepare file list
    files_to_create = get_auxiliary_files(sys_info)
    
    # Show interactive confirmation
    if not show_confirmation(sys_info, target_dir, dir_status, files_to_create):
        return False
    
    try:
        # Create directory
        target_dir.mkdir(parents=True, exist_ok=False)
        
        # Create auxiliary files
        for filename, content in files_to_create:
            file_path = target_dir / filename
            file_path.write_text(content, encoding='utf-8')
        
        click.echo(f"\n✓ 成功建立專案目錄: {target_dir}")
        click.echo(f"✓ 已產生 {len(files_to_create)} 個輔助檔案")
        return True
        
    except Exception as e:
        click.echo(f"\n❌ 建立失敗: {e}", err=True)
        return False


def check_system_info() -> dict:
    """Collect system diagnostic information.
    
    Returns:
        dict: System information including OS, CPU, memory, etc.
    """
    info = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user': getpass.getuser(),
        'pwd': os.getcwd(),
        'hostname': platform.node(),
        'os_system': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }
    
    # Detect specific Unix-like environments
    info['environment'] = detect_environment()
    
    # Get memory information
    info['memory'] = get_memory_info()
    
    # Check for GPU
    info['gpu'] = detect_gpu()
    
    # Get CPU cores
    try:
        info['cpu_cores'] = os.cpu_count()
    except:
        info['cpu_cores'] = 'unknown'
    
    return info


def detect_environment() -> str:
    """Detect specific Unix-like environment type.
    
    Returns:
        str: Environment type (WSL2, macOS, Ubuntu, etc.)
    """
    system = platform.system()
    
    if system == 'Darwin':
        return 'macOS'
    elif system == 'Linux':
        # Check for WSL
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info:
                    return 'WSL2' if 'wsl2' in version_info else 'WSL'
        except:
            pass
        
        # Check for specific Linux distributions
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                if 'ubuntu' in os_info.lower():
                    return 'Ubuntu'
                elif 'arch' in os_info.lower():
                    return 'Arch Linux'
                elif 'debian' in os_info.lower():
                    return 'Debian'
                elif 'fedora' in os_info.lower():
                    return 'Fedora'
                elif 'centos' in os_info.lower():
                    return 'CentOS'
        except:
            pass
        
        return 'Linux (Unknown Distribution)'
    
    return system


def get_memory_info() -> dict:
    """Get system memory information.
    
    Returns:
        dict: Memory information including total and available
    """
    memory = {}
    
    try:
        # Try to read from /proc/meminfo (Linux)
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    total_kb = int(line.split()[1])
                    memory['total_gb'] = round(total_kb / 1024 / 1024, 2)
                elif line.startswith('MemAvailable:'):
                    avail_kb = int(line.split()[1])
                    memory['available_gb'] = round(avail_kb / 1024 / 1024, 2)
    except:
        # Fallback for macOS or other systems
        try:
            if platform.system() == 'Darwin':
                # macOS specific command
                result = subprocess.run(['sysctl', 'hw.memsize'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    total_bytes = int(result.stdout.split(':')[1].strip())
                    memory['total_gb'] = round(total_bytes / 1024 / 1024 / 1024, 2)
        except:
            pass
    
    if not memory:
        memory['status'] = 'Unable to determine'
    
    return memory


def detect_gpu() -> str:
    """Detect GPU presence in the system.
    
    Returns:
        str: GPU information or status
    """
    # Try nvidia-smi first
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return f"NVIDIA GPU: {result.stdout.strip()}"
    except:
        pass
    
    # Try lspci for any GPU
    try:
        result = subprocess.run(['lspci'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'VGA compatible controller' in line or 'Display controller' in line:
                    return f"GPU detected: {line.split(':', 1)[1].strip()}"
    except:
        pass
    
    return "No GPU detected or unable to determine"


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


def generate_checked_content(sys_info: dict) -> str:
    """Generate content for checked.md diagnostic file.
    
    Args:
        sys_info: System information dictionary
        
    Returns:
        str: Content for checked.md file
    """
    content = f"""# 系統診斷報告 - System Diagnostic Report

Generated by `soldcli pack2` at {sys_info['timestamp']}

## 基本資訊 Basic Information

- **使用者 User**: {sys_info['user']}
- **主機名稱 Hostname**: {sys_info['hostname']}
- **當前目錄 Current Directory**: {sys_info['pwd']}
- **Python 版本**: {sys_info['python_version']}

## 作業系統 Operating System

- **環境類型 Environment**: {sys_info['environment']}
- **系統 System**: {sys_info['os_system']}
- **版本 Release**: {sys_info['os_release']}
- **詳細版本 Version**: {sys_info['os_version'][:80]}...

## 硬體資訊 Hardware Information

### CPU
- **架構 Architecture**: {sys_info['machine']}
- **處理器 Processor**: {sys_info['processor']}
- **核心數 Cores**: {sys_info['cpu_cores']}

### 記憶體 Memory
"""
    
    if 'total_gb' in sys_info['memory']:
        content += f"- **總容量 Total**: {sys_info['memory']['total_gb']} GB\n"
        if 'available_gb' in sys_info['memory']:
            content += f"- **可用容量 Available**: {sys_info['memory']['available_gb']} GB\n"
    else:
        content += f"- **狀態 Status**: {sys_info['memory'].get('status', 'Unknown')}\n"
    
    content += f"""
### GPU
- **狀態 Status**: {sys_info['gpu']}

## Docker 相容性 Docker Compatibility

- **CPU 架構 Architecture**: {'✓ Compatible' if sys_info['machine'] in ['x86_64', 'amd64', 'arm64', 'aarch64'] else '⚠ May need special handling'}
- **建議 Docker Platform**: `{get_docker_platform(sys_info['machine'])}`

## 注意事項 Notes

1. 此診斷報告用於快速了解系統環境
2. 某些資訊可能因權限限制無法取得
3. GPU 偵測依賴於系統工具 (nvidia-smi, lspci)

---
*Generated by [soldcli](https://pypi.org/project/soldcli/)*
"""
    
    return content


def get_docker_platform(machine: str) -> str:
    """Get Docker platform string based on machine architecture.
    
    Args:
        machine: Machine architecture string
        
    Returns:
        str: Docker platform string
    """
    platform_map = {
        'x86_64': 'linux/amd64',
        'amd64': 'linux/amd64',
        'arm64': 'linux/arm64',
        'aarch64': 'linux/arm64',
        'armv7l': 'linux/arm/v7',
        'armv6l': 'linux/arm/v6',
    }
    return platform_map.get(machine, 'unknown')


def create_auxiliary_files() -> list[tuple[str, str]]:
    """Create additional auxiliary files (extension point).
    
    This function is designed to be extended by developers
    to add more diagnostic files as needed.
    
    Returns:
        list[tuple[str, str]]: List of (filename, content) tuples
    """
    # Extension point for future auxiliary files
    # Developers can add more files here
    files = []
    
    # Example: Add a README file
    readme_content = """# Diagnostic Project

This directory contains system diagnostic information generated by soldcli pack2.

## Files

- `checked.md` - Main system diagnostic report
- `README.md` - This file

## Usage

Review the diagnostic information to understand the system environment.
This is particularly useful for:
- Setting up development environments
- Troubleshooting system-specific issues
- Preparing for Docker deployments
- CI/CD environment validation

For more information, visit: https://pypi.org/project/soldcli/
"""
    files.append(('README.md', readme_content))
    
    return files


def get_auxiliary_files(sys_info: dict) -> list[tuple[str, str]]:
    """Get all auxiliary files to create.
    
    Args:
        sys_info: System information dictionary
        
    Returns:
        list[tuple[str, str]]: List of (filename, content) tuples
    """
    files = [
        ('checked.md', generate_checked_content(sys_info))
    ]
    
    # Add extension files
    files.extend(create_auxiliary_files())
    
    return files


def show_confirmation(sys_info: dict, target_dir: Path, dir_status: dict, 
                     files_to_create: list[tuple[str, str]]) -> bool:
    """Show interactive confirmation prompt.
    
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