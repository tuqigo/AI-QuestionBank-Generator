"""
题目数据清洗服务
负责解析 AI 返回的原始 JSON 并填充 answer_blanks、rows_to_answer、answer_text 等字段
"""
import json
import traceback
from typing import List, Dict, Any, Optional, Tuple
from utils.logger import api_logger


# ===================== 题型常量 =====================

class QuestionType:
    """题型枚举"""
    SINGLE_CHOICE = "SINGLE_CHOICE"           # 单选题
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"       # 多选题
    TRUE_FALSE = "TRUE_FALSE"                 # 判断题
    FILL_BLANK = "FILL_BLANK"                 # 填空题
    CALCULATION = "CALCULATION"               # 计算题
    WORD_PROBLEM = "WORD_PROBLEM"             # 应用题
    GEOMETRY = "GEOMETRY"                     # 几何题
    READ_COMP = "READ_COMP"                   # 阅读理解
    POETRY_APP = "POETRY_APP"                 # 古诗文鉴赏
    CLOZE = "CLOZE"                           # 完形填空
    ESSAY = "ESSAY"                           # 作文题


# ===================== 作答行数计算规则 =====================

def calculate_rows_to_answer(question_type: str, question_data: Dict[str, Any]) -> int:
    """
    计算题目预留作答行数

    规则：
    - 单选题/判断题/填空题：1 行
    - 计算题/应用题/几何题：3 行
    - 古诗文鉴赏：3 行
    - 作文题：10 行
    - 阅读理解/完形填空：题干行数 + 子题数 × 2
    """
    # 基础题型固定行数
    basic_rows = {
        QuestionType.SINGLE_CHOICE: 1,
        QuestionType.MULTIPLE_CHOICE: 1,
        QuestionType.TRUE_FALSE: 1,
        QuestionType.FILL_BLANK: 1,
        QuestionType.CALCULATION: 3,
        QuestionType.WORD_PROBLEM: 3,
        QuestionType.GEOMETRY: 3,
        QuestionType.POETRY_APP: 3,
        QuestionType.ESSAY: 10,
    }

    if question_type in basic_rows:
        return basic_rows[question_type]

    # 阅读理解/完形填空：题干行数 + 子题数 × 2
    if question_type in [QuestionType.READ_COMP, QuestionType.CLOZE]:
        passage = question_data.get("passage", "")
        passage_lines = len(passage.split("\n")) if passage else 1
        sub_questions = question_data.get("sub_questions", [])
        sub_questions_count = len(sub_questions) if sub_questions else 0
        return passage_lines + sub_questions_count * 2

    # 默认 1 行
    return 1


# ===================== 填空题空格数计算 =====================

def calculate_answer_blanks(question_type: str, question_data: Dict[str, Any]) -> Optional[int]:
    """
    计算填空题的空格数量

    通过分析题干中的下划线或空白标记来确定
    """
    if question_type != QuestionType.FILL_BLANK:
        return None

    stem = question_data.get("stem", "")

    # 统计下划线数量（______ 或 ___）
    underscore_count = stem.count("______") + stem.count("___") + stem.count("__")

    # 统计方括号空白 [  ] 或 [_]
    bracket_blank_count = stem.count("[  ]") + stem.count("[ ]") + stem.count("[_]")

    # 统计大括号空白 {____}
    brace_blank_count = stem.count("{____}")

    total_blanks = underscore_count + bracket_blank_count + brace_blank_count

    # 如果都没有检测到，默认为 1
    return total_blanks if total_blanks > 0 else 1


# ===================== 答案提取 =====================

def extract_answer_text(question_type: str, question_data: Dict[str, Any]) -> Optional[str]:
    """
    从题目数据中提取/生成标准答案

    注意：当前 AI 返回的 JSON 中可能不包含答案字段
    此函数预留接口，未来可通过以下方式获取答案：
    1. 从 AI 返回的 answer 字段提取
    2. 从 AI 返回的 explanation 字段提取
    3. 人工录入答案后存储
    """
    # 尝试从 AI 返回数据中提取答案
    answer = question_data.get("answer")
    if answer:
        return str(answer)

    # 尝试从 explanation 中提取
    explanation = question_data.get("explanation")
    if explanation:
        # 简单提取：取 explanation 的前 50 个字符
        return explanation[:50] + "..." if len(explanation) > 50 else explanation

    # 选择题：如果有选项，可以预留答案位置
    if question_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE]:
        options = question_data.get("options")
        if options:
            # 答案待定，返回占位符
            return "【答案待录入】"

    return None


