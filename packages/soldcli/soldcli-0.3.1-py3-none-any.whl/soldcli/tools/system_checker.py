"""System state checking utilities."""

import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class SystemChecker:
    """Check system state and available tools."""
    
    def __init__(self, ctx: Optional[Dict[str, Any]] = None):
        """Initialize system checker.
        
        Args:
            ctx: Optional context object for future extensions
        """
        self.ctx = ctx or {}
        self.os_type = platform.system().lower()
        self.distro = self._detect_distro()
    
    def _detect_distro(self) -> Optional[str]:
        """Detect Linux distribution if on Linux."""
        if self.os_type != 'linux':
            return None
        
        try:
            # Try to read from /etc/os-release
            if Path('/etc/os-release').exists():
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            return line.split('=')[1].strip().strip('"')
        except Exception:
            pass
        
        return None
    
    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH.
        
        Args:
            command: Command name to check
            
        Returns:
            bool: True if command exists, False otherwise
        """
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_directory_exists(self, path: str) -> bool:
        """Check if a directory exists.
        
        Args:
            path: Directory path to check
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        return Path(path).is_dir()
    
    def get_os_info(self) -> Dict[str, Any]:
        """Get operating system information.
        
        Returns:
            dict: OS information including type, distro, and package manager
        """
        info = {
            'type': self.os_type,
            'distro': self.distro,
            'package_manager': self._detect_package_manager()
        }
        
        # Add architecture info
        info['arch'] = platform.machine()
        
        return info
    
    def _detect_package_manager(self) -> Optional[str]:
        """Detect the system's package manager."""
        if self.os_type == 'darwin':
            # macOS
            if self.check_command_exists('brew'):
                return 'brew'
            return 'brew'  # Suggest brew even if not installed
        
        elif self.os_type == 'linux':
            # Common Linux package managers
            if self.check_command_exists('apt-get'):
                return 'apt'
            elif self.check_command_exists('yum'):
                return 'yum'
            elif self.check_command_exists('dnf'):
                return 'dnf'
            elif self.check_command_exists('pacman'):
                return 'pacman'
            elif self.check_command_exists('zypper'):
                return 'zypper'
            elif self.check_command_exists('apk'):
                return 'apk'
        
        elif self.os_type == 'windows':
            # Windows package managers
            if self.check_command_exists('winget'):
                return 'winget'
            elif self.check_command_exists('choco'):
                return 'choco'
            elif self.check_command_exists('scoop'):
                return 'scoop'
        
        return None