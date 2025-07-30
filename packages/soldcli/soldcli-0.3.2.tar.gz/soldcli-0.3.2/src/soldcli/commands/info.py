"""info command implementation - Display system diagnostic information."""

import click
from ..tools.system_diagnostics import collect_system_info


def execute_info() -> bool:
    """Execute info command to display system diagnostic information.
    
    Returns:
        bool: Always returns True as this is display-only
    """
    # Collect system information
    sys_info = collect_system_info()
    
    # Display header
    click.echo("\n" + "="*60)
    click.echo("系統診斷資訊 - System Diagnostic Information")
    click.echo("="*60)
    
    # Basic information
    click.echo(f"\n執行時間 Timestamp: {click.style(sys_info['timestamp'], fg='cyan')}")
    click.echo(f"執行身份 User: {click.style(sys_info['user'], fg='cyan')}")
    click.echo(f"主機名稱 Hostname: {click.style(sys_info['hostname'], fg='cyan')}")
    click.echo(f"當前目錄 PWD: {click.style(sys_info['pwd'], fg='cyan')}")
    
    # Python environment
    click.echo(f"\nPython 版本 Version: {click.style(sys_info['python_version'], fg='green')}")
    click.echo(f"執行環境 Environment: {click.style(sys_info['environment'], fg='green')}")
    
    # System information
    click.echo(f"\n作業系統 OS: {click.style(sys_info['os_system'], fg='yellow')}")
    click.echo(f"系統版本 Release: {click.style(sys_info['os_release'], fg='yellow')}")
    click.echo(f"詳細版本 Version: {click.style(sys_info['os_version'], fg='yellow')}")
    
    # Hardware information
    click.echo(f"\n機器架構 Machine: {click.style(sys_info['machine'], fg='magenta')}")
    click.echo(f"處理器 Processor: {click.style(sys_info['processor'], fg='magenta')}")
    click.echo(f"CPU 核心數 Cores: {click.style(str(sys_info['cpu_cores']), fg='magenta')}")
    click.echo(f"記憶體 Memory: {click.style(sys_info['memory'], fg='magenta')}")
    
    if sys_info['gpu'] != 'N/A':
        click.echo(f"GPU 資訊: {click.style(sys_info['gpu'], fg='magenta')}")
    
    click.echo("\n" + "="*60 + "\n")
    
    return True