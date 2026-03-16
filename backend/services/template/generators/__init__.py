"""
模板生成器包
"""
from .base import TemplateGenerator
from .compare_number import CompareNumberGenerator
from .currency_conversion import CurrencyConversionGenerator
from .multiplication_table import MultiplicationTableGenerator
from .volume_conversion import VolumeConversionGenerator
from .fraction_comparison import FractionComparisonGenerator
from .mixed_addition_subtraction import MixedAdditionSubtractionGenerator
from .length_comparison import LengthComparisonGenerator
from .multiplication_division_comprehensive import MultiplicationDivisionComprehensiveGenerator


# 生成器注册表
# key: generator_module 值，value: 生成器类
GENERATOR_REGISTRY = {
    "compare_number": CompareNumberGenerator,
    "currency_conversion": CurrencyConversionGenerator,
    "multiplication_table": MultiplicationTableGenerator,
    "volume_conversion": VolumeConversionGenerator,
    "fraction_comparison": FractionComparisonGenerator,
    "mixed_addition_subtraction": MixedAdditionSubtractionGenerator,
    "length_comparison": LengthComparisonGenerator,
    "multiplication_division_comprehensive": MultiplicationDivisionComprehensiveGenerator,
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
