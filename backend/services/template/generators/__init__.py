"""
模板生成器包
"""
from .base import TemplateGenerator
from .fraction_arithmetic_comparison import FractionArithmeticComparisonGenerator
from .mixed_addition_subtraction import MixedAdditionSubtractionGenerator
from .multiplication_division_comprehensive import MultiplicationDivisionComprehensiveGenerator
from .vertical_addition_subtraction import VerticalAdditionSubtractionGenerator
from .decimal_arithmetic import DecimalArithmeticGenerator
from .unit_conversion_comprehensive import UnitConversionComprehensiveGenerator


# 生成器注册表
# key: generator_module 值，value: 生成器类
GENERATOR_REGISTRY = {
    "fraction_arithmetic_comparison": FractionArithmeticComparisonGenerator,
    "mixed_addition_subtraction": MixedAdditionSubtractionGenerator,
    "multiplication_division_comprehensive": MultiplicationDivisionComprehensiveGenerator,
    "vertical_addition_subtraction": VerticalAdditionSubtractionGenerator,
    "decimal_arithmetic": DecimalArithmeticGenerator,
    "unit_conversion_comprehensive": UnitConversionComprehensiveGenerator,
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
