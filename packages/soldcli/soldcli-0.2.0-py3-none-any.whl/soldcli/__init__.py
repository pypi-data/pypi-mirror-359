"""soldcli - 便捷命令列工具

提供快速便捷的魔術標籤功能，幫助開發者提升工作效率。
"""

__version__ = "0.2.0"
__author__ = "nphard001"
__email__ = "nphard001@gmail.com"

import logging
from .cli import main

__all__ = ["main"]

logging.getLogger("soldcli").addHandler(logging.NullHandler())