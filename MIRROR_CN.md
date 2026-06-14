# CleanBot v2.0 — 国内镜像源配置指南

## 🇨🇳 国内用户专用

本指南帮助国内用户无需代理即可正常使用 CleanBot v2.0。

---

## 🚀 快速安装（推荐）

### 方式 1：使用快速安装脚本

```bash
# 下载项目
git clone https://github.com/5201314ty0609-collab/clean-bot-v2.git

# 进入目录
cd clean-bot-v2

# 运行国内快速安装脚本
quick_install_cn.bat
```

**脚本会自动：**
- ✅ 使用清华镜像源
- ✅ 安装所有依赖
- ✅ 生成机器人图片
- ✅ 创建启动脚本

### 方式 2：使用标准安装脚本

```bash
# 运行安装脚本（已配置国内镜像）
install.bat
```

---

## 🔧 手动配置国内镜像

### 方法 1：临时使用（每次安装时指定）

```bash
# 清华镜像（推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 豆瓣镜像
pip install -r requirements.txt -i https://pypi.douban.com/simple/

# 中科大镜像
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```

### 方法 2：永久配置（推荐）

#### Windows

**方法 A：使用 pip.ini 文件**

将 `pip.ini` 文件复制到以下目录：
```
%APPDATA%\pip\pip.ini
```

如果没有 `pip` 目录，手动创建：
```bash
mkdir %APPDATA%\pip
copy pip.ini %APPDATA%\pip\pip.ini
```

**方法 B：手动创建配置文件**

创建文件 `%APPDATA%\pip\pip.ini`，内容如下：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**方法 C：使用命令配置**

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

#### macOS/Linux

编辑文件 `~/.pip/pip.conf`：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

---

## 🪞 国内镜像源列表

| 镜像源 | 地址 | 速度 | 稳定性 |
|--------|------|------|--------|
| **清华镜像** | https://pypi.tuna.tsinghua.edu.cn/simple | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **阿里云镜像** | https://mirrors.aliyun.com/pypi/simple/ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **豆瓣镜像** | https://pypi.douban.com/simple/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **中科大镜像** | https://pypi.mirrors.ustc.edu.cn/simple/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **华为云镜像** | https://repo.huaweicloud.com/repository/pypi/simple/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐使用清华镜像或阿里云镜像，速度最快且最稳定。**

---

## 📦 依赖包说明

CleanBot v2.0 使用的所有依赖包均可在国内镜像源下载：

| 包名 | 用途 | 国内可用 |
|------|------|---------|
| PyQt6 | GUI 框架 | ✅ |
| psutil | 系统监控 | ✅ |
| pywin32 | Windows API | ✅ |
| send2trash | 安全删除 | ✅ |
| Pillow | 图像处理 | ✅ |
| matplotlib | 图表 | ✅ |
| rich | 终端美化 | ✅ |
| click | 命令行工具 | ✅ |

**所有依赖包均支持国内镜像源，无需代理即可安装！**

---

## 🔍 验证镜像配置

### 检查当前配置

```bash
pip config list
```

### 测试镜像源

```bash
# 测试清华镜像
pip install --dry-run psutil -i https://pypi.tuna.tsinghua.edu.cn/simple

# 测试阿里云镜像
pip install --dry-run psutil -i https://mirrors.aliyun.com/pypi/simple/
```

---

## ❓ 常见问题

### Q1：pip install 速度很慢

**解决：**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2：提示 "trusted-host" 警告

**解决：**
```bash
# 添加 --trusted-host 参数
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 或永久配置
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

### Q3：某些包安装失败

**解决：**
```bash
# 尝试其他镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或使用豆瓣镜像
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```

### Q4：提示 SSL 证书错误

**解决：**
```bash
# 添加 --trusted-host 参数
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 或升级 pip
python -m pip install --upgrade pip
```

### Q5：公司内网无法访问外网

**解决：**
1. 联系 IT 部门开通以下域名访问权限：
   - pypi.tuna.tsinghua.edu.cn
   - mirrors.aliyun.com
   - pypi.douban.com

2. 或使用公司内部镜像源（如果有的话）

3. 或在有网络的电脑上下载依赖包，然后复制到内网电脑

---

## 🛠️ 高级配置

### 使用多个镜像源

创建 `%APPDATA%\pip\pip.ini`：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
extra-index-url =
    https://mirrors.aliyun.com/pypi/simple/
    https://pypi.douban.com/simple/
trusted-host =
    pypi.tuna.tsinghua.edu.cn
    mirrors.aliyun.com
    pypi.douban.com

[install]
trusted-host =
    pypi.tuna.tsinghua.edu.cn
    mirrors.aliyun.com
    pypi.douban.com
```

### 使用代理（如果需要）

```bash
# HTTP 代理
pip install -r requirements.txt --proxy http://127.0.0.1:7890

# HTTPS 代理
pip install -r requirements.txt --proxy https://127.0.0.1:7890

# 或配置文件
[global]
proxy = http://127.0.0.1:7890
```

---

## 📞 技术支持

如果遇到问题，请：

1. 检查网络连接
2. 尝试其他镜像源
3. 查看错误日志
4. 提交 GitHub Issue

---

## ✅ 验证安装

安装完成后，运行以下命令验证：

```bash
# 检查 Python
python --version

# 检查 pip
pip --version

# 检查依赖
pip list

# 运行测试
python -c "import PyQt6; import psutil; print('所有依赖安装成功！')"
```

---

**CleanBot v2.0 支持国内镜像源，无需代理即可正常使用！** 🎉
