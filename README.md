# CleanBot v2.0 — 智能桌面清理机器人

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![国内可用](https://img.shields.io/badge/国内可用-无需代理-green.svg)](MIRROR_CN.md)

> 一键启动，简单易用的系统清理工具。帮你清理电脑垃圾、释放磁盘空间、优化系统性能。

**🇨🇳 国内用户无需代理即可使用！**

---

## ✨ 核心功能

### 🔍 系统诊断
- 检测系统问题，给出健康评分 (0-100分)
- 检查 Windows 更新、防火墙、杀毒软件状态
- 识别性能瓶颈（CPU、内存、磁盘）

### 🧹 文件清理
- 扫描临时文件、缓存、日志等垃圾文件
- 识别重复文件，释放磁盘空间
- **每个文件都说明类型和删除影响，不用担心误删**

### 📁 文件迁移
- 将 C 盘大文件迁移到其他盘
- 原位置仍可正常访问，不影响使用
- 释放 C 盘空间

### 📦 应用迁移
- 将已安装应用迁移到其他盘
- 保留所有数据和设置
- 迁移后可正常打开和使用

### 🗑️ 智能删除
- 输入文件/应用路径，系统自动分析
- 显示风险等级、删除影响、关联项
- 深度清理，不留残渣（注册表、快捷方式、启动项等）
- 二次确认，避免误删

### 📊 磁盘监控
- 实时显示磁盘使用情况
- 预测磁盘何时会满
- 空间不足时自动提醒

### 💡 智能推荐
- 根据你的使用习惯推荐清理方案
- 优先清理最安全、释放空间最大的文件

---

## 🚀 快速开始

### 方式 1：一键安装（推荐）

```bash
# 1. 下载项目
git clone https://github.com/5201314ty0609-collab/clean-bot-v2.git

# 2. 进入目录
cd clean-bot-v2

# 3. 双击 install.bat
```

安装完成后，桌面会出现 "CleanBot v2.0" 快捷方式，双击即可使用。

### 方式 2：手动安装

```bash
# 1. 安装依赖
pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 双击 start.bat 启动
```

---

## 🎮 使用方法

**双击桌面快捷方式** 或 **双击 start.bat** 即可启动。

启动后会看到主界面，包含以下功能：

### 📊 仪表盘
- 查看系统概览
- 显示磁盘使用情况
- 显示健康分数

### 🔍 系统诊断
- 点击"开始诊断"按钮
- 等待诊断完成
- 查看问题列表和解决方案

### 🧹 文件扫描
- 点击"开始扫描"按钮
- 查看扫描结果
- **每个文件都会显示**：
  - 文件类型（如"临时文件"、"缓存文件"）
  - 风险等级（🟢安全/🟡低风险/🟠中风险/🔴高风险）
  - 删除影响（如"删除后应用可能变慢"）
- 勾选要清理的文件
- 点击"清理选中"按钮

### 💡 智能推荐
- 点击"刷新推荐"按钮
- 查看推荐的清理方案
- 点击"执行"按钮一键清理

### 📊 磁盘监控
- 点击"开始监控"按钮
- 实时查看磁盘使用情况
- 查看使用趋势和告警

---

## 🔒 安全保障

**我们非常重视你的数据安全：**

- ✅ **只清理安全文件**：临时文件、缓存、日志等
- ✅ **风险评估**：每个文件都有风险等级标识
- ✅ **删除影响说明**：告诉你删除后会有什么影响
- ✅ **移到回收站**：文件先移到回收站，可以随时恢复
- ✅ **用户确认**：删除前必须确认
- ✅ **完整日志**：记录所有操作

**绝对不会删除：**
- ❌ 桌面上的文件
- ❌ 正在运行的程序
- ❌ 系统关键文件
- ❌ 你的个人文档

---

## ❓ 常见问题

### Q：程序打不开怎么办？

**A**：请确保已安装 Python 3.9 或更高版本。
- 下载地址：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### Q：安装依赖失败怎么办？

**A**：打开命令提示符，运行：
```bash
pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q：杀毒软件报警怎么办？

**A**：这是误报，CleanBot 是安全的。请将 CleanBot 添加到杀毒软件白名单。

### Q：扫描很慢怎么办？

**A**：这是正常的，扫描需要检查所有文件。请耐心等待。

### Q：清理后电脑会变快吗？

**A**：会的！清理垃圾文件可以释放磁盘空间，提高系统性能。

### Q：误删文件怎么办？

**A**：不用担心，文件先移到回收站。打开回收站，找到文件，右键选择"还原"即可。

---

## 📁 项目结构

```
clean-bot-v2/
├── core/                        # 核心功能
│   ├── diagnosis/              # 系统诊断
│   ├── scanner/                # 文件扫描
│   ├── cleaner/                # 文件清理
│   ├── monitor/                # 磁盘监控
│   ├── ai/                     # 智能推荐
│   └── analyzer/               # 文件分析
├── ui/                          # 界面
│   ├── main_window.py          # 主窗口
│   └── dashboard.py            # 仪表盘
├── main.py                      # 启动入口
├── start.bat                    # 启动脚本
├── install.bat                  # 安装脚本
├── create_shortcut.bat          # 创建快捷方式
└── README.md                    # 说明文档
```

---

## 🤝 反馈与建议

如有问题或建议，请提交 Issue：
https://github.com/5201314ty0609-collab/clean-bot-v2/issues

---

## 📄 许可证

MIT License - 免费开源，可以放心使用。

---

## 🙏 致谢

感谢以下开源项目：
- [BleachBit](https://github.com/bleachbit/bleachbit)
- [Win11Debloat](https://github.com/Raphire/Win11Debloat)

---

**CleanBot v2.0** — 让你的电脑更干净、更快速！
