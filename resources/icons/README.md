# CleanBot 图标说明

## 需要的图标文件

- `cleanbot.ico` — Windows 图标文件（256x256, 128x128, 64x64, 48x48, 32x32, 16x16）

## 创建图标

### 方式 1：使用在线工具

1. 访问 https://convertico.com/
2. 上传 PNG 图片（建议 256x256）
3. 下载 ICO 文件
4. 重命名为 `cleanbot.ico`

### 方式 2：使用 Python

```python
from PIL import Image

# 打开 PNG 图片
img = Image.open('cleanbot.png')

# 保存为 ICO
img.save('cleanbot.ico', format='ICO', sizes=[
    (256, 256),
    (128, 128),
    (64, 64),
    (48, 48),
    (32, 32),
    (16, 16),
])
```

### 方式 3：使用 GIMP

1. 打开 GIMP
2. 导入 PNG 图片
3. 文件 → 导出为
4. 选择 ICO 格式
5. 保存

## 图标设计建议

- 使用简洁的图标设计
- 主题：清理、优化、机器人
- 颜色：蓝色 (#2196F3) 或绿色 (#4CAF50)
- 避免过于复杂的细节

## 示例图标

可以使用以下免费图标资源：
- https://www.flaticon.com/
- https://icons8.com/
- https://www.iconfinder.com/

搜索关键词：clean, robot, optimize, disk
