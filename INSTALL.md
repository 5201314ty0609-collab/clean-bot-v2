# CleanBot v2.0 — Windows 安装指南

## 🎉 欢迎使用 CleanBot v2.0！

CleanBot 是一个**智能桌面清理机器人**，具备以下特性：
- 🤖 **可爱的桌面机器人**：卡通柯南形象，支持动画和表情
- 🔍 **智能系统诊断**：自动检测系统问题
- 🧹 **多元化清理**：文件、缓存、日志、重复文件
- 📊 **实时监控**：磁盘使用情况、趋势分析
- 💡 **智能推荐**：根据使用习惯推荐清理方案

---

## 📋 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 10/11 (64-bit) |
| **Python** | 3.9 或更高版本 |
| **内存** | 4GB 或更多 |
| **磁盘空间** | 200MB 可用空间 |
| **显示器** | 1024x768 或更高分辨率 |

---

## 🚀 快速安装（5分钟）

### 方式 1：一键安装（推荐）

#### 步骤 1：下载项目

```bash
# 方式 A：使用 git（推荐）
git clone https://github.com/your-username/clean-bot-v2.git

# 方式 B：下载 ZIP
# 1. 访问 GitHub 页面
# 2. 点击 "Code" → "Download ZIP"
# 3. 解压到任意目录
```

#### 步骤 2：运行安装脚本

```bash
# 进入项目目录
cd clean-bot-v2

# 双击运行 install.bat
# 或在命令行中运行：
install.bat
```

安装脚本会自动：
- ✅ 检查 Python 环境
- ✅ 安装所有依赖包
- ✅ 创建启动脚本
- ✅ 创建桌面快捷方式

#### 步骤 3：启动程序

```bash
# 方式 A：双击桌面快捷方式 "CleanBot v2.0"
# 方式 B：运行启动脚本
start.bat

# 方式 C：命令行
python main.py
```

---

### 方式 2：手动安装

#### 步骤 1：安装 Python

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.9 或更高版本
3. **重要**：安装时勾选 ✅ "Add Python to PATH"
4. 验证安装：
   ```bash
   python --version
   # 应该显示 Python 3.9.x 或更高版本
   ```

#### 步骤 2：安装依赖

```bash
# 进入项目目录
cd clean-bot-v2

# 安装依赖
pip install -r requirements.txt
```

**如果 pip 速度慢，使用国内镜像：**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 步骤 3：运行程序

```bash
# 启动主界面
python main.py

# 启动桌面机器人
python main_robot.py

# 命令行模式
python main.py --cli
```

---

### 方式 3：打包成 exe（便携版）

#### 步骤 1：安装打包工具

```bash
pip install pyinstaller pillow
```

#### 步骤 2：生成机器人图片

```bash
# 生成柯南形象图片
python ui/robot/characters/conan/generate_images.py
```

#### 步骤 3：运行打包脚本

```bash
# 运行打包脚本
build.bat
```

#### 步骤 4：获取 exe 文件

打包完成后，在 `dist` 目录下找到 `CleanBot.exe`。

---

### 方式 4：完整安装包

#### 步骤 1：安装 NSIS

1. 访问 https://nsis.sourceforge.io/Download
2. 下载并安装 NSIS
3. 将 NSIS 添加到 PATH 环境变量

#### 步骤 2：构建安装包

```bash
# 运行构建脚本
build_installer.bat
```

#### 步骤 3：分发安装包

在 `installer` 目录下找到 `CleanBot-Setup.exe`。

---

## 🎮 使用指南

### 启动桌面机器人

```bash
# 默认使用柯南形象
python main_robot.py

# 指定角色
python main_robot.py --character conan

# 打开形象选择器
python main_robot.py --selector
```

### 机器人交互

| 操作 | 效果 |
|------|------|
| **单击** | 触发点击事件 |
| **双击** | 打开主界面 |
| **右键** | 显示菜单 |
| **拖拽** | 移动位置 |

