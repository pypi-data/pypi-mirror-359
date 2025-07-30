"""soldcli - 便捷命令列工具

提供快速便捷的魔術標籤功能，幫助開發者提升工作效率。
"""

import logging
from .cli import main

__all__ = ["main"]

logging.getLogger("soldcli").addHandler(logging.NullHandler())