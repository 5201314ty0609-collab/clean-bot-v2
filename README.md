# CleanBot v2.0 — 智能桌面清理机器人 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![国内可用](https://img.shields.io/badge/国内可用-无需代理-green.svg)](MIRROR_CN.md)

> 一个部署在 Windows 上的**智能系统优化助手**，具备可爱的桌面机器人形象、智能诊断、实时监控、多元化清理等功能。

**🇨🇳 国内用户请注意：本项目支持国内镜像源，无需代理即可安装使用！** [查看国内镜像配置指南](MIRROR_CN.md)

---

## ✨ 核心特性

### 🤖 可爱的桌面机器人
- **卡通柯南形象**：可爱的卡通形象，支持动画和表情
- **丰富的交互**：点击、拖拽、右键菜单、对话气泡
- **动态表情**：根据状态变化表情（开心、思考、工作等）
- **随机行为**：眨眼、左右看、伸懒腰、打哈欠等
- **形象切换**：支持多种角色，可导入自定义形象

### 🔍 智能系统诊断
- **系统健康检查**：系统文件完整性、Windows 更新、还原点
- **性能瓶颈分析**：CPU、内存、磁盘使用率
- **安全漏洞检测**：Defender、防火墙、UAC 状态
- **磁盘健康监控**：磁盘错误、碎片率
- **注册表问题检测**：无效注册表项
- **服务问题检测**：关键服务状态
- **启动项问题检测**：启动项数量
- **健康评分**：0-100 分评分系统

### 🧹 多元化清理
- **深度文件清理**：临时文件、缓存、日志、重复文件
- **大文件识别**：>100MB 文件
- **旧文件识别**：>30天未访问
- **重复文件检测**：基于 SHA-256 哈希
- **安全分类**：safe, ask, skip, danger

### 📊 实时监控
- **磁盘使用监控**：实时显示 C 盘使用情况
- **趋势分析**：线性回归预测使用趋势
- **自动告警**：低空间、快速增长告警
- **历史记录**：保留 1000 条历史数据

### 💡 智能推荐
- **基于系统状态推荐**：磁盘空间、内存、CPU
- **基于使用习惯推荐**：常用应用、不常用应用缓存
- **基于历史数据推荐**：上次清理时间
- **基于时间推荐**：月初、周一清理提醒
- **空间预测**：预测 30 天后磁盘使用率

---

## 🚀 快速开始

### 安装（国内用户）

```bash
# 1. 克隆项目
git clone https://github.com/5201314ty0609-collab/clean-bot-v2.git

# 2. 进入目录
cd clean-bot-v2

# 3. 安装依赖（使用国内镜像，无需代理）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 生成机器人图片
python ui/robot/characters/conan/generate_images.py

# 5. 启动程序
python main_robot.py
```

**或者直接运行安装脚本（自动使用国内镜像）：**
```bash
# 双击 install.bat
# 或在命令行运行：
install.bat
```

### 使用

```bash
# 启动桌面机器人
python main_robot.py

# 启动主界面
python main.py

# 命令行模式
python main.py --cli

# 系统诊断
python main.py --diagnosis

# 扫描文件
python main.py --scan

# 清理文件
python main.py --clean

# 磁盘监控
python main.py --monitor

# 智能推荐
python main.py --recommend
```

---

## 🎨 形象系统

### 内置形象

| 形象 | 描述 | 状态 |
|------|------|------|
| 🕵️ **柯南** | 名侦探柯南卡通形象 | ✅ 可用 |
| 🤖 **哆啦A梦** | 哆啦A梦卡通形象 | 🔜 开发中 |
| 🐻 **小熊** | 可爱小熊形象 | 🔜 开发中 |
| 🎨 **自定义** | 用户自定义形象 | ✅ 可用 |

### 切换形象

```bash
# 命令行指定
python main_robot.py --character conan

# 形象选择器
python main_robot.py --selector
```

### 导入自定义形象

1. 准备形象配置文件（JSON 格式）
2. 打开形象选择器
3. 点击 "导入自定义形象"
4. 选择配置文件
5. 确认导入

---

## 🖥️ 主界面

### 功能导航

