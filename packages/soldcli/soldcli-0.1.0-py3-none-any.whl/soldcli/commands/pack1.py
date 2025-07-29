"""pack1 command implementation."""

import os
from datetime import datetime
from pathlib import Path


def execute_pack1() -> bool:
    """Execute pack1 command to generate hint.md file in current directory.
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        OSError: When unable to write file
        PermissionError: When lacking write permissions
    """
    current_dir = Path.cwd()
    hint_file = current_dir / "hint.md"
    
    # Prepare hint.md content
    content = generate_hint_content()
    
    try:
        # Write file (overwrite if exists)
        hint_file.write_text(content, encoding='utf-8')
        return True
    except (OSError | PermissionError) as e:
        # Using Python 3.10+ union type
        raise OSError(f"無法寫入 hint.md 檔案: {e}") from e


def generate_hint_content() -> str:
    """Generate content for hint.md file.
    
    Returns:
        str: Content for hint.md file
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_dir = Path.cwd().name
    
    content = f"""# Hint - soldcli pack1

此檔案由 `soldcli pack1` 於 {current_time} 自動產生。

## 專案資訊

- **目錄**: {current_dir}
- **產生工具**: soldcli v0.1.0
- **命令**: `python -m soldcli pack1` 或 `uvx soldcli pack1`

## 使用建議

### 基本用法
```bash
# 顯示幫助
python -m soldcli --help

# 執行 pack1 命令
python -m soldcli pack1

# 使用 uv/uvx (推薦)
uvx soldcli pack1
```

### 最佳實踐

1. **定期更新**: 當專案結構變更時，重新執行 pack1 更新此檔案
2. **版本控制**: 可以將此檔案加入 .gitignore 或提交到版本控制
3. **自動化**: 可以整合到開發流程中自動執行

### 進階功能

目前 soldcli 專注於基本的魔術標籤功能，未來版本將會加入：
- 更多魔術標籤選項
- 自訂內容模板
- 專案分析功能
- 整合其他開發工具

## 注意事項

- 此檔案會覆寫既存的 hint.md，請注意備份重要內容
- 需要當前目錄的寫入權限
- 支援 Python 3.10+ 環境

---

*由 [soldcli](https://github.com/soldpack/soldpack) 自動產生*
"""
    
    return content