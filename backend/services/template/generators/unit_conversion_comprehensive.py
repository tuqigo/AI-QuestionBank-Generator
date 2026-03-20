"""
模板：小学单位换算综合生成器

支持小学阶段所有单位换算类型，按年级分类：
- 一年级：人民币单位（元、角、分）、长度单位初步（厘米、米）
- 二年级：长度单位拓展（分米、毫米）、时间单位（时、分、秒）
- 三年级：长度单位完整体系（千米）、质量单位（克、千克）、时间单位（年、月、日）
- 四年级：面积单位（平方厘米、平方分米、平方米）、质量单位拓展（吨）
- 五年级：面积单位拓展（公顷、平方千米）、体积/容积单位
- 六年级：复合单位（速度单位等）、综合应用

核心设计理念：
1. 统一的换算率配置系统
2. 支持单单位换算和复名数换算
3. 支持正向和逆向换算
4. 智能生成符合年级难度的题目
"""
import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from .base import TemplateGenerator


@dataclass
class UnitDefinition:
    """单位定义"""
    name: str  # 中文名称
    symbol: str  # 符号（可选）
    ratio: float  # 相对于基本单位的换算率


class UnitConversionComprehensiveGenerator(TemplateGenerator):
    """
    小学单位换算综合生成器

    配置示例（一年级人民币）:
    {
        "unit_category": "currency",
        "grade_level": "grade1",
        "convert_types": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"],
        "value_range": {"min": 1, "max": 50}
    }

    配置示例（三年级长度）:
    {
        "unit_category": "length",
        "grade_level": "grade3",
        "convert_types": ["m_to_km", "km_to_m", "m_cm_to_cm"],
        "value_range": {"min": 1, "max": 100}
    }

    配置示例（五年级体积）:
    {
        "unit_category": "volume",
        "grade_level": "grade5",
        "convert_types": ["m3_to_dm3", "l_to_ml", "dm3_to_l"],
        "value_range": {"min": 1, "max": 100}
    }
    """

    # ==================== 单位换算率定义 ====================
    # 格式：{类别：{单位名称：(符号，换算率，基本单位)}}

    UNIT_DEFINITIONS = {
        # 人民币单位（进率：10）
        "currency": {
            "yuan": ("元", "元", 100),      # 基本单位：分，1 元 = 100 分
            "jiao": ("角", "角", 10),        # 1 角 = 10 分
            "fen": ("分", "分", 1),          # 1 分 = 1 分
        },

        # 长度单位
        "length": {
            "km": ("千米", "km", 100000),    # 基本单位：厘米，1 千米 = 100000 厘米
            "m": ("米", "m", 100),           # 1 米 = 100 厘米
            "dm": ("分米", "dm", 10),        # 1 分米 = 10 厘米
            "cm": ("厘米", "cm", 1),         # 基本单位
            "mm": ("毫米", "mm", 0.1),       # 1 毫米 = 0.1 厘米
        },

        # 质量单位
        "mass": {
            "t": ("吨", "t", 1000000),       # 基本单位：克，1 吨 = 1000000 克
            "kg": ("千克", "kg", 1000),      # 1 千克 = 1000 克
            "g": ("克", "g", 1),             # 基本单位
        },

        # 面积单位
        "area": {
            "km2": ("平方千米", "km²", 10000000000),  # 基本单位：平方厘米
            "hectare": ("公顷", "hm²", 100000000),     # 1 公顷 = 100000000 平方厘米
            "m2": ("平方米", "m²", 10000),             # 1 平方米 = 10000 平方厘米
            "dm2": ("平方分米", "dm²", 100),           # 1 平方分米 = 100 平方厘米
            "cm2": ("平方厘米", "cm²", 1),             # 基本单位
        },

        # 体积/容积单位
        "volume": {
            "m3": ("立方米", "m³", 1000000),   # 基本单位：立方厘米
            "dm3": ("立方分米", "dm³", 1000),  # 1 立方分米 = 1000 立方厘米
            "cm3": ("立方厘米", "cm³", 1),     # 基本单位
            "l": ("升", "L", 1000),            # 1 升 = 1000 毫升
            "ml": ("毫升", "mL", 1),           # 基本单位
        },

        # 时间单位
        "time": {
            "century": ("世纪", "", 100),       # 基本单位：年
            "year": ("年", "", 1),             # 基本单位
            "month": ("月", "", 1/12),         # 1 月 = 1/12 年
            "week": ("周", "", 7/365),         # 1 周 ≈ 7/365 年
            "day": ("日", "", 1/365),          # 1 日 = 1/365 年
            "hour": ("时", "", 1/8760),        # 1 时 = 1/8760 年
            "minute": ("分", "", 1/525600),    # 1 分 = 1/525600 年
            "second": ("秒", "", 1/31536000),  # 1 秒 = 1/31536000 年
        },
    }

    # 简化时间单位换算（使用更直观的进率）
    TIME_CONVERSIONS = {
        # 秒为基础单位
        ("century", "year"): 100,
        ("year", "month"): 12,
        ("year", "day"): 365,
        ("year", "week"): 52,
        ("week", "day"): 7,
        ("day", "hour"): 24,
        ("hour", "minute"): 60,
        ("minute", "second"): 60,
        ("day", "minute"): 1440,
        ("hour", "second"): 3600,
        ("minute", "second"): 60,
    }

    # ==================== 换算类型模板 ====================
    # 定义各类换算类型的生成模板

    CONVERSION_TEMPLATES = {
        # 简单单向换算
        "simple": "{value}{from_unit} = [BLANK]{to_unit}",
        # 复名数转单名数
        "compound_to_simple": "{value1}{unit1}{value2}{unit2} = [BLANK]{to_unit}",
        # 单名数转复名数
        "simple_to_compound": "{value}{from_unit} = [BLANK]{unit1}[BLANK2]{unit2}",
        # 带符号的换算
        "with_symbol": "{value}{symbol} = [BLANK]{to_symbol}",
    }

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        unit_category = template_config.get("unit_category", "currency")
        grade_level = template_config.get("grade_level", "grade1")
        convert_types = template_config.get("convert_types", [])
        value_range = template_config.get("value_range", {"min": 1, "max": 50})
        allow_compound = template_config.get("allow_compound", True)  # 是否允许复名数
        integer_result = template_config.get("integer_result", True)  # 确保结果为整数

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 支持通过 q_type 设置 answer_style
        q_type_styles = template_config.get("q_type", {})
        if isinstance(q_type_styles, str):
            q_type_styles = {q_type_styles: "circle"}

        # 是否是比较大小题型
        is_comparison = template_config.get("is_comparison", False)

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择换算类型
                convert_type = random.choice(convert_types) if convert_types else self._get_default_convert_types(unit_category, grade_level)
                # 如果返回的是列表（默认类型），再随机选择一个
                if isinstance(convert_type, list):
                    convert_type = random.choice(convert_type)

                # 如果是比较大小题型
                if is_comparison:
                    stem, q_type = self._generate_comparison_question(
                        unit_category,
                        convert_type,
                        value_range
                    )
                else:
                    stem, q_type = self._generate_question(
                        unit_category,
                        convert_type,
                        value_range,
                        allow_compound,
                        integer_result
                    )

                if stem is None or stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 100 次尝试后仍未生成有效题目，跳过
                continue

            # 应用 q_type 级别的 answer_style 配置
            question_rendering_meta = rendering_meta.copy()
            if q_type in q_type_styles:
                question_rendering_meta["answer_style"] = q_type_styles[q_type]

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config, unit_category, convert_type),
                "rows_to_answer": 1,
                "rendering_meta": question_rendering_meta,
            })

        return questions

    def _get_default_convert_types(self, unit_category: str, grade_level: str) -> List[str]:
        """根据单位类别和年级返回默认的换算类型"""
        defaults = {
            "currency": {
                "grade1": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"],
                "grade2": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao", "yuan_fen_to_fen"],
                "grade3": ["yuan_to_fen", "jiao_to_yuan", "fen_to_jiao", "yuan_jiao_fen_to_fen"],
            },
            "length": {
                "grade1": ["m_to_cm", "cm_to_m"],
                "grade2": ["dm_to_cm", "cm_to_dm", "m_to_dm", "dm_to_m"],
                "grade3": ["km_to_m", "m_to_km", "m_cm_to_cm"],
                "grade4": ["m_to_cm", "cm_to_m", "dm_to_mm", "mm_to_cm"],
            },
            "mass": {
                "grade3": ["kg_to_g", "g_to_kg"],
                "grade4": ["t_to_kg", "kg_to_t", "kg_g_to_g"],
            },
            "area": {
                "grade4": ["m2_to_dm2", "dm2_to_cm2", "dm2_to_m2"],
                "grade5": ["hectare_to_m2", "km2_to_hectare", "m2_to_hectare"],
            },
            "volume": {
                "grade5": ["m3_to_dm3", "dm3_to_cm3", "l_to_ml", "dm3_to_l"],
            },
            "time": {
                "grade2": ["hour_to_minute", "minute_to_second", "minute_to_hour"],
                "grade3": ["year_to_month", "day_to_hour", "week_to_day"],
                "grade5": ["day_to_minute", "hour_to_second", "year_to_day"],
            },
        }
        return defaults.get(unit_category, {}).get(grade_level, ["simple"])

    def _generate_question(
        self,
        unit_category: str,
        convert_type: str,
        value_range: dict,
        allow_compound: bool,
        integer_result: bool
    ) -> Tuple[str, str]:
        """生成单道题目，返回 (stem, q_type)"""

        value_min = value_range.get("min", 1)
        value_max = value_range.get("max", 50)

        # ==================== 人民币换算 ====================
        if unit_category == "currency":
            return self._generate_currency_question(convert_type, value_min, value_max)

        # ==================== 长度换算 ====================
        elif unit_category == "length":
            return self._generate_length_question(convert_type, value_min, value_max)

        # ==================== 质量换算 ====================
        elif unit_category == "mass":
            return self._generate_mass_question(convert_type, value_min, value_max)

        # ==================== 面积换算 ====================
        elif unit_category == "area":
            return self._generate_area_question(convert_type, value_min, value_max)

        # ==================== 体积/容积换算 ====================
        elif unit_category == "volume":
            return self._generate_volume_question(convert_type, value_min, value_max)

        # ==================== 时间换算 ====================
        elif unit_category == "time":
            return self._generate_time_question(convert_type, value_min, value_max)

        # 默认返回
        return f"{random.randint(value_min, value_max)} 单位 = [BLANK] 单位", "simple"

    # ==================== 人民币换算 ====================
    def _generate_currency_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成人民币换算题目"""

        if convert_type == "yuan_to_jiao":
            value = random.randint(min_val, max_val)
            return f"{value}元 = [BLANK]角", "yuan_to_jiao"

        elif convert_type == "jiao_to_yuan":
            value = random.randint(1, max_val // 10) * 10
            return f"{value}角 = [BLANK]元", "jiao_to_yuan"

        elif convert_type == "jiao_to_fen":
            value = random.randint(min_val, max_val)
            return f"{value}角 = [BLANK]分", "jiao_to_fen"

        elif convert_type == "fen_to_jiao":
            value = random.randint(1, max_val // 10) * 10
            return f"{value}分 = [BLANK]角", "fen_to_jiao"

        elif convert_type == "yuan_to_fen":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}元 = [BLANK]分", "yuan_to_fen"

        elif convert_type == "fen_to_yuan":
            value = random.randint(1, max_val // 10) * 100
            return f"{value}分 = [BLANK]元", "fen_to_yuan"

        elif convert_type == "yuan_jiao_to_jiao":
            yuan = random.randint(min_val, max_val)
            jiao = random.randint(1, 9)
            return f"{yuan}元{jiao}角 = [BLANK]角", "compound"

        elif convert_type == "yuan_fen_to_fen":
            yuan = random.randint(min_val, max_val)
            fen = random.randint(10, 99)
            return f"{yuan}元{fen}分 = [BLANK]分", "compound"

        elif convert_type == "yuan_jiao_fen_to_fen":
            yuan = random.randint(min_val, max_val)
            jiao = random.randint(1, 9)
            fen = random.randint(10, 99)
            return f"{yuan}元{jiao}角{fen}分 = [BLANK]分", "compound"

        elif convert_type == "jiao_fen_to_fen":
            jiao = random.randint(1, 9)
            fen = random.randint(1, 9)
            return f"{jiao}角{fen}分 = [BLANK]分", "compound"

        # 默认
        return f"{random.randint(min_val, max_val)}元 = [BLANK]角", "yuan_to_jiao"

    # ==================== 长度换算 ====================
    def _generate_length_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成长度换算题目"""

        if convert_type == "m_to_cm":
            value = random.randint(min_val, max_val)
            return f"{value}m = [BLANK]cm", "m_to_cm"

        elif convert_type == "cm_to_m":
            value = random.randint(1, max_val // 100) * 100 if max_val >= 100 else 100
            return f"{value}cm = [BLANK]m", "cm_to_m"

        elif convert_type == "dm_to_cm":
            value = random.randint(min_val, max_val)
            return f"{value}dm = [BLANK]cm", "dm_to_cm"

        elif convert_type == "cm_to_dm":
            value = random.randint(1, max_val // 10) * 10
            return f"{value}cm = [BLANK]dm", "cm_to_dm"

        elif convert_type == "m_to_dm":
            value = random.randint(min_val, max_val)
            return f"{value}m = [BLANK]dm", "m_to_dm"

        elif convert_type == "dm_to_m":
            value = random.randint(1, max_val // 10) * 10
            return f"{value}dm = [BLANK]m", "dm_to_m"

        elif convert_type == "km_to_m":
            value = random.randint(min_val, min(max_val, 20))
            return f"{value}km = [BLANK]m", "km_to_m"

        elif convert_type == "m_to_km":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}m = [BLANK]km", "m_to_km"

        elif convert_type == "mm_to_cm":
            value = random.randint(1, max_val // 10) * 10
            return f"{value}mm = [BLANK]cm", "mm_to_cm"

        elif convert_type == "cm_to_mm":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}cm = [BLANK]mm", "cm_to_mm"

        elif convert_type == "dm_to_mm":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}dm = [BLANK]mm", "dm_to_mm"

        elif convert_type == "m_cm_to_cm":
            m = random.randint(min_val, max_val)
            cm = random.randint(1, 99)
            return f"{m}m{cm}cm = [BLANK]cm", "compound"

        elif convert_type == "m_dm_to_dm":
            m = random.randint(min_val, max_val)
            dm = random.randint(1, 9)
            return f"{m}m{dm}dm = [BLANK]dm", "compound"

        elif convert_type == "dm_cm_to_cm":
            dm = random.randint(1, 9)
            cm = random.randint(1, 9)
            return f"{dm}dm{cm}cm = [BLANK]cm", "compound"

        elif convert_type == "km_m_to_m":
            km = random.randint(1, 10)
            m = random.randint(1, 999)
            return f"{km}km{m}m = [BLANK]m", "compound"

        # 默认
        return f"{random.randint(min_val, max_val)}m = [BLANK]cm", "m_to_cm"

    # ==================== 质量换算 ====================
    def _generate_mass_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成质量换算题目"""

        if convert_type == "kg_to_g":
            value = random.randint(min_val, max_val)
            return f"{value}kg = [BLANK]g", "kg_to_g"

        elif convert_type == "g_to_kg":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}g = [BLANK]kg", "g_to_kg"

        elif convert_type == "t_to_kg":
            value = random.randint(min_val, min(max_val, 20))
            return f"{value}t = [BLANK]kg", "t_to_kg"

        elif convert_type == "kg_to_t":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}kg = [BLANK]t", "kg_to_t"

        elif convert_type == "kg_g_to_g":
            kg = random.randint(min_val, max_val)
            g = random.randint(100, 999)
            return f"{kg}kg{g}g = [BLANK]g", "compound"

        elif convert_type == "t_kg_to_kg":
            t = random.randint(1, 10)
            kg = random.randint(100, 999)
            return f"{t}t{kg}kg = [BLANK]kg", "compound"

        # 默认
        return f"{random.randint(min_val, max_val)}kg = [BLANK]g", "kg_to_g"

    # ==================== 面积换算 ====================
    def _generate_area_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成面积换算题目"""

        if convert_type == "m2_to_dm2":
            value = random.randint(min_val, max_val)
            return f"{value}m² = [BLANK]dm²", "m2_to_dm2"

        elif convert_type == "dm2_to_m2":
            value = random.randint(1, max_val // 100 + 1) * 100
            return f"{value}dm² = [BLANK]m²", "dm2_to_m2"

        elif convert_type == "dm2_to_cm2":
            value = random.randint(min_val, max_val)
            return f"{value}dm² = [BLANK]cm²", "dm2_to_cm2"

        elif convert_type == "cm2_to_dm2":
            value = random.randint(1, max_val // 100 + 1) * 100
            return f"{value}cm² = [BLANK]dm²", "cm2_to_dm2"

        elif convert_type == "hectare_to_m2":
            value = random.randint(min_val, min(max_val, 20))
            return f"{value}公顷 = [BLANK]m²", "hectare_to_m2"

        elif convert_type == "m2_to_hectare":
            value = random.randint(1, max_val // 10000 + 1) * 10000
            return f"{value}m² = [BLANK]公顷", "m2_to_hectare"

        elif convert_type == "km2_to_hectare":
            value = random.randint(1, min(max_val, 10))
            return f"{value}km² = [BLANK]公顷", "km2_to_hectare"

        elif convert_type == "hectare_to_km2":
            value = random.randint(10, max_val) * 100
            return f"{value}公顷 = [BLANK]km²", "hectare_to_km2"

        # 默认
        return f"{random.randint(min_val, max_val)}m² = [BLANK]dm²", "m2_to_dm2"

    # ==================== 体积/容积换算 ====================
    def _generate_volume_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成体积/容积换算题目"""

        if convert_type == "m3_to_dm3":
            value = random.randint(min_val, max_val)
            return f"{value}m³ = [BLANK]dm³", "m3_to_dm3"

        elif convert_type == "dm3_to_m3":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}dm³ = [BLANK]m³", "dm3_to_m3"

        elif convert_type == "dm3_to_cm3":
            value = random.randint(min_val, max_val)
            return f"{value}dm³ = [BLANK]cm³", "dm3_to_cm3"

        elif convert_type == "cm3_to_dm3":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}cm³ = [BLANK]dm³", "cm3_to_dm3"

        elif convert_type == "l_to_ml":
            value = random.randint(min_val, max_val)
            return f"{value}L = [BLANK]mL", "l_to_ml"

        elif convert_type == "ml_to_l":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}mL = [BLANK]L", "ml_to_l"

        elif convert_type == "dm3_to_l":
            value = random.randint(min_val, max_val)
            return f"{value}dm³ = [BLANK]L", "dm3_to_l"

        elif convert_type == "l_to_dm3":
            value = random.randint(min_val, max_val)
            return f"{value}L = [BLANK]dm³", "l_to_dm3"

        elif convert_type == "cm3_to_ml":
            value = random.randint(min_val, max_val)
            return f"{value}cm³ = [BLANK]mL", "cm3_to_ml"

        elif convert_type == "ml_to_cm3":
            value = random.randint(min_val, max_val)
            return f"{value}mL = [BLANK]cm³", "ml_to_cm3"

        elif convert_type == "m3_to_l":
            value = random.randint(min_val, max_val)
            return f"{value}m³ = [BLANK]L", "m3_to_l"

        elif convert_type == "l_to_m3":
            value = random.randint(1, max_val // 1000 + 1) * 1000
            return f"{value}L = [BLANK]m³", "l_to_m3"

        # 默认
        return f"{random.randint(min_val, max_val)}dm³ = [BLANK]cm³", "dm3_to_cm3"

    # ==================== 时间换算 ====================
    def _generate_time_question(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成时间换算题目"""

        if convert_type == "hour_to_minute":
            value = random.randint(min_val, max_val)
            return f"{value}时 = [BLANK]分", "hour_to_minute"

        elif convert_type == "minute_to_hour":
            value = random.randint(1, max_val // 60 + 1) * 60
            return f"{value}分 = [BLANK]时", "minute_to_hour"

        elif convert_type == "minute_to_second":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}分 = [BLANK]秒", "minute_to_second"

        elif convert_type == "second_to_minute":
            value = random.randint(1, max_val // 60 + 1) * 60
            return f"{value}秒 = [BLANK]分", "second_to_minute"

        elif convert_type == "day_to_hour":
            value = random.randint(min_val, max_val)
            return f"{value}日 = [BLANK]时", "day_to_hour"

        elif convert_type == "hour_to_day":
            value = random.randint(1, max_val // 24 + 1) * 24
            return f"{value}时 = [BLANK]日", "hour_to_day"

        elif convert_type == "year_to_month":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}年 = [BLANK]月", "year_to_month"

        elif convert_type == "month_to_year":
            value = random.randint(1, max_val // 12 + 1) * 12
            return f"{value}月 = [BLANK]年", "month_to_year"

        elif convert_type == "week_to_day":
            value = random.randint(min_val, min(max_val, 10))
            return f"{value}周 = [BLANK]天", "week_to_day"

        elif convert_type == "day_to_week":
            value = random.randint(1, max_val // 7 + 1) * 7
            return f"{value}天 = [BLANK]周", "day_to_week"

        elif convert_type == "day_to_minute":
            value = random.randint(min_val, min(max_val, 5))
            return f"{value}日 = [BLANK]分", "day_to_minute"

        elif convert_type == "hour_to_second":
            value = random.randint(min_val, min(max_val, 5))
            return f"{value}时 = [BLANK]秒", "hour_to_second"

        elif convert_type == "hour_minute_to_minute":
            hour = random.randint(1, 5)
            minute = random.randint(1, 59)
            return f"{hour}时{minute}分 = [BLANK]分", "compound"

        elif convert_type == "day_hour_to_hour":
            day = random.randint(1, 5)
            hour = random.randint(1, 23)
            return f"{day}日{hour}时 = [BLANK]时", "compound"

        elif convert_type == "year_month_to_month":
            year = random.randint(1, 5)
            month = random.randint(1, 11)
            return f"{year}年{month}月 = [BLANK]月", "compound"

        # 默认
        return f"{random.randint(min_val, max_val)}时 = [BLANK]分", "hour_to_minute"

    def get_knowledge_points(self, template_config: dict, unit_category: str = None, convert_type: str = None) -> List[str]:
        """
        根据配置和单位类别动态返回知识点
        """
        # 支持通过配置自定义知识点
        if "knowledge_points" in template_config:
            return template_config["knowledge_points"]

        # 根据单位类别返回对应的知识点
        knowledge_map = {
            "currency": [
                "认识人民币",
                "元角分的认识",
                "元角分换算",
                "人民币的简单计算",
            ],
            "length": [
                "长度单位的认识",
                "长度单位换算",
                "测量物体长度",
            ],
            "mass": [
                "质量单位的认识",
                "克与千克",
                "吨的认识",
                "质量单位换算",
            ],
            "area": [
                "面积单位的认识",
                "面积单位换算",
                "公顷和平方千米",
            ],
            "volume": [
                "体积单位的认识",
                "容积单位换算",
                "体积和容积",
            ],
            "time": [
                "时间单位的认识",
                "时、分、秒",
                "年、月、日",
                "时间单位换算",
            ],
        }

        base_points = knowledge_map.get(unit_category, ["单位换算"])

        # 根据换算类型添加细分知识点
        type_points = {
            # 人民币
            "yuan_to_jiao": "元化角",
            "jiao_to_yuan": "角化元",
            "jiao_to_fen": "角化分",
            "fen_to_jiao": "分化角",
            "yuan_to_fen": "元化分",
            "compound": "复名数换算",
            # 长度
            "m_to_cm": "米化厘米",
            "cm_to_m": "厘米化米",
            "km_to_m": "千米化米",
            "m_to_km": "米化千米",
            # 质量
            "kg_to_g": "千克化克",
            "g_to_kg": "克化千克",
            "t_to_kg": "吨化千克",
            # 面积
            "m2_to_dm2": "平方米化平方分米",
            "dm2_to_cm2": "平方分米化平方厘米",
            "hectare_to_m2": "公顷化平方米",
            # 体积
            "m3_to_dm3": "立方米化立方分米",
            "dm3_to_cm3": "立方分米化立方厘米",
            "l_to_ml": "升化毫升",
            "dm3_to_l": "立方分米化升",
            # 时间
            "hour_to_minute": "时化分",
            "minute_to_second": "分化秒",
            "year_to_month": "年化月",
            "day_to_hour": "日化时",
        }

        if convert_type and convert_type in type_points:
            base_points.append(type_points[convert_type])

        return base_points

    def _generate_comparison_question(
        self,
        unit_category: str,
        convert_type: str,
        value_range: dict
    ) -> Tuple[str, str]:
        """生成单位比较大小题目"""

        value_min = value_range.get("min", 1)
        value_max = value_range.get("max", 50)

        # ==================== 人民币比较 ====================
        if unit_category == "currency":
            return self._generate_currency_comparison(convert_type, value_min, value_max)

        # ==================== 长度比较 ====================
        elif unit_category == "length":
            return self._generate_length_comparison(convert_type, value_min, value_max)

        # ==================== 质量比较 ====================
        elif unit_category == "mass":
            return self._generate_mass_comparison(convert_type, value_min, value_max)

        # ==================== 面积比较 ====================
        elif unit_category == "area":
            return self._generate_area_comparison(convert_type, value_min, value_max)

        # ==================== 体积/容积比较 ====================
        elif unit_category == "volume":
            return self._generate_volume_comparison(convert_type, value_min, value_max)

        # ==================== 时间比较 ====================
        elif unit_category == "time":
            return self._generate_time_comparison(convert_type, value_min, value_max)

        # 默认返回
        return f"{random.randint(value_min, value_max)} 单位 [BLANK] {random.randint(value_min, value_max)} 单位", "compare"

    # ==================== 人民币比较 ====================
    def _generate_currency_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成人民币比较大小题目"""

        if convert_type == "yuan_to_jiao":
            yuan = random.randint(min_val, max_val)
            jiao = random.randint(min_val * 8, min_val * 12)  # 接近的值
            return f"{yuan}元 [BLANK] {jiao}角", "compare_yuan_jiao"

        elif convert_type == "jiao_to_fen":
            jiao = random.randint(min_val, max_val)
            fen = random.randint(jiao * 8, jiao * 12)
            return f"{jiao}角 [BLANK] {fen}分", "compare_jiao_fen"

        elif convert_type == "yuan_jiao_to_jiao":
            yuan1 = random.randint(min_val, max_val)
            jiao1 = random.randint(1, 9)
            total_jiao1 = yuan1 * 10 + jiao1
            jiao2 = random.randint(total_jiao1 - 10, total_jiao1 + 10)
            return f"{yuan1}元{jiao1}角 [BLANK] {jiao2}角", "compare_compound"

        # 默认：同单位比较
        yuan1 = random.randint(min_val, max_val)
        yuan2 = random.randint(min_val, max_val)
        while yuan1 == yuan2:
            yuan2 = random.randint(min_val, max_val)
        return f"{yuan1}元 [BLANK] {yuan2}元", "compare_simple"

    # ==================== 长度比较 ====================
    def _generate_length_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成长度比较大小题目"""

        if convert_type == "m_to_cm":
            m = random.randint(min_val, max_val)
            cm = random.randint(m * 80, m * 120)  # 接近 100 倍
            return f"{m}m [BLANK] {cm}cm", "compare_m_cm"

        elif convert_type == "km_to_m":
            km = random.randint(min_val, min(max_val, 20))
            m = random.randint(km * 800, km * 1200)  # 接近 1000 倍
            return f"{km}km [BLANK] {m}m", "compare_km_m"

        elif convert_type == "dm_to_cm":
            dm = random.randint(min_val, max_val)
            cm = random.randint(dm * 8, dm * 12)  # 接近 10 倍
            return f"{dm}dm [BLANK] {cm}cm", "compare_dm_cm"

        elif convert_type == "m_cm_to_cm":
            m = random.randint(1, 5)
            cm1 = random.randint(1, 50)
            total_cm1 = m * 100 + cm1
            cm2 = random.randint(total_cm1 - 50, total_cm1 + 50)
            return f"{m}m{cm1}cm [BLANK] {cm2}cm", "compare_compound"

        # 默认：同单位比较
        v1 = random.randint(min_val, max_val)
        v2 = random.randint(min_val, max_val)
        while v1 == v2:
            v2 = random.randint(min_val, max_val)
        return f"{v1}m [BLANK] {v2}m", "compare_simple"

    # ==================== 质量比较 ====================
    def _generate_mass_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成质量比较大小题目"""

        if convert_type == "kg_to_g":
            kg = random.randint(min_val, max_val)
            g = random.randint(kg * 800, kg * 1200)  # 接近 1000 倍
            return f"{kg}kg [BLANK] {g}g", "compare_kg_g"

        elif convert_type == "t_to_kg":
            t = random.randint(min_val, min(max_val, 20))
            kg = random.randint(t * 800, t * 1200)  # 接近 1000 倍
            return f"{t}t [BLANK] {kg}kg", "compare_t_kg"

        elif convert_type == "kg_g_to_g":
            kg = random.randint(1, 5)
            g1 = random.randint(100, 500)
            total_g1 = kg * 1000 + g1
            g2 = random.randint(total_g1 - 500, total_g1 + 500)
            return f"{kg}kg{g1}g [BLANK] {g2}g", "compare_compound"

        # 默认：同单位比较
        v1 = random.randint(min_val, max_val)
        v2 = random.randint(min_val, max_val)
        while v1 == v2:
            v2 = random.randint(min_val, max_val)
        return f"{v1}kg [BLANK] {v2}kg", "compare_simple"

    # ==================== 面积比较 ====================
    def _generate_area_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成面积比较大小题目"""

        if convert_type == "m2_to_dm2":
            m2 = random.randint(min_val, max_val)
            dm2 = random.randint(m2 * 80, m2 * 120)  # 接近 100 倍
            return f"{m2}m² [BLANK] {dm2}dm²", "compare_m2_dm2"

        elif convert_type == "hectare_to_m2":
            hectare = random.randint(min_val, min(max_val, 10))
            m2 = random.randint(hectare * 8000, hectare * 12000)  # 接近 10000 倍
            return f"{hectare}公顷 [BLANK] {m2}m²", "compare_hectare_m2"

        # 默认：同单位比较
        v1 = random.randint(min_val, max_val)
        v2 = random.randint(min_val, max_val)
        while v1 == v2:
            v2 = random.randint(min_val, max_val)
        return f"{v1}m² [BLANK] {v2}m²", "compare_simple"

    # ==================== 体积/容积比较 ====================
    def _generate_volume_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成体积/容积比较大小题目"""

        if convert_type == "m3_to_dm3":
            m3 = random.randint(min_val, max_val)
            dm3 = random.randint(m3 * 800, m3 * 1200)  # 接近 1000 倍
            return f"{m3}m³ [BLANK] {dm3}dm³", "compare_m3_dm3"

        elif convert_type == "l_to_ml":
            l = random.randint(min_val, max_val)
            ml = random.randint(l * 800, l * 1200)  # 接近 1000 倍
            return f"{l}L [BLANK] {ml}mL", "compare_l_ml"

        elif convert_type == "dm3_to_l":
            # 1:1 换算，生成接近值
            v1 = random.randint(min_val, max_val)
            v2 = random.randint(v1 - 5, v1 + 5)
            while v1 == v2:
                v2 = random.randint(v1 - 5, v1 + 5)
            return f"{v1}dm³ [BLANK] {v2}L", "compare_dm3_l"

        # 默认：同单位比较
        v1 = random.randint(min_val, max_val)
        v2 = random.randint(min_val, max_val)
        while v1 == v2:
            v2 = random.randint(min_val, max_val)
        return f"{v1}m³ [BLANK] {v2}m³", "compare_simple"

    # ==================== 时间比较 ====================
    def _generate_time_comparison(self, convert_type: str, min_val: int, max_val: int) -> Tuple[str, str]:
        """生成时间比较大小题目"""

        if convert_type == "hour_to_minute":
            hour = random.randint(min_val, min(max_val, 12))
            minute = random.randint(hour * 50, hour * 70)  # 接近 60 倍
            return f"{hour}时 [BLANK] {minute}分", "compare_hour_minute"

        elif convert_type == "minute_to_second":
            minute = random.randint(min_val, min(max_val, 10))
            second = random.randint(minute * 50, minute * 70)  # 接近 60 倍
            return f"{minute}分 [BLANK] {second}秒", "compare_minute_second"

        elif convert_type == "year_to_month":
            year = random.randint(min_val, min(max_val, 5))
            month = random.randint(year * 10, year * 14)  # 接近 12 倍
            return f"{year}年 [BLANK] {month}月", "compare_year_month"

        elif convert_type == "day_to_hour":
            day = random.randint(min_val, min(max_val, 10))
            hour = random.randint(day * 20, day * 28)  # 接近 24 倍
            return f"{day}日 [BLANK] {hour}时", "compare_day_hour"

        # 默认：同单位比较
        v1 = random.randint(min_val, max_val)
        v2 = random.randint(min_val, max_val)
        while v1 == v2:
            v2 = random.randint(min_val, max_val)
        return f"{v1}时 [BLANK] {v2}时", "compare_simple"
