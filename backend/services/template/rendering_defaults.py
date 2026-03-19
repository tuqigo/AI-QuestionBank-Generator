"""
题目渲染默认配置管理模块

提供全局默认渲染配置和按题型的默认配置
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path


class RenderingDefaults:
    """渲染默认配置管理器"""

    _instance = None
    _defaults: Dict[str, Any] = {}
    _config_loaded: bool = False  # 标记配置是否已加载

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config_loaded:
            self._load_defaults()
            self._config_loaded = True

    def reload(self):
        """强制重新加载配置文件（用于开发环境）"""
        self._defaults = {}
        self._config_loaded = False
        self._load_defaults()

    def _load_defaults(self):
        """加载默认配置文件"""
        config_path = Path(__file__).parent / "rendering_defaults.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._defaults = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，使用内置默认值
            self._defaults = self._get_builtin_defaults()
        except json.JSONDecodeError:
            # JSON 解析失败，使用内置默认值
            self._defaults = self._get_builtin_defaults()

    def _get_builtin_defaults(self) -> Dict[str, Any]:
        """内置默认配置（配置文件不存在时的后备）"""
        return {
            "global": {
                "layout": "single",
                "font_size": 14,
                "latex_scale": 1.0,
                "rows_to_answer": 1,
                "keep_together": True
            },
            "by_question_type": {
                "ORAL_CALCULATION": {
                    "layout": "multi",
                    "columns": 3,
                    "font_size": 14,
                    "answer_width": 80
                },
                "FILL_BLANK": {
                    "layout": "single",
                    "font_size": 14,
                    "answer_width": 150
                },
                "CALCULATION": {
                    "layout": "single",
                    "font_size": 14,
                    "rows_to_answer": 3
                },
                "WORD_PROBLEM": {
                    "layout": "single",
                    "font_size": 14,
                    "rows_to_answer": 5
                },
                "VERTICAL_ARITHMETIC": {
                    "layout": "single",
                    "font_size": 16,
                    "latex_scale": 1.2,
                    "keep_together": False
                },
                "READ_COMP": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "SINGLE_CHOICE": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "MULTIPLE_CHOICE": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "TRUE_FALSE": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "GEOMETRY": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "POETRY_APP": {
                    "layout": "single",
                    "font_size": 14,
                    "rows_to_answer": 2
                },
                "CLOZE": {
                    "layout": "single",
                    "font_size": 14,
                    "keep_together": True
                },
                "ESSAY": {
                    "layout": "single",
                    "font_size": 14,
                    "rows_to_answer": 10
                }
            }
        }

    def get_global_defaults(self) -> Dict[str, Any]:
        """获取全局默认配置"""
        return self._defaults.get("global", {})

    def get_question_type_defaults(self, question_type: str) -> Dict[str, Any]:
        """获取指定题型的默认配置

        Args:
            question_type: 题型（如 "ORAL_CALCULATION", "FILL_BLANK"）

        Returns:
            该题型的默认配置，如果不存在则返回全局默认配置
        """
        by_type = self._defaults.get("by_question_type", {})
        return by_type.get(question_type, self.get_global_defaults())

    def get_rendering_meta(
        self,
        question_type: str,
        template_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取渲染元数据

        优先级：模板配置 > 题型默认配置 > 全局默认配置

        Args:
            question_type: 题型
            template_config: 模板配置（可选），包含 rendering_config 字段

        Returns:
            合并后的渲染元数据
        """
        # 1. 获取全局默认配置
        rendering_meta = self.get_global_defaults().copy()

        # 2. 应用题型默认配置
        type_defaults = self.get_question_type_defaults(question_type)
        rendering_meta.update(type_defaults)

        # 3. 应用模板配置（如果有）
        if template_config:
            template_rendering = template_config.get("rendering_config", {})
            if template_rendering:
                rendering_meta.update(template_rendering)

        return rendering_meta


# 单例实例
_rendering_defaults = None


def get_rendering_defaults() -> RenderingDefaults:
    """获取渲染默认配置单例实例"""
    global _rendering_defaults
    if _rendering_defaults is None:
        _rendering_defaults = RenderingDefaults()
    return _rendering_defaults