# ===================== 数据清洗主函数 =====================

class QuestionDataCleaner:
    """题目数据清洗类"""

    @staticmethod
    def clean_question(question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗单道题目数据，填充后端字段

        Args:
            question_data: AI 返回的原始题目数据

        Returns:
            清洗后的题目数据，包含：
            - type: 题型
            - stem: 题干
            - options: 选项（如有）
            - passage: 阅读材料（如有）
            - sub_questions: 子题（如有）
            - knowledge_points: 知识点
            - answer_blanks: 填空题空格数（后端填充）
            - rows_to_answer: 作答行数（后端填充）
            - answer_text: 标准答案（后端填充）
        """
        question_type = question_data.get("type", "")

        # 计算后端填充字段
        rows_to_answer = calculate_rows_to_answer(question_type, question_data)
        answer_blanks = calculate_answer_blanks(question_type, question_data)
        answer_text = extract_answer_text(question_type, question_data)

        # 构建清洗后的数据
        cleaned_data = {
            "type": question_type,
            "stem": question_data.get("stem", ""),
            "options": question_data.get("options"),
            "passage": question_data.get("passage"),
            "sub_questions": question_data.get("sub_questions"),
            "knowledge_points": question_data.get("knowledge_points", []),
            "rows_to_answer": rows_to_answer,
            "answer_blanks": answer_blanks,
            "answer_text": answer_text,
            # 保留原始数据用于调试
            "_original": question_data
        }

        return cleaned_data

    @staticmethod
    def clean_questions(questions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量清洗题目数据

        Args:
            questions_data: AI 返回的原始题目列表

        Returns:
            清洗后的题目列表
        """
        cleaned_questions = []
        for i, q in enumerate(questions_data):
            try:
                cleaned = QuestionDataCleaner.clean_question(q)
                cleaned["_index"] = i + 1  # 题目序号
                cleaned_questions.append(cleaned)
            except Exception as e:
                api_logger.error(f"清洗题目第 {i+1} 题失败：{e}")
                api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
                # 清洗失败时保留最小数据集
                cleaned_questions.append({
                    "type": q.get("type", "UNKNOWN"),
                    "stem": q.get("stem", ""),
                    "options": q.get("options"),
                    "passage": q.get("passage"),
                    "sub_questions": q.get("sub_questions"),
                    "knowledge_points": q.get("knowledge_points", []),
                    "rows_to_answer": 1,
                    "answer_blanks": None,
                    "answer_text": None,
                    "_index": i + 1,
                    "_error": str(e)
                })

        return cleaned_questions

    @staticmethod
    def parse_ai_response(ai_response: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        解析 AI 返回的 JSON 字符串，提取 meta 和 questions

        Args:
            ai_response: AI 返回的原始 JSON 字符串

        Returns:
            (meta, questions_list) 元组
            - meta: 元数据（subject, grade, title）
            - questions_list: 清洗后的题目列表
        """
        try:
            data = json.loads(ai_response)

            # 提取 meta 数据
            meta = data.get("meta", {})

            # 提取题目列表
            questions_raw = data.get("questions", [])

            if not questions_raw:
                api_logger.warning("AI 返回的题目列表为空")
                return meta, []

            # 清洗题目数据
            cleaned_questions = QuestionDataCleaner.clean_questions(questions_raw)

            return meta, cleaned_questions

        except json.JSONDecodeError as e:
            api_logger.error(f"解析 AI 返回的 JSON 失败：{e}")
            api_logger.error(f"原始内容：{ai_response[:500]}...")
            return None, []
        except Exception as e:
            api_logger.error(f"解析 AI 返回数据失败：{e}")
            api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
            return None, []
