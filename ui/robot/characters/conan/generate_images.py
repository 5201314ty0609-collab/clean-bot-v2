"""
CleanBot v2.0 — 柯南形象图片生成器

生成卡通柯南的各个状态图片。
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_conan_image(expression: str, size: tuple = (200, 200)) -> Image.Image:
    """
    创建柯南图片

    Args:
        expression: 表情名称
        size: 图片尺寸

    Returns:
        PIL Image 对象
    """
    # 创建透明背景
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 基础颜色
    hair_color = (51, 51, 51)  # 黑色头发
    skin_color = (255, 224, 189)  # 肤色
    glass_color = (0, 0, 0)  # 眼镜框
    shirt_color = (0, 102, 204)  # 蓝色衬衫
    tie_color = (255, 0, 0)  # 红色领结

    # 绘制头部（圆形）
    head_center = (100, 80)
    head_radius = 50
    draw.ellipse(
        [head_center[0] - head_radius, head_center[1] - head_radius,
         head_center[0] + head_radius, head_center[1] + head_radius],
        fill=skin_color
    )

    # 绘制头发（黑色，遮住额头）
    hair_points = [
        (50, 70),  # 左侧
        (60, 30),  # 左上
        (100, 20),  # 顶部
        (140, 30),  # 右上
        (150, 70),  # 右侧
        (140, 60),  # 右侧内
        (100, 50),  # 顶部内
        (60, 60),  # 左侧内
    ]
    draw.polygon(hair_points, fill=hair_color)

    # 绘制眼镜框
    # 左眼镜
    draw.ellipse([70, 70, 95, 95], outline=glass_color, width=3)
    # 右眼镜
    draw.ellipse([105, 70, 130, 95], outline=glass_color, width=3)
    # 眼镜桥
    draw.line([95, 82, 105, 82], fill=glass_color, width=2)

    # 根据表情绘制眼睛和嘴巴
    if expression == "idle" or expression == "blink":
        # 普通眼睛
        draw.ellipse([77, 77, 88, 88], fill=(255, 255, 255))  # 左眼白
        draw.ellipse([112, 77, 123, 88], fill=(255, 255, 255))  # 右眼白
        draw.ellipse([80, 80, 85, 85], fill=(0, 0, 0))  # 左瞳孔
        draw.ellipse([115, 80, 120, 85], fill=(0, 0, 0))  # 右瞳孔

        if expression == "blink":
            # 眨眼：画一条线
            draw.line([77, 82, 88, 82], fill=(0, 0, 0), width=2)
            draw.line([112, 82, 123, 82], fill=(0, 0, 0), width=2)

        # 微笑嘴巴
        draw.arc([85, 95, 115, 110], 0, 180, fill=(0, 0, 0), width=2)

    elif expression == "happy":
        # 开心眼睛（弯弯的）
        draw.arc([77, 75, 88, 90], 0, 180, fill=(0, 0, 0), width=2)
        draw.arc([112, 75, 123, 90], 0, 180, fill=(0, 0, 0), width=2)

        # 大笑嘴巴
        draw.arc([80, 90, 120, 115], 0, 180, fill=(0, 0, 0), width=3)

        # 腮红
        draw.ellipse([65, 85, 75, 95], fill=(255, 150, 150, 128))
        draw.ellipse([125, 85, 135, 95], fill=(255, 150, 150, 128))

    elif expression == "thinking":
        # 思考眼睛（向上看）
        draw.ellipse([77, 77, 88, 88], fill=(255, 255, 255))
        draw.ellipse([112, 77, 123, 88], fill=(255, 255, 255))
        draw.ellipse([80, 78, 85, 83], fill=(0, 0, 0))  # 瞳孔向上
        draw.ellipse([115, 78, 120, 83], fill=(0, 0, 0))

        # 思考嘴巴
        draw.line([90, 100, 110, 100], fill=(0, 0, 0), width=2)

    elif expression == "working":
        # 工作眼睛（专注）
        draw.ellipse([77, 77, 88, 88], fill=(255, 255, 255))
        draw.ellipse([112, 77, 123, 88], fill=(255, 255, 255))
        draw.ellipse([80, 80, 85, 85], fill=(0, 0, 0))
        draw.ellipse([115, 80, 120, 85], fill=(0, 0, 0))

        # 专注嘴巴
        draw.line([90, 100, 110, 100], fill=(0, 0, 0), width=2)

        # 汗水
        draw.ellipse([140, 60, 145, 70], fill=(100, 180, 255, 200))

    elif expression == "sad":
        # 难过眼睛（向下的弧线）
        draw.arc([77, 80, 88, 95], 180, 360, fill=(0, 0, 0), width=2)
        draw.arc([112, 80, 123, 95], 180, 360, fill=(0, 0, 0), width=2)

        # 难过嘴巴
        draw.arc([85, 105, 115, 120], 180, 360, fill=(0, 0, 0), width=2)

        # 眼泪
        draw.ellipse([85, 95, 88, 100], fill=(100, 180, 255, 200))
        draw.ellipse([112, 95, 115, 100], fill=(100, 180, 255, 200))

    elif expression == "surprised":
        # 惊讶眼睛（大大的）
        draw.ellipse([75, 75, 90, 90], fill=(255, 255, 255))
        draw.ellipse([110, 75, 125, 90], fill=(255, 255, 255))
        draw.ellipse([80, 80, 85, 85], fill=(0, 0, 0))
        draw.ellipse([115, 80, 120, 85], fill=(0, 0, 0))

        # 惊讶嘴巴（圆形）
        draw.ellipse([90, 100, 110, 115], outline=(0, 0, 0), width=2)

    elif expression == "angry":
        # 生气眼睛（向下的眉毛）
        draw.ellipse([77, 77, 88, 88], fill=(255, 255, 255))
        draw.ellipse([112, 77, 123, 88], fill=(255, 255, 255))
        draw.ellipse([80, 80, 85, 85], fill=(0, 0, 0))
        draw.ellipse([115, 80, 120, 85], fill=(0, 0, 0))

        # 生气眉毛
        draw.line([75, 75, 90, 70], fill=(0, 0, 0), width=2)
        draw.line([110, 70, 125, 75], fill=(0, 0, 0), width=2)

        # 生气嘴巴
        draw.arc([85, 105, 115, 120], 180, 360, fill=(0, 0, 0), width=2)

    else:
        # 默认表情
        draw.ellipse([77, 77, 88, 88], fill=(255, 255, 255))
        draw.ellipse([112, 77, 123, 88], fill=(255, 255, 255))
        draw.ellipse([80, 80, 85, 85], fill=(0, 0, 0))
        draw.ellipse([115, 80, 120, 85], fill=(0, 0, 0))
        draw.arc([85, 95, 115, 110], 0, 180, fill=(0, 0, 0), width=2)

    # 绘制身体（蓝色衬衫）
    body_points = [
        (70, 130),  # 左肩
        (100, 125),  # 领口
        (130, 130),  # 右肩
        (140, 180),  # 右下
        (60, 180),  # 左下
    ]
    draw.polygon(body_points, fill=shirt_color)

    # 绘制领结
    tie_points = [
        (95, 125),  # 左
        (100, 120),  # 上
        (105, 125),  # 右
        (100, 135),  # 下
    ]
    draw.polygon(tie_points, fill=tie_color)

    return img


def generate_all_images():
    """生成所有表情图片"""
    output_dir = os.path.dirname(os.path.abspath(__file__))

    expressions = [
        "idle", "happy", "thinking", "working", "sad",
        "surprised", "angry", "confused", "proud", "shy",
        "sleepy", "excited", "blink_1", "blink_2",
        "look_left", "look_right", "look_center",
        "wave_1", "wave_2", "bounce_1", "bounce_2", "bounce_3",
        "walk_1", "walk_2", "walk_3", "walk_4",
        "run_1", "run_2", "run_3", "run_4",
    ]

    for expression in expressions:
        img = create_conan_image(expression)
        output_path = os.path.join(output_dir, f"{expression}.png")
        img.save(output_path)
        print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate_all_images()
