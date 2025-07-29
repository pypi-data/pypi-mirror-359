"""Main CLI interface for soldcli."""

import click
from .commands import pack1


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


if __name__ == "__main__":
    main()