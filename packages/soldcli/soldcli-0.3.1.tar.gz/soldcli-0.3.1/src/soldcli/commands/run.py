"""run command - Tag-based static command execution system."""

import subprocess
import click
from typing import List, Tuple, Dict, Optional


class StaticRunRegistry:
    """Registry for tag-based static command sets."""
    
    def __init__(self):
        self._tags: Dict[str, List[Tuple[str, str]]] = {}
        self._register_builtin_tags()
    
    def _register_builtin_tags(self) -> None:
        """Register built-in command tags."""
        
        # tag1 - Network and file operations demo
        self.register_tag('tag1', [
            ('ping -c 3 8.8.8.8', '測試網路連線'),
            ('curl -s https://raw.githubusercontent.com/curl/curl/master/README.md -o /tmp/test.sh', '下載測試檔案'),
            ('rm -f /tmp/test.sh', '刪除測試檔案')
        ])
        
        self.register_tag('demo', [
            ('whoami', '顯示你誰'),
            ('which uv', '查一下有沒有uv')
        ])
        
        self.register_tag('qtwu', [
            *[(f'mkdir -p /{item}', 'qtwu 風格的根目錄物件') for item in ['active', 'dat', 'tmp2']],
        ])
        
        self.register_tag('qtwu1122', [
            ('uvx soldcli run qtwu && mkdir -p /dat/runpy/', '確保qtwu風格目錄被建立並製造隔離環境'),
            ('cd /dat/runpy/ && uvx soldcli toml qtwu1122 --base-dir .', '建立基本Python3.11與Node22環境'),
            *[(f'cd /dat/runpy/qtwu1122 && {CMD}', '建立基本Python3.11與Node22環境') for CMD in [
                "uv venv",
                "uv add nodeenv",
                "uv run nodeenv -n 22.16.0 .node22 --prompt NODE22 --verbose",
            ]],
            
        ])
        
    
    def register_tag(self, tag: str, commands: List[Tuple[str, str]]) -> None:
        """Register a new tag with its command set.
        
        Args:
            tag: Tag name
            commands: List of (command, description) tuples
        """
        self._tags[tag] = commands
    
    def get_commands(self, tag: str) -> Optional[List[Tuple[str, str]]]:
        """Get commands for a specific tag.
        
        Args:
            tag: Tag name
            
        Returns:
            List of (command, description) tuples, or None if tag not found
        """
        return self._tags.get(tag)
    
    def list_tags(self) -> List[str]:
        """Get list of available tags."""
        return list(self._tags.keys())
    
    def get_tag_info(self, tag: str) -> Optional[str]:
        """Get description info for a tag."""
        commands = self.get_commands(tag)
        if not commands:
            return None
        
        descriptions = [desc for _, desc in commands]
        return f"包含 {len(commands)} 個指令: " + ", ".join(descriptions)


# Global registry instance
_registry = StaticRunRegistry()


def execute_static_run(tag: str) -> bool:
    """Execute static commands for a specific tag.
    
    Args:
        tag: Tag name to execute
        
    Returns:
        bool: True if successful, False otherwise
    """
    commands = _registry.get_commands(tag)
    
    if not commands:
        click.echo(f"❌ 找不到標籤 '{tag}'")
        click.echo(f"可用標籤: {', '.join(_registry.list_tags())}")
        return False
    
    # 顯示標籤資訊
    click.echo(f"\n🏷️ 執行標籤: {tag}")
    tag_info = _registry.get_tag_info(tag)
    if tag_info:
        click.echo(f"📝 {tag_info}")
    
    # 顯示即將執行的指令
    click.echo("\n📋 即將執行的 static-run 指令:")
    for i, (cmd, desc) in enumerate(commands, 1):
        click.echo(f"{i}. {cmd}  # {desc}")
    
    # 詢問使用者確認
    if not click.confirm("\n是否執行以上指令？", default=False):
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
    
    click.echo(f"✅ 標籤 '{tag}' 的所有指令執行完成！")
    return True


def list_available_tags() -> None:
    """List all available tags with their descriptions."""
    tags = _registry.list_tags()
    
    if not tags:
        click.echo("沒有可用的標籤。")
        return
    
    click.echo("📋 可用的 static-run 標籤:")
    for tag in sorted(tags):
        tag_info = _registry.get_tag_info(tag)
        if tag_info:
            click.echo(f"  {tag}: {tag_info}")
        else:
            click.echo(f"  {tag}")


def register_new_tag(tag: str, commands: List[Tuple[str, str]]) -> None:
    """Register a new tag (for future extension)."""
    _registry.register_tag(tag, commands)