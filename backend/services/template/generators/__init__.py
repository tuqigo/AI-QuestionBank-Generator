"""
模板生成器包
"""
from .base import TemplateGenerator
from .compare_number import CompareNumberGenerator
from .addition_subtraction import AdditionSubtractionGenerator
from .consecutive_addition_subtraction import ConsecutiveAdditionSubtractionGenerator
from .currency_conversion import CurrencyConversionGenerator


# 生成器注册表
# key: generator_module 值，value: 生成器类
GENERATOR_REGISTRY = {
    "compare_number": CompareNumberGenerator,
    "addition_subtraction": AdditionSubtractionGenerator,
    "consecutive_addition_subtraction": ConsecutiveAdditionSubtractionGenerator,
    "currency_conversion": CurrencyConversionGenerator,
}


def get_generator(generator_name: str) -> TemplateGenerator:
    """
    根据生成器名称获取生成器实例

    Args:
        generator_name: 生成器名称（对应 generator_module 字段）

    Returns:
        生成器实例

    Raises:
        ValueError: 生成器不存在
    """
    if generator_name not in GENERATOR_REGISTRY:
        raise ValueError(f"未知的生成器：{generator_name}")

    return GENERATOR_REGISTRY[generator_name]()
