"""run1 command implementation - experimental dynamic command generation."""

import subprocess
from typing import Dict, Any, Optional

import click

from ..tools.system_checker import SystemChecker
from ..tools.command_builder import CommandBuilder


def execute_run1(ctx: Optional[Dict[str, Any]] = None) -> bool:
    """Execute run1 command with dynamic command generation.
    
    This experimental command:
    1. Checks if tmux is installed
    2. Checks if /tmp/soldcli/test_space directory exists
    3. Generates appropriate commands based on system state
    4. Shows commands and asks for confirmation before execution
    
    Args:
        ctx: Optional context object for future extensions
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Initialize tools with context
    checker = SystemChecker(ctx)
    builder = CommandBuilder(ctx)
    
    click.echo("🔍 Checking system state...")
    click.echo()
    
    # Check tmux installation
    tmux_exists = checker.check_command_exists('tmux')
    if tmux_exists:
        click.echo("✓ tmux is already installed")
    else:
        click.echo("✗ tmux is not installed")
        os_info = checker.get_os_info()
        click.echo(f"  Detected OS: {os_info['type']} ({os_info.get('distro', 'unknown')})")
        click.echo(f"  Package manager: {os_info.get('package_manager', 'unknown')}")
        
        # Build tmux install command
        tmux_cmd = builder.build_tmux_install_command(os_info)
        if tmux_cmd:
            builder.add_command(
                command=tmux_cmd.command,
                description=tmux_cmd.description,
                check_before=tmux_cmd.check_before,
                skip_if_success=tmux_cmd.skip_if_success
            )
    
    click.echo()
    
    # Check directory existence
    test_dir = '/tmp/soldcli/test_space'
    dir_exists = checker.check_directory_exists(test_dir)
    if dir_exists:
        click.echo(f"✓ Directory {test_dir} already exists")
    else:
        click.echo(f"✗ Directory {test_dir} does not exist")
        
        # Build mkdir command
        mkdir_cmd = builder.build_mkdir_command(test_dir)
        builder.add_command(
            command=mkdir_cmd.command,
            description=mkdir_cmd.description,
            check_before=mkdir_cmd.check_before,
            skip_if_success=mkdir_cmd.skip_if_success
        )
    
    # Get all commands to execute
    commands = builder.get_commands()
    
    if not commands:
        click.echo()
        click.echo("✨ Everything is already set up! No commands needed.")
        return True
    
    # Display commands to user
    click.echo()
    click.echo("📋 Commands to execute:")
    click.echo("-" * 50)
    
    for i, cmd in enumerate(commands, 1):
        click.echo(f"{i}. {cmd.description}")
        click.echo(f"   $ {cmd.command}")
        if cmd.check_before:
            click.echo(f"   (Will check first: {cmd.check_before})")
        click.echo()
    
    # Ask for confirmation
    if not click.confirm("\n🤔 Do you want to execute these commands?"):
        click.echo("❌ Operation cancelled by user")
        return False
    
    # Execute commands
    click.echo()
    click.echo("🚀 Executing commands...")
    click.echo("-" * 50)
    
    success_count = 0
    for i, cmd in enumerate(commands, 1):
        click.echo(f"\n[{i}/{len(commands)}] {cmd.description}")
        
        # Check before execution if needed
        should_execute = True
        if cmd.check_before and cmd.skip_if_success:
            try:
                check_result = subprocess.run(
                    cmd.check_before,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if check_result.returncode == 0:
                    click.echo("   ⏭️  Skipping (already done)")
                    success_count += 1
                    should_execute = False
            except Exception:
                # If check fails, proceed with execution
                pass
        
        if should_execute:
            click.echo(f"   $ {cmd.command}")
            
            # Handle comment commands (manual instructions)
            if cmd.command.startswith('#'):
                click.echo(f"   ℹ️  {cmd.command[1:].strip()}")
                click.echo("   ⚠️  Manual action required")
                continue
            
            try:
                result = subprocess.run(
                    cmd.command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    click.echo("   ✓ Success")
                    success_count += 1
                    if result.stdout.strip():
                        click.echo(f"   Output: {result.stdout.strip()}")
                else:
                    click.echo(f"   ✗ Failed (exit code: {result.returncode})")
                    if result.stderr.strip():
                        click.echo(f"   Error: {result.stderr.strip()}")
                    
            except Exception as e:
                click.echo(f"   ✗ Error: {str(e)}")
    
    # Summary
    click.echo()
    click.echo("-" * 50)
    click.echo(f"📊 Results: {success_count}/{len(commands)} commands successful")
    
    return success_count == len(commands)