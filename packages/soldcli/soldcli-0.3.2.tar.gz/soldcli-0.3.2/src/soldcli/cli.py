"""Main CLI interface for soldcli."""

import click
from .commands import pack1, pack2, hello, run1, run2, run3, run


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='顯示版本資訊')
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """soldcli - 便捷命令列工具
    
    提供快速便捷的魔術標籤功能，幫助開發者提升工作效率。
    """
    if version:
        from . import __version__
        click.echo(f"soldcli version {__version__}")
        return
    
    # Show help if no subcommand is provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.pass_context
def pack1(ctx: click.Context) -> None:
    """執行魔術標籤 pack1，在當前目錄產生 hint.md 檔案"""
    try:
        from .commands.pack1 import execute_pack1
        result = execute_pack1()
        
        # Use match/case for future command result handling
        match result:
            case True:
                click.echo("✓ hint.md 檔案已成功產生")
            case _:
                # Placeholder for future error cases
                click.echo("✓ hint.md 檔案已成功產生")
                
    except (OSError | PermissionError) as e:
        # Python 3.10+ union type in exception handling
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"❌ 未預期的錯誤: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.argument('project_name')
@click.option('--base-dir', default='/tmp', help='基礎目錄路徑 (預設: /tmp)')
@click.pass_context
def pack2(ctx: click.Context, project_name: str, base_dir: str) -> None:
    """建立診斷專案目錄，產生系統環境報告
    
    PROJECT_NAME: 專案目錄名稱
    """
    try:
        from .commands.pack2 import execute_pack2
        result = execute_pack2(project_name, base_dir)
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
def hello(ctx: click.Context) -> None:
    """向當前使用者打招呼"""
    try:
        from .commands.hello import execute_hello
        result = execute_hello()
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """顯示系統診斷資訊"""
    try:
        from .commands.info import execute_info
        result = execute_info()
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.argument('project_name')
@click.option('--base-dir', default='/tmp', help='基礎目錄路徑 (預設: /tmp)')
@click.option('--python', default='3.11.13', help='Python 版本 (預設: 3.11.13)')
@click.pass_context
def toml(ctx: click.Context, project_name: str, base_dir: str, python: str) -> None:
    """建立 uv 友善專案結構，包含 pyproject.toml 和 uv.toml
    
    PROJECT_NAME: 專案目錄名稱
    """
    try:
        from .commands.toml import execute_toml
        result = execute_toml(project_name, base_dir, python)
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
def run1(ctx: click.Context) -> None:
    """實驗性命令 - 動態產生並執行系統設定指令
    
    檢查系統狀態並產生相應的設定指令，包含：
    - 檢查並安裝 tmux
    - 建立必要的目錄結構
    """
    try:
        from .commands.run1 import execute_run1
        # Reserve space for potential ctx object parameters
        ctx_obj = ctx.obj if ctx.obj else {}
        result = execute_run1(ctx_obj)
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
def run2(ctx: click.Context) -> None:
    """簡單示範 - 執行三個靜態指令
    
    依序執行：
    - ping 測試網路連線
    - curl 下載測試檔案
    - rm 刪除測試檔案
    """
    try:
        from .commands.run2 import execute_run2
        # Reserve space for potential ctx object parameters
        ctx_obj = ctx.obj if ctx.obj else {}
        result = execute_run2(ctx_obj)
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
def run3(ctx: click.Context) -> None:
    """精簡示範 - 最簡化的靜態指令執行
    
    展示最直接的方式執行靜態指令清單：
    - ping 測試網路連線
    - curl 下載測試檔案
    - rm 刪除測試檔案
    """
    try:
        from .commands.run3 import execute_run3
        result = execute_run3()
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.argument('tag', required=False)
@click.option('--list', 'list_tags', is_flag=True, help='列出所有可用標籤')
@click.pass_context
def run(ctx: click.Context, tag: str, list_tags: bool) -> None:
    """Static-run: 執行標籤式靜態指令組合
    
    這是一個模組化的靜態指令執行系統。每個 TAG 對應一組預先定義的指令，
    系統會依序執行該標籤下的所有指令。
    
    TAG: 要執行的指令標籤 (如: tag1, test1209)
    
    範例:
      uvx soldcli run tag1        # 執行 tag1 的指令組合
      uvx soldcli run --list      # 列出所有可用標籤
    """
    try:
        from .commands.run import execute_static_run, list_available_tags
        
        if list_tags:
            list_available_tags()
            return
        
        if not tag:
            click.echo("❌ 請指定要執行的標籤")
            click.echo("使用 --list 查看可用標籤")
            ctx.exit(1)
        
        result = execute_static_run(tag)
        
        if not result:
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 執行失敗: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    main()