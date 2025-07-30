"""System diagnostic tools for soldcli."""

import os
import platform
import subprocess
import getpass
from datetime import datetime


def collect_system_info() -> dict:
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