"""
JSON 校验工具
用于校验 AI 返回的题目 JSON 是否符合 Schema 规范
"""
import json
import os
from typing import Tuple, List, Optional
from jsonschema import validate, ValidationError

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "backend", "schemas", "question_schema.json")


def load_schema() -> dict:
    """加载 JSON Schema 文件"""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_question_json(json_str: str) -> Tuple[bool, Optional[dict], List[str]]:
    """
    校验 AI 返回的题目 JSON

    Args:
        json_str: AI 返回的 JSON 字符串

    Returns:
        (is_valid, parsed_data, errors)
        - is_valid: 是否校验通过
        - parsed_data: 解析后的数据（校验通过时）
        - errors: 错误信息列表
    """
    errors = []

    # 1. 尝试解析 JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return False, None, [f"JSON 解析失败: {str(e)}"]

    # 2. 加载 Schema
    try:
        schema = load_schema()
    except Exception as e:
        return False, None, [f"加载 Schema 失败: {str(e)}"]

    # 3. 校验数据
    try:
        validate(instance=data, schema=schema)
        return True, data, []
    except ValidationError as e:
        error_msg = f"字段 '{e.path[-1] if e.path else 'root'}': {e.message}"
        return False, None, [error_msg]
    except Exception as e:
        return False, None, [f"校验异常: {str(e)}"]


def validate_question_data(data: dict) -> Tuple[bool, List[str]]:
    """
    直接校验已解析的数据（不重新解析 JSON）

    Args:
        data: 已解析的字典数据

    Returns:
        (is_valid, errors)
    """
    errors = []

    try:
        schema = load_schema()
        validate(instance=data, schema=schema)
        return True, []
    except ValidationError as e:
        error_msg = f"字段 '{e.path[-1] if e.path else 'root'}': {e.message}"
        return False, [error_msg]
    except Exception as e:
        return False, [f"校验异常: {str(e)}"]


def extract_question_text(data: dict) -> str:
    """
    从结构化数据中提取 Markdown 格式的题目文本
    用于与老系统兼容

    Args:
        data: 校验通过的结构化数据

    Returns:
        Markdown 格式的题目文本
    """
    meta = data.get("meta", {})
    questions = data.get("questions", [])

    # 构建标题
    title = meta.get("title", "题目练习")
    md_lines = [f"# {title}", ""]

    # 构建题目
    for idx, q in enumerate(questions, 1):
        q_type = q.get("type", "UNKNOWN")
        stem = q.get("stem", "")
        options = q.get("options")
        sub_questions = q.get("sub_questions")
        passage = q.get("passage")

        md_lines.append(f"{idx}. {stem}")

        # 添加选项（单选题、多选题）
        if options:
            for opt in options:
                md_lines.append(f"   {opt}")

        # 添加阅读材料（阅读理解、完形填空）
        if passage:
            md_lines.append("")
            md_lines.append(passage)

        # 添加子题
        if sub_questions:
            for sub_idx, sub_q in enumerate(sub_questions, 1):
                sub_stem = sub_q.get("stem", "")
                sub_options = sub_q.get("options")
                md_lines.append(f"   {sub_idx}. {sub_stem}")
                if sub_options:
                    for opt in sub_options:
                        md_lines.append(f"      {opt}")

        md_lines.append("")

    return "\n".join(md_lines)


# 全局缓存 Schema（避免重复加载）
_schema_cache: Optional[dict] = None


def get_schema() -> dict:
    """获取缓存的 Schema"""
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = load_schema()
    return _schema_cache
