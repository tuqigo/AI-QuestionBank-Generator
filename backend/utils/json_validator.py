"""
JSON 校验工具
用于校验 AI 返回的题目 JSON 是否符合 Schema 规范
"""
import json
import os
import re
from typing import Tuple, List, Optional
from jsonschema import validate, ValidationError

from utils.logger import qwen_logger

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "backend", "schemas", "question_schema.json")

# LaTeX 命令列表（需要修复的单反斜杠转义）
LATEX_COMMANDS = [
    r'\\frac', r'\\times', r'\\div', r'\\pm', r'\\mp', r'\\ldots', r'\\cdots',
    r'\\geq', r'\\leq', r'\\neq', r'\\approx', r'\\rightarrow', r'\\leftarrow',
    r'\\mapsto', r'\\Rightarrow', r'\\Leftarrow', r'\\Leftrightarrow',
    r'\\infty', r'\\sqrt', r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln',
    r'\\sum', r'\\int', r'\\partial', r'\\nabla', r'\\bullet', r'\\cdot',
    r'\\circ', r'\\degree', r'\\prime', r'\\text', r'\\math', r'\\begin', r'\\end'
]

# 用于修复的正则表达式：匹配单反斜杠加 LaTeX 命令
LATEX_FIX_PATTERN = re.compile(
    r'(\\)([a-zA-Z]+)',
    re.IGNORECASE
)


def _fix_latex_escapes(json_str: str) -> str:
    """
    修复 JSON 字符串中的 LaTeX 转义问题

    AI 有时会返回单反斜杠的 LaTeX 命令（如 \div），这在 JSON 中是无效的。
    需要将单反斜杠替换成双反斜杠（\\div），这样 JSON 解析后才是正确的 LaTeX。

    Args:
        json_str: 原始 JSON 字符串

    Returns:
        修复后的 JSON 字符串
    """
    # 方法：遍历所有 $...$ 公式环境，修复其中的 LaTeX 转义

    LATEX_COMMANDS = [
        'frac', 'times', 'div', 'pm', 'mp', 'ldots', 'cdots',
        'geq', 'leq', 'neq', 'approx', 'rightarrow', 'leftarrow',
        'Rightarrow', 'Leftarrow', 'Leftrightarrow', 'infty',
        'sqrt', 'sin', 'cos', 'tan', 'log', 'ln',
        'sum', 'int', 'partial', 'nabla', 'bullet', 'cdot',
        'circ', 'degree', 'prime', 'text', 'math', 'begin', 'end',
        'pi', 'theta', 'alpha', 'beta', 'gamma', 'delta', 'epsilon',
        'angle', 'triangle', 'perp', 'parallel', 'cup', 'cap',
        'subset', 'supset', 'subseteq', 'supseteq', 'in', 'notin',
        'forall', 'exists', 'to', 'mapsto', 'iff', 'hbar', 'omega'
    ]

    def fix_formula_content(content):
        """修复公式内容中的 LaTeX 转义"""
        # 替换 \command 为 \\command（只在 \ 前面不是另一个 \ 的情况下）
        # 使用逐字符扫描，更可靠
        result = []
        i = 0
        while i < len(content):
            if content[i] == '\\' and i + 1 < len(content):
                # 检查是否是双反斜杠
                if content[i + 1] == '\\':
                    # 已经是双反斜杠，保留
                    result.append('\\\\')
                    i += 2
                    continue

                # 检查是否是 LaTeX 命令
                cmd_start = i + 1
                cmd_end = cmd_start
                while cmd_end < len(content) and content[cmd_end].isalpha():
                    cmd_end += 1
                cmd = content[cmd_start:cmd_end]

                if cmd in LATEX_COMMANDS:
                    # 这是单反斜杠的 LaTeX 命令，替换为双反斜杠
                    result.append('\\\\' + cmd)
                    i = cmd_end
                else:
                    # 不是 LaTeX 命令，保留原样
                    result.append(content[i])
                    i += 1
            else:
                result.append(content[i])
                i += 1

        return ''.join(result)

    # 匹配 $...$ 公式环境（非贪婪）
    result = []
    i = 0
    while i < len(json_str):
        if json_str[i] == '$':
            # 找到匹配的结束 $
            j = i + 1
            while j < len(json_str) and json_str[j] != '$':
                j += 1

            if j < len(json_str):
                # 找到了匹配的 $
                formula = json_str[i:j + 1]
                # 修复公式中的 LaTeX 转义
                fixed_formula = fix_formula_content(formula)
                result.append(fixed_formula)
                i = j + 1
            else:
                # 没有匹配的 $
                result.append(json_str[i])
                i += 1
        else:
            result.append(json_str[i])
            i += 1

    return ''.join(result)


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
        # JSON 解析失败，尝试修复 LaTeX 转义后重试
        qwen_logger.warning(f"[JSON 校验] JSON 解析失败，尝试修复 LaTeX 转义: {str(e)}")
        try:
            fixed_json_str = _fix_latex_escapes(json_str)
            if fixed_json_str != json_str:
                qwen_logger.info("[JSON 校验] 已修复 LaTeX 转义")
                data = json.loads(fixed_json_str)
            else:
                return False, None, [f"JSON 解析失败: {str(e)}"]
        except json.JSONDecodeError as e2:
            return False, None, [f"JSON 解析失败 (修复后仍失败): {str(e2)}"]

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
