"""
题目数据清洗服务测试
"""
import sys
sys.path.insert(0, 'D:/project/AI-QuestionBank-Generator/backend')

from services.question_data_cleaner import QuestionDataCleaner

# 测试 AI 返回的原始 JSON
ai_response = """
{
  "meta": {
    "subject": "math",
    "grade": "grade3",
    "title": "三年级数学万以内加减法同步练习"
  },
  "questions": [
    {
      "type": "SINGLE_CHOICE",
      "stem": "计算 352 + 148 的结果是？",
      "options": ["400", "500", "600", "450"],
      "knowledge_points": ["万以内加法计算"]
    },
    {
      "type": "CALCULATION",
      "stem": "脱式计算：800 - 256 + 144",
      "knowledge_points": ["万以内加减混合运算"]
    },
    {
      "type": "FILL_BLANK",
      "stem": "300 + ______ = 500",
      "knowledge_points": ["加法逆运算"]
    }
  ]
}
"""

print("=" * 60)
print("题目数据清洗测试")
print("=" * 60)

# 解析 AI 响应
meta, cleaned_questions = QuestionDataCleaner.parse_ai_response(ai_response)

print(f"\nMeta 数据:")
print(f"  subject: {meta.get('subject')}")
print(f"  grade: {meta.get('grade')}")
print(f"  title: {meta.get('title')}")

print(f"\n清洗后的题目:")
for i, q in enumerate(cleaned_questions, 1):
    print(f"\n  题目 {i}:")
    print(f"    type: {q['type']}")
    print(f"    stem: {q['stem']}")
    print(f"    rows_to_answer: {q['rows_to_answer']}")
    print(f"    answer_blanks: {q['answer_blanks']}")
    print(f"    answer_text: {q['answer_text']}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
