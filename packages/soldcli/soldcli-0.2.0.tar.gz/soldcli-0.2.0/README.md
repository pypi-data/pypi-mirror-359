# soldcli - 便捷命令列工具

快速便捷的系統配置與診斷工具，專為 Unix-like 環境設計。

## 快速開始

### 安裝
```bash
pip install soldcli
```

### 基本使用

1. **生成提示檔案** - 在當前目錄建立 hint.md
```bash
soldcli pack1
```

2. **系統診斷** - 建立包含系統資訊的診斷報告
```bash
soldcli pack2 myproject              # 在 /tmp 建立診斷專案
soldcli pack2 myproject --base-dir .  # 在當前目錄建立
```

### 使用 uvx (推薦)
```bash
# 無需預先安裝，直接執行
uvx soldcli pack1
uvx soldcli pack2 test-env
```

## 主要功能

- **pack1**: 魔術標籤功能，快速生成專案提示檔案
- **pack2**: 系統環境診斷，支援 WSL2、macOS、Ubuntu、Arch Linux 等

## 版本資訊

- 需要 Python 3.10 或以上版本
- 最新版本: 0.2.0

---

# soldcli - Convenient CLI Tool

A quick and convenient system configuration and diagnostic tool designed for Unix-like environments.

## Quick Start

### Installation
```bash
pip install soldcli
```

### Basic Usage

1. **Generate hint file** - Create hint.md in current directory
```bash
soldcli pack1
```

2. **System diagnostics** - Create diagnostic report with system information
```bash
soldcli pack2 myproject              # Create in /tmp
soldcli pack2 myproject --base-dir .  # Create in current directory
```

### Using uvx (Recommended)
```bash
# Run directly without pre-installation
uvx soldcli pack1
uvx soldcli pack2 test-env
```

## Main Features

### pack1 - Magic Tag
- Generates a hint.md file in the current directory
- Contains project information and usage suggestions
- Useful for project initialization and documentation

### pack2 - System Diagnostics
- Creates a diagnostic project directory with system information
- Interactive confirmation before creation
- Detects environment type (WSL2, macOS, various Linux distributions)
- Reports:
  - OS type and version
  - CPU architecture (x86_64, arm64, etc.)
  - Memory information
  - GPU detection
  - Docker compatibility suggestions

## Supported Environments

- WSL2 (Windows Subsystem for Linux 2)
- macOS
- Ubuntu
- Arch Linux
- Other Linux distributions

## Requirements

- Python 3.10 or higher
- Unix-like operating system

## Output Files

### pack1 Output
- `hint.md` - Project hints and usage suggestions

### pack2 Output
- `checked.md` - System diagnostic report
- `README.md` - Project description
- Additional auxiliary files (extensible)

## Advanced Usage

### Custom Base Directory
```bash
# Specify a custom base directory for pack2
soldcli pack2 myproject --base-dir /home/user/diagnostics
```

### Check Version
```bash
soldcli --version
```

### Get Help
```bash
soldcli --help
soldcli pack2 --help
```

## Use Cases

1. **Remote Server Setup** - Quickly understand system environment
2. **Docker Preparation** - Check CPU architecture compatibility
3. **CI/CD Environment** - Validate build environment
4. **Development Setup** - Document system specifications
5. **Troubleshooting** - Gather system information for debugging

## Development

This tool is part of the soldpack project, focusing on Infrastructure as Code practices.

- Repository: [soldpack](https://github.com/soldpack/soldpack)
- PyPI: [soldcli](https://pypi.org/project/soldcli/)

## License

MIT License

## Changelog

- **v0.2.0** - Added pack2 system diagnostics with interactive confirmation
- **v0.1.0** - Initial release with pack1 magic tag functionality