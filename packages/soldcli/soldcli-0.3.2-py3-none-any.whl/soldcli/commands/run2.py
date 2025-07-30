"""run2 command - Simple static command execution example."""

import subprocess
import click
from typing import Dict, Any, Optional

from ..tools.command_builder import CommandBuilder


def execute_run2(ctx: Optional[Dict[str, Any]] = None) -> bool:
    """Execute run2 command - demonstrates simple static command pattern.
    
    This is a simplified example showing how to:
    1. Build a list of static commands
    2. Show them to the user
    3. Execute them in sequence
    
    Args:
        ctx: Optional context object (reserved for future use)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # 建立 CommandBuilder 實例
    builder = CommandBuilder(ctx)
    
    # 加入三個靜態指令
    # 1. Ping Google DNS
    builder.add_command(
        command='ping -c 3 8.8.8.8',
        description='測試網路連線 (ping Google DNS)'
    )
    
    # 2. 下載測試檔案
    builder.add_command(
        command='curl -s https://raw.githubusercontent.com/curl/curl/master/README.md -o /tmp/test.sh',
        description='下載測試檔案到 /tmp/test.sh'
    )
    
    # 3. 刪除測試檔案
    builder.add_command(
        command='rm -f /tmp/test.sh',
        description='刪除測試檔案 /tmp/test.sh'
    )
    
    # 取得要執行的指令清單
    commands = builder.get_executable_commands()
    
    if not commands:
        click.echo("沒有需要執行的指令。")
        return True
    
    # 顯示即將執行的指令
    click.echo("\n📋 即將執行以下指令:")
    for i, (cmd, desc) in enumerate(commands, 1):
        click.echo(f"{i}. {cmd}  # {desc}")
    
    # 詢問使用者確認
    click.echo()
    if not click.confirm("是否執行以上指令？", default=False):
        click.echo("已取消執行。")
        return False
    
    # 依序執行指令
    click.echo("\n開始執行...\n")
    
    for i, (cmd, desc) in enumerate(commands, 1):
        click.echo(f"[{i}/{len(commands)}] {desc}")
        click.echo(f"$ {cmd}")
        
        try:
            # 執行指令並即時顯示輸出
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=False  # 直接顯示輸出
            )
            
            if result.returncode != 0:
                click.echo(f"❌ 指令執行失敗 (返回碼: {result.returncode})", err=True)
                return False
                
            click.echo("✓ 完成\n")
            
        except Exception as e:
            click.echo(f"❌ 執行錯誤: {e}", err=True)
            return False
    
    click.echo("✅ 所有指令執行完成！")
    return True


# 如果你想要更簡單的方式，也可以不使用 CommandBuilder：
def execute_run2_simple() -> bool:
    """更簡單的實作方式 - 直接定義指令清單"""
    
    # 定義靜態指令清單
    commands = [
        ('ping -c 3 8.8.8.8', '測試網路連線'),
        ('curl -s https://raw.githubusercontent.com/curl/curl/master/README.md -o /tmp/test.sh', '下載測試檔案'),
        ('rm -f /tmp/test.sh', '刪除測試檔案')
    ]
    
    # 顯示並執行（邏輯相同）
    click.echo("\n📋 即將執行以下指令:")
    for i, (cmd, desc) in enumerate(commands, 1):
        click.echo(f"{i}. {cmd}  # {desc}")
    
    if not click.confirm("\n是否執行？", default=False):
        return False
    
    # 執行指令...
    # (省略，與上面相同)
    
    return True