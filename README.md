# CleanBot v2.0 — 智能桌面清理机器人

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![国内可用](https://img.shields.io/badge/国内可用-无需代理-green.svg)](MIRROR_CN.md)

> 一个部署在 Windows 上的**智能系统优化助手**，支持智能诊断、实时监控、多元化清理等功能。

**🇨🇳 国内用户请注意：本项目支持国内镜像源，无需代理即可安装使用！** [查看国内镜像配置指南](MIRROR_CN.md)

---

## ✨ 核心特性

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
- **智能分析**：50+ 文件类型识别，风险评估，删除影响说明

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

# 4. 启动程序
python main.py
```

**或者直接运行安装脚本（自动使用国内镜像）：**
```bash
# 双击 install.bat
# 或在命令行运行：
install.bat
```

### 创建桌面快捷方式

```bash
# 运行快捷方式创建脚本
create_shortcut.bat
```

---

## 🎮 使用方式

### 启动程序

```bash
# 方式 1：双击桌面快捷方式（推荐）
# 方式 2：双击 start.bat
# 方式 3：命令行启动
python main.py
```

### 模式选择

启动后会显示模式选择界面：

```
============================================================
  CleanBot v2.0 — 智能桌面清理机器人
============================================================

请选择运行模式:

  1. GUI 模式      - 图形界面（推荐）
  2. CLI 模式      - 命令行界面
  3. 系统诊断      - 检测系统问题
  4. 文件扫描      - 扫描可清理文件
  5. 磁盘监控      - 实时监控磁盘使用
  6. 智能推荐      - 获取清理建议
  7. 快速清理      - 一键清理安全文件
  8. 退出

请输入选项 (1-8):
```

### 命令行参数

```bash
# 直接启动 GUI
python main.py --gui

# 直接启动 CLI
python main.py --cli

# 运行系统诊断
python main.py --diagnosis

# 启动磁盘监控
python main.py --monitor

# 获取智能推荐
python main.py --recommend

# 扫描文件系统
python main.py --scan

# 清理文件
python main.py --clean

# 快速清理安全文件
python main.py --quick
```

---

## 🔍 系统诊断

```bash
python main.py --diagnosis
```

输出示例：

```
系统健康分数: 85/100

发现的问题:

  1. 🟠 CPU 使用率过高
     当前 CPU 使用率 85%，可能影响系统响应速度
     解决方案: 检查并关闭占用 CPU 较高的程序

  2. 🟡 磁盘 C: 使用率 85%
     磁盘 C: 已使用 85%，剩余空间不足
     解决方案: 清理磁盘空间或扩展磁盘容量

推荐:
  - 关闭占用 CPU 较高的程序
  - 清理磁盘空间
```

---

## 🧹 文件清理

### 扫描文件

```bash
python main.py --scan
```

输出示例：

```
扫描完成!

总文件数: 125,432
总大小: 45.2 GB
扫描时间: 12.34 秒

可安全删除:
  文件数: 1,234
  大小: 2.3 GB

需要确认:
  文件数: 567
  大小: 1.8 GB

最大的 10 个文件:
  1.    2.5 GB C:\Users\...\Downloads\video.mp4
  2.    1.2 GB C:\...\Windows\Installer\...
```

### 快速清理

```bash
python main.py --quick
```

输出示例：

```
发现 1,234 个安全文件，共 2.3 GB

这些文件包括:
  - 临时文件 (.tmp, .temp)
  - 缓存文件 (.cache)
  - 日志文件 (.log)
  - 系统垃圾 (thumbs.db, .ds_store)

确认清理？(y/N):
```

---

## 📊 磁盘监控

```bash
python main.py --monitor
```

输出示例：

```
磁盘使用情况:

  C:\ [████████████████████░░░░░░░░░░] 65.2%
       326.0 GB / 500.0 GB

使用趋势:
  C:\: ↑ 0.5 GB/天
    ⚠️ 预计 15 天后磁盘满

⚠️ 告警:
  🟡 磁盘 C: 空间不足 (65.2%)
```

---

## 💡 智能推荐

```bash
python main.py --recommend
```

输出示例：

```
生成了 5 个推荐:

1. 🔴 清理磁盘 C:
   磁盘 C: 使用率 85%，建议清理空间
   类别: cleanup
   优先级: 8/10
   风险: low
   预计节省: 5.00 GB

2. 🟡 清理 Chrome 缓存
   Chrome 缓存占用 500.00 MB
   类别: cleanup
   优先级: 6/10
   风险: low
   预计节省: 500.00 MB
```

---

## 🖥️ GUI 界面

```bash
python main.py --gui
```

### 功能导航

| 页面 | 功能 |
|------|------|
| **仪表盘** | 系统概览、健康分数、推荐 |
| **系统诊断** | 检测系统问题、给出评分 |
| **文件扫描** | 扫描可清理文件 |
| **智能推荐** | 根据习惯推荐清理方案 |
| **磁盘监控** | 实时监控磁盘使用 |
| **设置** | 配置选项 |

### 扫描结果

扫描结果包含详细信息：

| 列 | 说明 |
|----|------|
| 选择 | 勾选要清理的文件 |
| 路径 | 文件完整路径 |
| 大小 | 文件大小 |
| 类型 | 文件类型名称（如"临时文件"、"缓存文件"） |
| 风险 | 风险等级（🟢安全/🟡低/🟠中/🔴高） |
| 影响 | 删除后的影响说明 |
| 时间 | 最后修改时间 |

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
- ✅ **风险评估**：每个文件都有风险等级和删除影响说明

### 恢复文件

如果误删文件，可以从回收站恢复：

1. 打开回收站
2. 找到被删除的文件
3. 右键 → 还原

---

## 📁 项目结构

```
clean-bot-v2/
├── core/                        # 核心引擎
│   ├── diagnosis/              # 系统诊断
│   ├── scanner/                # 文件扫描
│   ├── cleaner/                # 文件清理
│   ├── monitor/                # 磁盘监控
│   ├── ai/                     # 智能推荐 + 对话系统
│   ├── analyzer/               # 智能文件分析器
│   └── utils.py                # 工具函数
├── ui/                          # 用户界面
│   ├── main_window.py          # 主窗口
│   └── dashboard.py            # 仪表盘
├── config/                      # 配置
├── tests/                       # 测试
├── resources/                   # 资源
├── main.py                      # 主入口（模式选择）
├── start.bat                    # 启动脚本
├── create_shortcut.bat          # 创建桌面快捷方式
├── requirements.txt             # 依赖
├── setup.py                     # 安装脚本
├── install.bat                  # 安装脚本
├── README.md                    # 文档
├── INSTALL.md                   # 安装指南
├── QUICKSTART.md                # 快速开始
├── MIRROR_CN.md                 # 国内镜像配置
└── LICENSE                      # 许可证
```

---

## ❓ 常见问题

### Q1：程序无法启动

**解决**：
```bash
# 检查 Python
python --version

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2：pip 安装失败

**解决**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Q3：杀毒软件误报

**解决**：
1. 将 CleanBot 添加到杀毒软件白名单
2. 或暂时关闭杀毒软件

### Q4：扫描速度慢

**解决**：
```bash
# 减少扫描深度
python main.py --scan --depth 3
```

---

## 📚 文档

- **README.md**：项目介绍和快速开始
- **INSTALL.md**：详细安装指南
- **QUICKSTART.md**：快速开始指南
- **MIRROR_CN.md**：国内镜像源配置指南

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

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

## 🔗 相关链接

- **GitHub 仓库**：https://github.com/5201314ty0609-collab/clean-bot-v2
- **下载 ZIP**：https://github.com/5201314ty0609-collab/clean-bot-v2/archive/refs/heads/main.zip
- **Issues**：https://github.com/5201314ty0609-collab/clean-bot-v2/issues

---

**CleanBot v2.0** — 让你的电脑更干净、更快速！
