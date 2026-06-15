# CleanBot v2.0 — Windows 构建指南

> 在 Windows 10/11 上操作，一条命令构建安装包，全程约 5-10 分钟。

## 前提条件

| 软件 | 必需？ | 下载 |
|------|--------|------|
| Python 3.10+ | ✅ 必需 | https://www.python.org/downloads/ |
| NSIS 3.x | ⚠️ 安装包需要 | https://nsis.sourceforge.io/Download |

> Python 安装时务必勾选 **"Add Python to PATH"**

## 快速开始（3 步）

### 1. 获取源码

```powershell
git clone https://gitee.com/holyty/clean-bot-v2.git
cd clean-bot-v2
```

如果没装 git，直接从 Gitee 网页下载 zip 解压即可。

### 2. 构建

```powershell
# 仅需要 EXE（便携版，双击即用）
build.bat

# 需要 EXE + NSIS 安装包（标准 Windows 安装程序）
build_installer.bat
```

### 3. 得到产物

```
dist\CleanBot.exe            ← 便携版，单文件约 50-80MB
installer\CleanBot-Setup.exe ← 安装包，约 50-80MB
```

## 常见问题

### pip 安装慢/失败？

脚本已自动配置清华镜像源。如果还是慢：
1. 关闭代理/VPN
2. 或手动：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### pywin32 安装失败？

```powershell
#  pywin32 在某些 Windows 上需要手动安装
pip install pywin32
#  然后重新运行 build.bat
```

### NSIS 未安装？

构建便携 EXE 不需要 NSIS。安装包才需要。
下载 NSIS: https://nsis.sourceforge.io/Download

### 杀毒软件报毒？

PyInstaller 打包的 exe 可能被误报。添加到白名单即可。

## 发布到 Gitee

构建完成后，创建 Release 让用户下载：

1. 打开 https://gitee.com/holyty/clean-bot-v2/releases
2. 点击「创建 Release」
3. 标签: `v2.0.0`，标题: `CleanBot v2.0.0`
4. 上传 `CleanBot-Setup.exe`
5. 发布

发布后，所有用户的应用内更新检测即可生效。

## 更新发布流程

每次发布新版本只需：

1. 修改 `core/__init__.py` 中的 `__version__`
2. 修改 `core/updater.py` 中的 `CURRENT_VERSION`
3. 修改 `version.json` 中的版本号和下载链接
4. 运行 `build_installer.bat` 构建新版本
5. Gitee 创建新 Release → 上传 exe
6. Push 代码: `git push gitee main`
