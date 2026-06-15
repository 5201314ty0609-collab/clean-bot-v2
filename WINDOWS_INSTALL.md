# CleanBot v2.0 — Windows 安装指南

## 三种安装方式

| 方式 | 适合人群 | 难度 | 说明 |
|------|---------|------|------|
| **A. 便携版** | 普通用户 | ⭐ | 下载即用，双击运行 |
| **B. 安装包** | 所有用户 | ⭐ | 标准 Windows 安装程序 |
| **C. 源码安装** | 开发者 | ⭐⭐⭐ | 从源码运行 |

---

## A. 便携版（推荐）

最简方式 — 下载一个 exe 文件，双击运行。

### 1. 下载

从发布页面下载 `CleanBot.exe`：
```
https://github.com/your-username/clean-bot-v2/releases
```

### 2. 运行

双击 `CleanBot.exe` 即可启动。

首次启动会自动：
- 检查运行环境
- 显示平台兼容性提示（仅 Windows 10/11 支持全部功能）

### 3. （可选）创建桌面快捷方式

右键 `CleanBot.exe` → 发送到 → 桌面快捷方式

---

## B. 安装包方式

标准 Windows 安装程序，安装到 Program Files。

### 1. 下载安装包

```
https://github.com/your-username/clean-bot-v2/releases
```

下载 `CleanBot-Setup.exe`

### 2. 安装

双击 `CleanBot-Setup.exe`，按提示操作：
1. 欢迎页 → 下一步
2. 许可协议 → 同意
3. 选择安装目录（默认 `C:\Program Files\CleanBot`）
4. 安装 → 等待完成

安装后会自动：
- 创建桌面快捷方式
- 添加到开始菜单
- 注册到 Windows 程序列表（可在"添加/删除程序"中卸载）

### 3. 卸载

方式一：开始菜单 → CleanBot → 卸载 CleanBot

方式二：控制面板 → 添加/删除程序 → CleanBot → 卸载

---

## C. 源码安装（开发者）

### 环境要求

- **Windows 10/11**（64 位）
- **Python 3.10+**
- **Git**（可选）

### 步骤

```powershell
# 1. 克隆项目
git clone https://github.com/your-username/clean-bot-v2.git
cd clean-bot-v2

# 2. 安装依赖（国内用户使用清华镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 启动
python main.py

# 或双击运行
start.bat
```

### 国内网络问题

如果 pip 安装慢或失败，运行：
```
quick_install_cn.bat
```

---

## 自己构建安装包

如果你需要自己打包分发：

```powershell
# 仅构建便携 EXE
build.bat

# 构建 EXE + NSIS 安装包（需要先安装 NSIS）
build_installer.bat
```

构建产物：
- `dist/CleanBot.exe` — 便携版，可直接分发
- `installer/CleanBot-Setup.exe` — 安装包

---

## 国内网络说明

### 安装
安装包本身**不需要网络**。所有依赖已打包在 EXE 中，下载后即可离线安装使用。

### 更新检测
应用内置的更新检测已针对国内网络优化：

| 更新源 | 国内可达 | 说明 |
|--------|---------|------|
| Gitee API（首选） | ✅ 正常 | gitee.com，国内直连 |
| Gitee raw（备用） | ✅ 正常 | 托管 version.json |
| GitHub API（兜底） | ⚠️ 需代理 | 对开了代理的用户可用 |

如果你发现更新检测失败：
1. 打开应用 → 设置 → 软件更新 → 检查更新
2. 如果提示"检查失败"，说明当前网络无法访问所有更新源
3. 手动访问下载页获取最新版本：
   - Gitee: https://gitee.com/YOUR_GITEE_USER/clean-bot-v2/releases
   - GitHub: https://github.com/YOUR_USERNAME/clean-bot-v2/releases

### 自定义更新源
编辑 `config/update_config.json` 可以切换到自己的更新服务器：
```json
{
  "update_urls": ["https://你的服务器/version.json"],
  "download_pages": ["https://你的下载页"]
}
```

---

## 系统要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| 操作系统 | Windows 10 1809+ | Windows 11 |
| 内存 | 2 GB | 4 GB+ |
| 磁盘 | 100 MB | 200 MB |
| Python | 3.10+（仅源码安装需要） | 3.12 |

---

## 常见问题

### Q: 杀毒软件报毒？

A: CleanBot 使用 PyInstaller 打包，部分杀软可能误报。请：
- 将 CleanBot 添加到杀软白名单
- 或使用源码方式运行（`python main.py`）

### Q: 启动后界面乱码？

A: 确保系统语言为中文（简体），或修改 `main_window.py` 中的字体设置。

### Q: 需要管理员权限吗？

A: 常规清理不需要。以下功能需要管理员权限：
- 文件迁移（创建符号链接）
- 系统诊断
- 注册表相关操作

程序会在需要时自动提示提权。

### Q: 能清理多少空间？

A: 取决于你的系统使用情况，通常可以释放 1-10 GB：
- 临时文件：200 MB - 5 GB
- 浏览器缓存：100 MB - 2 GB
- 系统日志：50 MB - 2 GB
- 重复文件：不定

### Q: 删除的文件能恢复吗？

A: 默认使用回收站模式（移到回收站而非永久删除），可以在回收站中恢复。建议在"设置"中启用"备份后删除"选项。

---

## 技术支持

- GitHub Issues: https://github.com/your-username/clean-bot-v2/issues
- 项目主页: https://github.com/your-username/clean-bot-v2

---

Made with ❤️ by PHOENIX | CleanBot v2.0
