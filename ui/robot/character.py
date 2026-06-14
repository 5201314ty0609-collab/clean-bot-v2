"""
CleanBot v2.0 — 角色管理系统

管理不同角色的加载、切换、资源。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CharacterConfig:
    """角色配置"""
    id: str
    name: str
    description: str
    size: Dict[str, int]
    colors: Dict[str, str]
    expressions: Dict[str, str]
    animations: Dict[str, str]
    images: Dict[str, str]
    sounds: Dict[str, str] = field(default_factory=dict)


class Character:
    """角色类"""

    def __init__(self, config_path: str):
        """
        初始化角色

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config_dir = os.path.dirname(config_path)
        self.config = self._load_config()
        self.resources = {}

    def _load_config(self) -> CharacterConfig:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CharacterConfig(**data)
        except Exception as e:
            print(f"加载角色配置失败: {e}")
            return None

    def get_id(self) -> str:
        """获取角色ID"""
        return self.config.id if self.config else ""

    def get_name(self) -> str:
        """获取角色名称"""
        return self.config.name if self.config else ""

    def get_description(self) -> str:
        """获取角色描述"""
        return self.config.description if self.config else ""

    def get_size(self) -> Tuple[int, int]:
        """获取角色尺寸"""
        if self.config:
            return (self.config.size.get("width", 200), self.config.size.get("height", 200))
        return (200, 200)

    def get_colors(self) -> Dict[str, str]:
        """获取角色颜色"""
        return self.config.colors if self.config else {}

    def get_expression_image(self, expression: str) -> Optional[str]:
        """
        获取表情图片路径

        Args:
            expression: 表情名称

        Returns:
            图片路径
        """
        if not self.config:
            return None

        # 从配置中获取图片文件名
        image_file = self.config.images.get(expression)
        if image_file:
            image_path = os.path.join(self.config_dir, image_file)
            if os.path.exists(image_path):
                return image_path

        # 返回默认图片
        return self.get_default_image()

    def get_default_image(self) -> Optional[str]:
        """获取默认图片路径"""
        if not self.config:
            return None

        # 优先使用 idle 图片
        image_file = self.config.images.get("idle")
        if image_file:
            image_path = os.path.join(self.config_dir, image_file)
            if os.path.exists(image_path):
                return image_path

        # 返回第一个可用图片
        for image_file in self.config.images.values():
            image_path = os.path.join(self.config_dir, image_file)
            if os.path.exists(image_path):
                return image_path

        return None

    def get_animation_frame(self, frame_name: str) -> Optional[str]:
        """
        获取动画帧图片路径

        Args:
            frame_name: 帧名称

        Returns:
            图片路径
        """
        if not self.config:
            return None

        # 从配置中获取动画帧
        animation_file = self.config.animations.get(frame_name)
        if animation_file:
            animation_path = os.path.join(self.config_dir, animation_file)
            if os.path.exists(animation_path):
                return animation_path

        return None

    def get_sound(self, sound_name: str) -> Optional[str]:
        """
        获取音效文件路径

        Args:
            sound_name: 音效名称

        Returns:
            音效文件路径
        """
        if not self.config:
            return None

        sound_file = self.config.sounds.get(sound_name)
        if sound_file:
            sound_path = os.path.join(self.config_dir, sound_file)
            if os.path.exists(sound_path):
                return sound_path

        return None


class CharacterManager:
    """角色管理器"""

    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.current_character: Optional[Character] = None
        self.characters_dir = os.path.join(os.path.dirname(__file__), "characters")

        # 加载所有角色
        self._load_characters()

    def _load_characters(self):
        """加载所有角色"""
        if not os.path.exists(self.characters_dir):
            os.makedirs(self.characters_dir, exist_ok=True)
            return

        # 遍历角色目录
        for character_name in os.listdir(self.characters_dir):
            character_dir = os.path.join(self.characters_dir, character_name)

            if os.path.isdir(character_dir):
                config_path = os.path.join(character_dir, "config.json")

                if os.path.exists(config_path):
                    try:
                        character = Character(config_path)
                        if character.get_id():
                            self.characters[character.get_id()] = character
                    except Exception as e:
                        print(f"加载角色 {character_name} 失败: {e}")

    def get_character_list(self) -> List[str]:
        """获取所有角色ID列表"""
        return list(self.characters.keys())

    def get_character_names(self) -> Dict[str, str]:
        """获取所有角色名称"""
        return {
            character_id: character.get_name()
            for character_id, character in self.characters.items()
        }

    def get_character(self, character_id: str) -> Optional[Character]:
        """
        获取角色

        Args:
            character_id: 角色ID

        Returns:
            角色对象
        """
        return self.characters.get(character_id)

    def get_current_character(self) -> Optional[Character]:
        """获取当前角色"""
        return self.current_character

    def switch_character(self, character_id: str) -> bool:
        """
        切换角色

        Args:
            character_id: 角色ID

        Returns:
            是否切换成功
        """
        if character_id in self.characters:
            self.current_character = self.characters[character_id]
            return True
        return False

    def add_character(self, character: Character) -> bool:
        """
        添加角色

        Args:
            character: 角色对象

        Returns:
            是否添加成功
        """
        character_id = character.get_id()
        if character_id:
            self.characters[character_id] = character
            return True
        return False

    def remove_character(self, character_id: str) -> bool:
        """
        移除角色

        Args:
            character_id: 角色ID

        Returns:
            是否移除成功
        """
        if character_id in self.characters:
            del self.characters[character_id]

            # 如果移除的是当前角色，切换到第一个可用角色
            if self.current_character and self.current_character.get_id() == character_id:
                if self.characters:
                    first_id = next(iter(self.characters))
                    self.switch_character(first_id)
                else:
                    self.current_character = None

            return True
        return False
