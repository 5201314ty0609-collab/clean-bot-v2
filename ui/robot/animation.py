"""
CleanBot v2.0 — 动画系统

管理角色的动画播放。
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class AnimationFrame:
    """动画帧"""
    image: str
    duration: float  # 秒
    offset_x: int = 0
    offset_y: int = 0


@dataclass
class Animation:
    """动画"""
    name: str
    frames: List[AnimationFrame]
    loop: bool = False
    speed: float = 1.0
    on_complete: Optional[Callable] = None


class AnimationSystem:
    """动画系统"""

    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.current_frame_index: int = 0
        self.last_frame_time: float = 0
        self.is_playing: bool = False
        self.is_paused: bool = False

        # 初始化默认动画
        self._init_default_animations()

    def _init_default_animations(self):
        """初始化默认动画"""
        # 眨眼动画
        self.animations["blink"] = Animation(
            name="blink",
            frames=[
                AnimationFrame(image="blink_1", duration=0.1),
                AnimationFrame(image="blink_2", duration=0.1),
                AnimationFrame(image="blink_1", duration=0.1),
            ],
            loop=False,
        )

        # 左右看动画
        self.animations["look_around"] = Animation(
            name="look_around",
            frames=[
                AnimationFrame(image="look_left", duration=0.5),
                AnimationFrame(image="look_center", duration=0.3),
                AnimationFrame(image="look_right", duration=0.5),
                AnimationFrame(image="look_center", duration=0.3),
            ],
            loop=False,
        )

        # 伸懒腰动画
        self.animations["stretch"] = Animation(
            name="stretch",
            frames=[
                AnimationFrame(image="stretch_1", duration=0.3),
                AnimationFrame(image="stretch_2", duration=0.5),
                AnimationFrame(image="stretch_1", duration=0.3),
                AnimationFrame(image="idle", duration=0.2),
            ],
            loop=False,
        )

        # 打哈欠动画
        self.animations["yawn"] = Animation(
            name="yawn",
            frames=[
                AnimationFrame(image="yawn_1", duration=0.3),
                AnimationFrame(image="yawn_2", duration=0.8),
                AnimationFrame(image="yawn_1", duration=0.3),
                AnimationFrame(image="idle", duration=0.2),
            ],
            loop=False,
        )

        # 挥手动画
        self.animations["wave"] = Animation(
            name="wave",
            frames=[
                AnimationFrame(image="wave_1", duration=0.2),
                AnimationFrame(image="wave_2", duration=0.2),
                AnimationFrame(image="wave_1", duration=0.2),
                AnimationFrame(image="wave_2", duration=0.2),
                AnimationFrame(image="wave_1", duration=0.2),
                AnimationFrame(image="idle", duration=0.2),
            ],
            loop=False,
        )

        # 跳跃动画
        self.animations["bounce"] = Animation(
            name="bounce",
            frames=[
                AnimationFrame(image="bounce_1", duration=0.15, offset_y=-10),
                AnimationFrame(image="bounce_2", duration=0.15, offset_y=-20),
                AnimationFrame(image="bounce_3", duration=0.15, offset_y=-10),
                AnimationFrame(image="idle", duration=0.1),
            ],
            loop=False,
        )

        # 行走动画
        self.animations["walk"] = Animation(
            name="walk",
            frames=[
                AnimationFrame(image="walk_1", duration=0.2),
                AnimationFrame(image="walk_2", duration=0.2),
                AnimationFrame(image="walk_3", duration=0.2),
                AnimationFrame(image="walk_4", duration=0.2),
            ],
            loop=True,
        )

        # 跑步动画
        self.animations["run"] = Animation(
            name="run",
            frames=[
                AnimationFrame(image="run_1", duration=0.1),
                AnimationFrame(image="run_2", duration=0.1),
                AnimationFrame(image="run_3", duration=0.1),
                AnimationFrame(image="run_4", duration=0.1),
            ],
            loop=True,
            speed=2.0,
        )

    def load_animation(self, name: str, animation: Animation):
        """
        加载动画

        Args:
            name: 动画名称
            animation: 动画对象
        """
        self.animations[name] = animation

    def play(self, name: str, loop: bool = False, speed: float = 1.0):
        """
        播放动画

        Args:
            name: 动画名称
            loop: 是否循环
            speed: 播放速度
        """
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.current_animation.loop = loop
            self.current_animation.speed = speed
            self.current_frame_index = 0
            self.last_frame_time = time.time()
            self.is_playing = True
            self.is_paused = False

    def stop(self):
        """停止动画"""
        self.is_playing = False
        self.current_animation = None
        self.current_frame_index = 0

    def pause(self):
        """暂停动画"""
        self.is_paused = True

    def resume(self):
        """恢复动画"""
        self.is_paused = False
        self.last_frame_time = time.time()

    def update(self) -> Optional[str]:
        """
        更新动画

        Returns:
            当前帧的图片名称，如果没有动画在播放则返回 None
        """
        if not self.is_playing or self.is_paused or not self.current_animation:
            return None

        current_time = time.time()
        elapsed = current_time - self.last_frame_time

        # 获取当前帧
        if self.current_frame_index < len(self.current_animation.frames):
            frame = self.current_animation.frames[self.current_frame_index]

            # 检查是否需要切换到下一帧
            frame_duration = frame.duration / self.current_animation.speed
            if elapsed >= frame_duration:
                self.current_frame_index += 1
                self.last_frame_time = current_time

                # 检查动画是否结束
                if self.current_frame_index >= len(self.current_animation.frames):
                    if self.current_animation.loop:
                        self.current_frame_index = 0
                    else:
                        self.is_playing = False
                        if self.current_animation.on_complete:
                            self.current_animation.on_complete()
                        return None

                # 返回当前帧
                if self.current_frame_index < len(self.current_animation.frames):
                    return self.current_animation.frames[self.current_frame_index].image
            else:
                # 返回当前帧
                return frame.image

        return None

    def get_current_frame(self) -> Optional[AnimationFrame]:
        """获取当前帧"""
        if self.current_animation and self.current_frame_index < len(self.current_animation.frames):
            return self.current_animation.frames[self.current_frame_index]
        return None

    def get_current_animation_name(self) -> Optional[str]:
        """获取当前动画名称"""
        return self.current_animation.name if self.current_animation else None

    def is_animation_playing(self, name: str) -> bool:
        """检查动画是否正在播放"""
        return (
            self.is_playing and
            self.current_animation and
            self.current_animation.name == name
        )

    def get_available_animations(self) -> List[str]:
        """获取所有可用动画"""
        return list(self.animations.keys())
