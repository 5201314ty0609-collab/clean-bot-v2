"""
CleanBot v2.0 — 表情系统

管理角色的表情变化。
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Expression:
    """表情"""
    name: str
    eyes: str
    mouth: str
    eyebrows: str = "normal"
    blush: bool = False
    sweat: bool = False
    tears: bool = False


class ExpressionSystem:
    """表情系统"""

    def __init__(self):
        self.expressions: Dict[str, Expression] = {}
        self.current_expression: str = "idle"
        self.expression_intensity: float = 1.0  # 0.0-1.0

        # 初始化默认表情
        self._init_default_expressions()

    def _init_default_expressions(self):
        """初始化默认表情"""
        # 空闲表情
        self.expressions["idle"] = Expression(
            name="idle",
            eyes="normal",
            mouth="smile",
            eyebrows="normal",
        )

        # 眨眼表情
        self.expressions["blink"] = Expression(
            name="blink",
            eyes="closed",
            mouth="smile",
            eyebrows="normal",
        )

        # 思考表情
        self.expressions["thinking"] = Expression(
            name="thinking",
            eyes="looking_up",
            mouth="neutral",
            eyebrows="raised",
        )

        # 工作表情
        self.expressions["working"] = Expression(
            name="working",
            eyes="focused",
            mouth="neutral",
            eyebrows="normal",
            sweat=True,
        )

        # 开心表情
        self.expressions["happy"] = Expression(
            name="happy",
            eyes="happy",
            mouth="big_smile",
            eyebrows="raised",
            blush=True,
        )

        # 难过表情
        self.expressions["sad"] = Expression(
            name="sad",
            eyes="sad",
            mouth="frown",
            eyebrows="worried",
            tears=True,
        )

        # 惊讶表情
        self.expressions["surprised"] = Expression(
            name="surprised",
            eyes="wide",
            mouth="open",
            eyebrows="raised",
        )

        # 生气表情
        self.expressions["angry"] = Expression(
            name="angry",
            eyes="angry",
            mouth="frown",
            eyebrows="angry",
        )

        # 困惑表情
        self.expressions["confused"] = Expression(
            name="confused",
            eyes="confused",
            mouth="neutral",
            eyebrows="worried",
        )

        # 得意表情
        self.expressions["proud"] = Expression(
            name="proud",
            eyes="confident",
            mouth="smile",
            eyebrows="raised",
            blush=True,
        )

        # 害羞表情
        self.expressions["shy"] = Expression(
            name="shy",
            eyes="shy",
            mouth="smile",
            eyebrows="normal",
            blush=True,
        )

        # 困倦表情
        self.expressions["sleepy"] = Expression(
            name="sleepy",
            eyes="half_closed",
            mouth="neutral",
            eyebrows="normal",
        )

        # 兴奋表情
        self.expressions["excited"] = Expression(
            name="excited",
            eyes="sparkling",
            mouth="big_smile",
            eyebrows="raised",
            blush=True,
        )

    def get_expression(self, name: str) -> Optional[Expression]:
        """
        获取表情

        Args:
            name: 表情名称

        Returns:
            表情对象
        """
        return self.expressions.get(name)

    def get_current_expression(self) -> str:
        """获取当前表情名称"""
        return self.current_expression

    def get_current_expression_data(self) -> Optional[Expression]:
        """获取当前表情数据"""
        return self.expressions.get(self.current_expression)

    def set_expression(self, name: str, intensity: float = 1.0):
        """
        设置表情

        Args:
            name: 表情名称
            intensity: 表情强度 (0.0-1.0)
        """
        if name in self.expressions:
            self.current_expression = name
            self.expression_intensity = max(0.0, min(1.0, intensity))

    def set_expression_intensity(self, intensity: float):
        """
        设置表情强度

        Args:
            intensity: 表情强度 (0.0-1.0)
        """
        self.expression_intensity = max(0.0, min(1.0, intensity))

    def get_expression_intensity(self) -> float:
        """获取表情强度"""
        return self.expression_intensity

    def get_available_expressions(self) -> List[str]:
        """获取所有可用表情"""
        return list(self.expressions.keys())

    def get_expression_components(self, expression_name: str) -> Dict[str, str]:
        """
        获取表情组件

        Args:
            expression_name: 表情名称

        Returns:
            表情组件字典
        """
        expression = self.expressions.get(expression_name)
        if expression:
            return {
                "eyes": expression.eyes,
                "mouth": expression.mouth,
                "eyebrows": expression.eyebrows,
                "blush": str(expression.blush).lower(),
                "sweat": str(expression.sweat).lower(),
                "tears": str(expression.tears).lower(),
            }
        return {}

    def blend_expressions(self, expr1: str, expr2: str, factor: float) -> Dict[str, str]:
        """
        混合两个表情

        Args:
            expr1: 表情1名称
            expr2: 表情2名称
            factor: 混合因子 (0.0=expr1, 1.0=expr2)

        Returns:
            混合后的表情组件
        """
        expression1 = self.expressions.get(expr1)
        expression2 = self.expressions.get(expr2)

        if not expression1 or not expression2:
            return self.get_expression_components(expr1 or expr2 or "idle")

        # 简单的线性插值
        # 对于字符串类型的组件，使用 factor 决定使用哪个
        result = {}
        for component in ["eyes", "mouth", "eyebrows"]:
            value1 = getattr(expression1, component)
            value2 = getattr(expression2, component)

            if factor < 0.5:
                result[component] = value1
            else:
                result[component] = value2

        # 对于布尔类型的组件，使用 factor 决定
        for component in ["blush", "sweat", "tears"]:
            value1 = getattr(expression1, component)
            value2 = getattr(expression2, component)

            if factor < 0.5:
                result[component] = str(value1).lower()
            else:
                result[component] = str(value2).lower()

        return result

    def get_expression_for_state(self, state: str) -> str:
        """
        根据状态获取对应的表情

        Args:
            state: 状态名称

        Returns:
            表情名称
        """
        state_expression_map = {
            "idle": "idle",
            "thinking": "thinking",
            "working": "working",
            "happy": "happy",
            "sad": "sad",
            "surprised": "surprised",
            "angry": "angry",
            "confused": "confused",
            "proud": "proud",
            "shy": "shy",
            "sleepy": "sleepy",
            "excited": "excited",
        }

        return state_expression_map.get(state, "idle")

    def get_random_expression(self) -> str:
        """获取随机表情"""
        import random
        expressions = list(self.expressions.keys())
        # 排除当前表情
        if self.current_expression in expressions:
            expressions.remove(self.current_expression)
        return random.choice(expressions) if expressions else "idle"
