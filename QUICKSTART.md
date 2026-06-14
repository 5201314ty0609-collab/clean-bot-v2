# CleanBot v2.0 — 快速开始指南

## 🚀 5 分钟快速上手

### 步骤 1：下载项目

```bash
# 方式 1：使用 git
git clone https://github.com/your-username/clean-bot-v2.git

# 方式 2：下载 ZIP
# 访问 GitHub 页面，点击 "Code" → "Download ZIP"
```

### 步骤 2：安装依赖

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

### 步骤 3：生成机器人图片

```bash
# 生成柯南形象图片
python ui/robot/characters/conan/generate_images.py
```

### 步骤 4：启动程序

```bash
# 启动桌面机器人（柯南形象）
python main_robot.py

# 或启动主界面
python main.py
```

---

## 🤖 桌面机器人使用

### 启动机器人

```bash
# 默认柯南形象
python main_robot.py

# 指定角色
python main_robot.py --character conan

# 打开形象选择器
python main_robot.py --selector
```

### 交互操作

| 操作 | 效果 |
|------|------|
| **单击** | 触发点击事件 |
| **双击** | 打开主界面 |
| **右键** | 显示菜单 |
| **拖拽** | 移动位置 |

### 右键菜单

- **切换角色**：选择不同形象
- **设置状态**：空闲、思考、工作、开心、难过
- **测试对话**：显示对话气泡
- **退出**：关闭程序

### 系统托盘

- **显示/隐藏**：控制机器人显示
- **切换角色**：快速切换形象
- **选择形象**：打开形象选择器
- **退出**：关闭程序

---

## 🖥️ 主界面使用

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

### 常用命令

```bash
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

### 交互式 CLI

```bash
python main.py --cli

CleanBot> diagnosis
CleanBot> scan
CleanBot> clean
CleanBot> monitor
CleanBot> recommend
CleanBot> exit
```

---

## 🎨 形象系统

### 内置形象

| 形象 | 描述 | 启动命令 |
|------|------|---------|
| 🕵️ **柯南** | 名侦探柯南 | `python main_robot.py --character conan` |
| 🤖 **哆啦A梦** | 哆啦A梦 | `python main_robot.py --character doraemon` |
| 🎨 **自定义** | 用户自定义 | `python main_robot.py --character custom` |

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

---

## 🔍 系统诊断

### 运行诊断

```bash
python main.py --diagnosis
```

### 输出示例

```
系统健康分数: 85/100

发现的问题:
  1. [HIGH] CPU 使用率过高
  2. [MEDIUM] 磁盘 C: 使用率 85%

推荐:
  - 关闭占用 CPU 较高的程序
  - 清理磁盘空间
```

### 诊断内容

- ✅ 系统文件完整性
- ✅ Windows 更新状态
- ✅ 系统还原点
- ✅ Windows Defender 状态
- ✅ 防火墙状态
- ✅ UAC 状态
- ✅ 磁盘健康检查
- ✅ 磁盘碎片检查
- ✅ 注册表问题
- ✅ 服务状态
- ✅ 启动项检查

---

## 🧹 文件清理

### 扫描文件

```bash
python main.py --scan
```

### 输出示例

```
扫描完成!

总文件数: 125,432
总大小: 45.2 GB

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

### 清理文件

```bash
python main.py --clean
```

### 清理流程

1. 扫描文件
2. 显示可清理文件
3. 用户确认
4. 移到回收站
5. 显示结果

---

## 📊 磁盘监控

### 启动监控

```bash
python main.py --monitor
```

### 输出示例

```
磁盘使用情况:
  C:\: 256.0 GB / 512.0 GB (50.0%)

使用趋势:
  C:\: ↑ 0.5 GB/天

⚠️ 告警:
  🟡 磁盘 C: 空间不足 (85%)
```

### 监控内容

- ✅ 磁盘使用率
- ✅ 使用趋势
- ✅ 预测磁盘满时间
- ✅ 自动告警

---

## 💡 智能推荐

### 获取推荐

```bash
python main.py --recommend
```

### 输出示例

```
生成了 5 个推荐:

1. 🔴 清理磁盘 C:
   磁盘 C: 使用率 85%，建议清理空间
   类别: cleanup
   优先级: 8/10
   预计节省: 5.00 GB

2. 🟡 清理 Chrome 缓存
   Chrome 缓存占用 500.00 MB
   类别: cleanup
   优先级: 6/10
   预计节省: 500.00 MB
```

### 推荐类型

- **基于系统状态**：磁盘空间、内存、CPU
- **基于使用习惯**：常用应用、不常用应用缓存
- **基于历史数据**：上次清理时间
- **基于时间**：月初、周一清理提醒

---

## ⚙️ 配置设置

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

## 🔒 安全说明

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

**解决**：
```bash
# 检查 Python
python --version

# 如果没有，下载安装
# https://www.python.org/downloads/
# 安装时勾选 "Add Python to PATH"
```

### Q2：pip 安装失败

**解决**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3：程序无法启动

**解决**：
```bash
# 以管理员身份运行
# 或检查依赖
pip install -r requirements.txt
```

### Q4：桌面机器人不显示

**解决**：
```bash
# 生成图片
python ui/robot/characters/conan/generate_images.py

# 重新启动
python main_robot.py
```

### Q5：杀毒软件误报

**解决**：
1. 将 CleanBot 添加到白名单
2. 或暂时关闭杀毒软件

---

## 📚 更多资源

- **完整文档**：README.md
- **安装指南**：INSTALL.md
- **问题反馈**：GitHub Issues

---

## 🎉 开始使用

```bash
# 1. 下载项目
git clone https://github.com/your-username/clean-bot-v2.git

# 2. 进入目录
cd clean-bot-v2

# 3. 安装依赖
pip install -r requirements.txt

# 4. 生成图片
python ui/robot/characters/conan/generate_images.py

# 5. 启动程序
python main_robot.py
```

**祝你使用愉快！** 🎉