### 右键菜单功能

- **切换角色**：选择不同形象（柯南、哆啦A梦等）
- **设置状态**：空闲、思考、工作、开心、难过
- **测试对话**：显示对话气泡
- **退出**：关闭程序

### 系统托盘

- **显示/隐藏**：控制机器人显示
- **切换角色**：快速切换形象
- **选择形象**：打开形象选择器
- **退出**：关闭程序

---

## 🖥️ 主界面功能

### 启动主界面

```bash
python main.py
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

### 命令行模式

```bash
# 运行系统诊断
python main.py --diagnosis

# 扫描文件系统
python main.py --scan

# 清理文件
python main.py --clean

# 磁盘监控
python main.py --monitor

# 智能推荐
python main.py --recommend

# 交互式 CLI
python main.py --cli
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
# 方式 1：命令行指定
python main_robot.py --character conan

# 方式 2：右键菜单
# 右键机器人 → 切换角色 → 选择形象

# 方式 3：形象选择器
python main_robot.py --selector

# 方式 4：系统托盘
# 右键托盘图标 → 切换角色 → 选择形象
```

### 导入自定义形象

1. 准备形象配置文件（JSON 格式）
2. 打开形象选择器
3. 点击 "导入自定义形象"
4. 选择配置文件
5. 确认导入

**配置文件示例：**
```json
{
  "id": "my_character",
  "name": "我的形象",
  "description": "自定义形象",
  "size": {"width": 200, "height": 200},
  "colors": {
    "primary": "#2196F3",
    "secondary": "#FF6B6B"
  },
  "images": {
    "idle": "idle.png",
    "happy": "happy.png"
  }
}
```

---

## ⚙️ 配置文件

### 配置文件位置

```
config/settings.json
```

### 主要配置项

```json
{
  "scan": {
    "root_path": "C:\\",
    "max_depth": 5,
    "safe_extensions": [".tmp", ".temp", ".log", ".bak"]
  },
  "clean": {
    "use_trash": true,
    "backup_before_delete": false,
    "confirm_before_delete": true
  },
  "monitor": {
    "interval": 60,
    "alert_threshold": 90
  },
  "recommendation": {
    "enabled": true,
    "frequency": "weekly"
  },
  "ui": {
    "theme": "light",
    "language": "zh-CN",
    "auto_refresh": true,
    "refresh_interval": 5000
  }
}
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

### 恢复文件

如果误删文件，可以从回收站恢复：

1. 打开回收站
2. 找到被删除的文件
3. 右键 → 还原

---

## ❓ 常见问题

### Q1：Python 未找到

**问题**：运行 `python --version` 提示 "python 不是内部或外部命令"

**解决**：
1. 重新安装 Python，勾选 "Add Python to PATH"
2. 或手动添加 Python 到 PATH：
   - 右键 "此电脑" → "属性" → "高级系统设置"
   - 点击 "环境变量"
   - 在 "系统变量" 中找到 "Path"，点击 "编辑"
   - 添加 Python 安装路径

### Q2：pip 安装失败

**问题**：运行 `pip install` 提示权限错误

**解决**：
```bash
# 使用 --user 选项
pip install --user -r requirements.txt

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3：PyQt6 安装失败

**问题**：安装 PyQt6 时出错

**解决**：
```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装 PyQt6
pip install PyQt6

# 如果仍然失败，尝试指定版本
pip install PyQt6==6.5.0
```

### Q4：程序无法启动

**问题**：双击启动脚本无反应

**解决**：
1. 以管理员身份运行
2. 检查 Python 是否正确安装
3. 检查依赖是否安装完整：
   ```bash
   pip install -r requirements.txt
   ```
4. 查看错误日志：
   ```bash
   python main.py 2>&1 | more
   ```

### Q5：杀毒软件误报

**问题**：杀毒软件拦截程序

**解决**：
1. 将 CleanBot 添加到杀毒软件白名单
2. 或暂时关闭杀毒软件
3. 这是因为程序访问系统文件，属于正常行为

### Q6：桌面机器人不显示

**问题**：运行 main_robot.py 后看不到机器人

**解决**：
1. 检查系统托盘是否有图标
2. 尝试按 Alt+Tab 切换窗口
3. 检查是否有错误提示
4. 确保已生成图片：
   ```bash
   python ui/robot/characters/conan/generate_images.py
   ```

### Q7：图片生成失败

**问题**：运行 generate_images.py 报错

**解决**：
```bash
# 安装 Pillow
pip install Pillow

