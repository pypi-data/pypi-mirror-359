"""hello command implementation."""

import getpass


def execute_hello() -> bool:
    """Execute hello command to greet the current user.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        username = getpass.getuser()
        print(f"Hello, {username}! 👋")
        print(f"Welcome to soldcli - your Infrastructure as Code companion!")
        return True
    except Exception:
        print("Hello there! 👋")
        print("Welcome to soldcli - your Infrastructure as Code companion!")
        return True