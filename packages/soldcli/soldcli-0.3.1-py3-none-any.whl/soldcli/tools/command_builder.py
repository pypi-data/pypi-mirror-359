"""Dynamic command building utilities."""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Command:
    """Represents a shell command with metadata."""
    
    command: str
    description: str
    check_before: Optional[str] = None  # Command to check before executing
    skip_if_success: bool = False  # Skip if check_before succeeds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'command': self.command,
            'description': self.description,
            'check_before': self.check_before,
            'skip_if_success': self.skip_if_success
        }


class CommandBuilder:
    """Build dynamic commands based on system state."""
    
    def __init__(self, ctx: Optional[Dict[str, Any]] = None):
        """Initialize command builder.
        
        Args:
            ctx: Optional context object for future extensions
        """
        self.ctx = ctx or {}
        self.commands: List[Command] = []
    
    def add_command(self, command: str, description: str, 
                   check_before: Optional[str] = None,
                   skip_if_success: bool = False) -> None:
        """Add a command to the build queue.
        
        Args:
            command: Shell command to execute
            description: Human-readable description
            check_before: Optional command to check before executing
            skip_if_success: Skip if check_before succeeds
        """
        self.commands.append(Command(
            command=command,
            description=description,
            check_before=check_before,
            skip_if_success=skip_if_success
        ))
    
    def build_tmux_install_command(self, os_info: Dict[str, Any]) -> Optional[Command]:
        """Build OS-specific tmux installation command.
        
        Args:
            os_info: Operating system information
            
        Returns:
            Command object or None if unsupported
        """
        os_type = os_info.get('type', '').lower()
        pkg_mgr = os_info.get('package_manager')
        
        install_commands = {
            'apt': 'sudo apt-get update && sudo apt-get install -y tmux',
            'yum': 'sudo yum install -y tmux',
            'dnf': 'sudo dnf install -y tmux',
            'pacman': 'sudo pacman -S --noconfirm tmux',
            'zypper': 'sudo zypper install -y tmux',
            'apk': 'sudo apk add tmux',
            'brew': 'brew install tmux',
            'winget': 'winget install --id=GNU.tmux -e',
            'choco': 'choco install tmux -y',
            'scoop': 'scoop install tmux'
        }
        
        if pkg_mgr and pkg_mgr in install_commands:
            return Command(
                command=install_commands[pkg_mgr],
                description=f"Install tmux using {pkg_mgr}",
                check_before='which tmux',
                skip_if_success=True
            )
        
        # Fallback suggestions
        if os_type == 'linux':
            return Command(
                command='# Please install tmux using your distribution package manager',
                description='Manual tmux installation required'
            )
        elif os_type == 'darwin':
            return Command(
                command='# Install Homebrew first: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                description='Homebrew installation required for tmux'
            )
        elif os_type == 'windows':
            return Command(
                command='# Install tmux via WSL or use Windows Terminal',
                description='tmux installation on Windows'
            )
        
        return None
    
    def build_mkdir_command(self, path: str) -> Command:
        """Build directory creation command.
        
        Args:
            path: Directory path to create
            
        Returns:
            Command object
        """
        return Command(
            command=f'mkdir -p "{path}"',
            description=f'Create directory: {path}',
            check_before=f'test -d "{path}"',
            skip_if_success=True
        )
    
    def get_commands(self) -> List[Command]:
        """Get all built commands.
        
        Returns:
            List of Command objects
        """
        return self.commands
    
    def clear(self) -> None:
        """Clear all commands."""
        self.commands = []
    
    def get_executable_commands(self) -> List[Tuple[str, str]]:
        """Get commands ready for execution.
        
        Returns:
            List of (command, description) tuples
        """
        return [(cmd.command, cmd.description) for cmd in self.commands]