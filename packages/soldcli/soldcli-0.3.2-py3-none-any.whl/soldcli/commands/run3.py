"""run3 command - Simplified static command execution."""

import subprocess
import click
from typing import List, Tuple


def execute_run3() -> bool:
    """Execute run3 command - simplified static command pattern.
    
    This demonstrates the simplest approach to executing static commands:
    1. Define a static command list
    2. Show commands to user
    3. Execute them in sequence
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # 定義靜態指令清單 (command, description)
    commands: List[Tuple[str, str]] = [
        ('ping -c 3 8.8.8.8', '測試網路連線'),
        ('curl -s https://raw.githubusercontent.com/curl/curl/master/README.md -o /tmp/test.sh', '下載測試檔案'),
        ('rm -f /tmp/test.sh', '刪除測試檔案')
    ]
    
    # 顯示即將執行的指令
    click.echo("\n📋 即將執行以下指令:")
    for i, (cmd, desc) in enumerate(commands, 1):
        click.echo(f"{i}. {cmd}  # {desc}")
    
    # 詢問使用者確認
    if not click.confirm("\n是否執行？", default=False):
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