# 重新运行
python ui/robot/characters/conan/generate_images.py
```

### Q8：扫描速度慢

**问题**：文件扫描时间过长

**解决**：
```bash
# 减少扫描深度
python main.py --scan --depth 3

# 只扫描特定目录
python main.py --scan --target "C:\Users"
```

### Q9：清理后空间未释放

**问题**：清理文件后磁盘空间没有明显变化

**解决**：
1. 清空回收站
2. 清理系统还原点
3. 重启电脑
4. 检查是否有其他程序占用空间

### Q10：程序崩溃

**问题**：程序运行中突然崩溃

**解决**：
1. 查看错误日志：
   ```
   %USERPROFILE%\CleanBot\logs\
   ```
2. 重启程序
3. 如果问题持续，提交 Issue

---

## 🛠️ 开发者指南

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

# 运行带覆盖率的测试
pytest --cov=core tests/
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

# 查看生成的图片
ls ui/robot/characters/conan/*.png
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

## 📁 目录结构

```
clean-bot-v2/
├── core/                        # 核心引擎
│   ├── diagnosis/              # 系统诊断
│   │   └── system_diagnosis.py
│   ├── scanner/                # 文件扫描
│   │   └── file_scanner.py
│   ├── cleaner/                # 文件清理
│   │   └── file_cleaner.py
│   ├── monitor/                # 磁盘监控
│   │   └── disk_monitor.py
│   ├── ai/                     # 智能推荐
│   │   └── recommendation.py
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
│           ├── conan/         # 柯南形象
│           ├── doraemon/      # 哆啦A梦
│           └── custom/        # 自定义
├── config/                      # 配置
│   └── settings.json
├── tests/                       # 测试
├── resources/                   # 资源
│   └── icons/                 # 图标
├── main.py                      # 主入口
├── main_robot.py                # 桌面机器人入口
├── requirements.txt             # 依赖
├── setup.py                     # 安装脚本
├── install.bat                  # 安装脚本
├── build.bat                    # 打包脚本
├── build_installer.bat          # 构建安装包
├── installer.nsi                # NSIS 脚本
├── INSTALL.md                   # 安装指南
├── QUICKSTART.md                # 快速开始
├── README.md                    # 文档
└── LICENSE                      # 许可证
```

---

## 🔄 更新

### 检查更新

```bash
# 进入项目目录
cd clean-bot-v2

# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt
```

### 手动更新

1. 下载最新版本
2. 替换旧版本文件
3. 重新安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

---

## 🗑️ 卸载

### 方式 1：使用卸载程序

如果使用安装包安装，可以通过 "控制面板" → "程序和功能" 卸载。

### 方式 2：手动卸载

1. 删除项目目录
2. 删除桌面快捷方式
3. 删除开始菜单快捷方式
4. （可选）删除用户数据：
   ```
   %USERPROFILE%\CleanBot\
   ```

---

## 📞 技术支持

- **GitHub Issues**：https://github.com/your-username/clean-bot-v2/issues
- **文档**：https://github.com/your-username/clean-bot-v2/wiki

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

## 🎉 开始使用

```bash
# 1. 下载项目
git clone https://github.com/your-username/clean-bot-v2.git

# 2. 进入目录
cd clean-bot-v2

# 3. 运行安装脚本
install.bat

# 4. 启动程序
start.bat
```

**祝你使用愉快！** 🎉
