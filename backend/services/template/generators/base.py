"""
模板生成器接口定义
所有模板生成器必须实现此接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class TemplateGenerator(ABC):
    """模板生成器抽象基类"""

    @abstractmethod
    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        """
        生成题目

        Args:
            template_config: 模板配置（从 variables_config 解析）
            quantity: 生成数量
            question_type: 题目类型（从模板 question_type 字段传入）

        Returns:
            题目列表，每项包含：type, stem, knowledge_points, rows_to_answer
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
