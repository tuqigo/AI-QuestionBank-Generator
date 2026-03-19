"""
模板生成器接口定义
所有模板生成器必须实现此接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class TemplateGenerator(ABC):
    """模板生成器抽象基类"""

    def get_rendering_meta(
        self,
        question_type: str,
        template_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取渲染元数据

        优先级：模板配置 > 题型默认配置 > 全局默认配置

        Args:
            question_type: 题型（如 "ORAL_CALCULATION", "FILL_BLANK"）
            template_config: 模板配置（可选），包含 rendering_config 字段

        Returns:
            渲染元数据字典
        """
        from ..rendering_defaults import get_rendering_defaults
        defaults = get_rendering_defaults()
        return defaults.get_rendering_meta(question_type, template_config)

    @abstractmethod
    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        """
        生成题目

        Args:
            template_config: 模板配置（从 variables_config 解析）
            quantity: 生成数量
            question_type: 题目类型（从模板 question_type 字段传入）

        Returns:
            题目列表，每项包含：type, stem, knowledge_points, rows_to_answer, rendering_meta
        """
        pass

    @abstractmethod
    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """
        获取知识点列表

        Args:
            template_config: 模板配置

        Returns:
            知识点列表
        """
        pass
