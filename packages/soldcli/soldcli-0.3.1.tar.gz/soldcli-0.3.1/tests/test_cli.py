"""Tests for CLI functionality."""

import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from soldcli.cli import main
from soldcli.commands.pack1 import execute_pack1


def test_main_help():
    """測試主命令的幫助顯示"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'soldcli' in result.output
    assert '便捷命令列工具' in result.output


def test_version_flag():
    """測試版本資訊顯示"""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert 'soldcli version' in result.output


def test_pack1_command():
    """測試 pack1 命令執行"""
    runner = CliRunner()
    
    # 在臨時目錄中執行測試
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = runner.invoke(main, ['pack1'])
            
            # 檢查命令執行成功
            assert result.exit_code == 0
            assert 'hint.md 檔案已成功產生' in result.output
            
            # 檢查檔案是否產生
            hint_file = Path(temp_dir) / 'hint.md'
            assert hint_file.exists()
            
            # 檢查檔案內容
            content = hint_file.read_text(encoding='utf-8')
            assert '# Hint - soldcli pack1' in content
            assert 'soldcli v0.1.0' in content
            
        finally:
            os.chdir(original_cwd)


def test_pack1_function_directly():
    """直接測試 pack1 函數"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            execute_pack1()
            
            # 檢查檔案是否產生
            hint_file = Path(temp_dir) / 'hint.md'
            assert hint_file.exists()
            
            # 檢查檔案內容
            content = hint_file.read_text(encoding='utf-8')
            assert '# Hint - soldcli pack1' in content
            
        finally:
            os.chdir(original_cwd)


def test_no_command_shows_help():
    """測試沒有子命令時顯示幫助"""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert 'Usage:' in result.output