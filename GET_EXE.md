# CleanBot v2.0 — 构建 EXE 安装包

> 开发者操作一次，产出 EXE。电脑小白只需双击 EXE 安装。

## 开发者：一次性构建

### 1. 安装 Python 3.12

打开 https://www.python.org/downloads/ → 点黄色大按钮下载 → 安装时 **勾选 Add Python to PATH** → 下一步 → 完成

### 2. 打开 cmd，运行：

```batch
python --version
```

确认显示 `Python 3.12.x`

### 3. 构建安装包

```batch
cd 你的clean-bot-v2目录
build_installer.bat
```

等待 5 分钟。

### 4. 得到产物

```
dist\CleanBot.exe              ← 便携版（双击即用）
installer\CleanBot-Setup.exe   ← 安装包（推荐分享）
```

## 电脑小白：使用 EXE

1. 收到 `CleanBot-Setup.exe`
2. 双击 → 下一步 → 下一步 → 完成
3. 桌面出现 CleanBot 图标 → 双击启动
4. 不需要装 Python，不需要懂电脑

## 更新策略

- EXE 安装包：适合电脑小白（推荐）
- 源码 + install.bat：适合已有 Python 3.10+ 的开发者
