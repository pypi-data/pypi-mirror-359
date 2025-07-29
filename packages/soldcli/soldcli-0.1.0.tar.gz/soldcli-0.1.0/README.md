# soldcli - 便捷命令列工具

## 相關文件

- **整體架構**: [../../../plan/soldpack.md](../../../plan/soldpack.md) - Infrastructure as Code 理念
- **開發討論**: [../../../idea/soldcli.md](../../../idea/soldcli.md) - 設計決策與功能討論
- **建置流程**: [toBuild.md](toBuild.md) - PYPI 發布詳細步驟
- **套件集合**: [../README.md](../README.md) - soldpack 整體說明

一個輕量級的 Python CLI 工具，提供快速便捷的魔術標籤功能，幫助開發者提升工作效率。

## 功能特色

- **魔術標籤系統**：透過簡單指令產生實用的提示檔案
- **原地檔案產生**：直接在當前目錄建立 `hint.md` 檔案
- **簡潔介面**：清晰易懂的命令列互動
- **模組化執行**：支援 `python -m soldcli` 方式執行

## 安裝方式

```bash
pip install soldcli
```

### 從原始碼安裝
```bash
git clone [repository-url]
cd soldpack/soldcli-PYPI
pip install -e .
```

## 使用方法

### 基本指令

```bash
# 顯示幫助資訊
python -m soldcli --help

# 執行魔術標籤 pack1
python -m soldcli pack1

# 查看版本資訊
python -m soldcli --version
```

### 使用範例

#### 1. 產生提示檔案

```bash
# 在當前目錄執行
python -m soldcli pack1
```

執行後，會在目前位置產生 `hint.md` 檔案，內容包含相關的使用提示和說明。

#### 2. 查看可用選項

```bash
python -m soldcli --help
```

這會顯示所有可用的命令和選項說明。

## 輸出檔案說明

### hint.md
當執行 `pack1` 命令時，工具會在當前目錄建立 `hint.md` 檔案，該檔案包含：
- 使用建議和最佳實踐
- 相關的技術提示
- 進階功能說明

檔案會自動覆寫既存的 `hint.md`，請注意備份重要內容。

## 進階用法

### 在不同目錄執行

```bash
# 切換到目標目錄
cd /path/to/your/project

# 執行命令
python -m soldcli pack1
```

### 整合到工作流程

可以將 soldcli 整合到您的開發流程中：

```bash
# 在專案初始化時產生提示檔案
python -m soldcli pack1

# 檢視產生的提示內容
cat hint.md
```

## 故障排除

### 常見問題

**Q: 執行時出現 "Module not found" 錯誤**
```bash
# 確認安裝狀態
pip list | grep soldcli

# 重新安裝
pip install --upgrade soldcli
```

**Q: hint.md 檔案沒有產生**
- 檢查當前目錄的寫入權限
- 確認已正確安裝 soldcli
- 嘗試使用 `python -m soldcli --help` 確認工具正常運作

**Q: 如何更新到最新版本**
```bash
pip install --upgrade soldcli
```

### 系統需求

- Python 3.10+
- 支援 Windows、macOS、Linux
- 無額外系統依賴

## 開發指南

### 本地開發

```bash
# 克隆專案
git clone [repository-url]
cd soldpack/soldcli-PYPI

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝開發版本
pip install -e .

# 執行測試
python -m pytest  # 如果有測試檔案
```

### 貢獻方式

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 版本歷史

- **v0.1.0** - 初始版本，支援基本魔術標籤功能

## 授權資訊

[待補充授權資訊]

## 支援與回饋

如遇到問題或有功能建議，歡迎：
- 開啟 GitHub Issue
- 提交 Pull Request
- 聯繫維護團隊

---

更多資訊請參考主專案 [soldpack](../README.md) 說明文件。