| 页面 | 功能 |
|------|------|
| **仪表盘** | 系统概览、健康分数、推荐 |
| **系统诊断** | 检测系统问题、给出评分 |
| **文件扫描** | 扫描可清理文件 |
| **智能推荐** | 根据习惯推荐清理方案 |
| **磁盘监控** | 实时监控磁盘使用 |
| **设置** | 配置选项 |

### 命令行

```bash
# 交互式 CLI
python main.py --cli

# 系统诊断
python main.py --diagnosis

# 扫描文件
python main.py --scan

# 清理文件
python main.py --clean

# 磁盘监控
python main.py --monitor

# 智能推荐
python main.py --recommend
```

---

## 🔒 安全机制

### 安全红线

**绝对不做的事**：
- ❌ 不删除正在运行的程序文件
- ❌ 不删除桌面上的用户文件
- ❌ 不修改注册表关键项
- ❌ 不迁移正在使用的程序文件
- ❌ 不迁移系统关键文件

### 安全措施

- ✅ **白名单机制**：只清理已知安全的文件
- ✅ **用户确认**：所有删除操作必须确认
- ✅ **可回滚**：文件移到回收站
- ✅ **备份优先**：任何可能有风险的操作先备份
- ✅ **完整日志**：记录所有操作

---

## 📁 项目结构

```
clean-bot-v2/
├── core/                        # 核心引擎
│   ├── diagnosis/              # 系统诊断
│   ├── scanner/                # 文件扫描
│   ├── cleaner/                # 文件清理
│   ├── monitor/                # 磁盘监控
│   ├── ai/                     # 智能推荐
│   └── utils.py                # 工具函数
├── ui/                          # 用户界面
│   ├── main_window.py          # 主窗口
│   ├── dashboard.py            # 仪表盘
│   └── robot/                  # 桌面机器人
│       ├── robot_widget.py    # 机器人控件
│       ├── character.py       # 角色管理
│       ├── animation.py       # 动画系统
│       ├── expression.py      # 表情系统
│       ├── character_selector.py # 形象选择器
│       └── characters/        # 角色资源
├── config/                      # 配置
├── tests/                       # 测试
├── resources/                   # 资源
├── main.py                      # 主入口
├── main_robot.py                # 桌面机器人入口
├── requirements.txt             # 依赖
├── setup.py                     # 安装脚本
├── install.bat                  # 安装脚本
├── build.bat                    # 打包脚本
└── README.md                    # 文档
```

---

## 🛠️ 开发

### 安装开发依赖

```bash
pip install -r requirements.txt
pip install pytest black flake8 pillow
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_scanner.py
pytest tests/test_diagnosis.py
```

### 代码格式化

```bash
# 格式化代码
black .

# 检查代码风格
flake8 .
```

### 生成机器人图片

```bash
# 生成柯南形象
python ui/robot/characters/conan/generate_images.py
```

### 打包成 exe

```bash
# 安装打包工具
pip install pyinstaller pillow

# 运行打包脚本
build.bat

# 获取 exe 文件
dist\CleanBot.exe
```

---

## 📚 文档

- **安装指南**：[INSTALL.md](INSTALL.md)
- **快速开始**：[QUICKSTART.md](QUICKSTART.md)
- **许可证**：[LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

```bash
# Fork 项目
# 创建分支
git checkout -b feature/my-feature

# 提交更改
git commit -m "Add my feature"

# 推送
git push origin feature/my-feature

# 创建 Pull Request
```

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目：
- [BleachBit](https://github.com/bleachbit/bleachbit)
- [Win11Debloat](https://github.com/Raphire/Win11Debloat)
- [Czkawka](https://github.com/qarmin/czkawka)
- [Optimizer](https://github.com/hellzerg/optimizer)
- [Stacer](https://github.com/oguzhaninan/Stacer)

---

## 📞 联系方式

- **GitHub Issues**：https://github.com/your-username/clean-bot-v2/issues

---

## ⭐ Star History

如果这个项目对你有帮助，请给它一个 ⭐️！

---

**CleanBot v2.0** — 让你的电脑更干净、更快速、更可爱！🎉
