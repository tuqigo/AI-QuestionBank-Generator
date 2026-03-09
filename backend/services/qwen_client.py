import dashscope
import time
import json
import re
from dashscope import Generation
from config import DASHSCOPE_API_KEY, QWEN_MODEL
from utils.logger import qwen_logger

# 全局设置 API key
dashscope.api_key = DASHSCOPE_API_KEY

SYSTEM_PROMPT = """你是小学 1 到 6 年级的题库生成专家，要根据用户需求生成题目。题目类型、难度得符合用户选的年级，输出用 Markdown 格式，包含题目、选项和答案。要是用户没说题目数量，就默认生成 20 道。请先输出全部题目，最后用 ## 答案 单独一段列出所有答案。"""


def _truncate_for_log(text: str, max_length: int = 500) -> str:
    """截断文本用于日志显示"""
    if not text:
        return "<empty>"
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"... [共 {len(text)} 字符]"


def _parse_title_and_content(content: str) -> tuple[str, str]:
    """解析 AI 返回的内容，提取标题和正文
    返回：(标题，题目内容)
    """
    if not content:
        return "AI 题目生成", ""

    lines = content.split('\n', 1)
    title_line = lines[0].strip()

    # 检查是否有 TITLE: 前缀
    match = re.match(r'^TITLE:\s*(.+)$', title_line, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        # 限制标题长度
        if len(title) > 100:
            title = title[:100] + "..."
        remaining_content = lines[1] if len(lines) > 1 else ""
        return title, remaining_content.strip()

    # 如果没有 TITLE 前缀，尝试从内容中提取标题
    # 通常第一行是 Markdown 标题 # 开头
    first_line_match = re.match(r'^#\s*(.+)$', title_line)
    if first_line_match:
        return first_line_match.group(1).strip(), content

    # 默认标题
    return "AI 题目生成", content


def generate_questions(user_prompt: str) -> tuple[str, str]:
    """生成题目
    返回：(标题，题目内容)
    """
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】generate_questions")
    qwen_logger.info("=" * 60)

    # 记录用户原始 prompt
    qwen_logger.info(f"[用户输入] {user_prompt}")
    qwen_logger.info(f"[用户输入长度] {len(user_prompt)} 字符")

    if not DASHSCOPE_API_KEY:
        qwen_logger.error("DASHSCOPE_API_KEY 未配置")
        raise ValueError("DASHSCOPE_API_KEY 未配置，请在 .env 中设置")

    user_content = f"""
你是小学 1–6 年级题库生成专家。任务：根据用户的输入需求生成练习题并以 Markdown 输出，便于前端直接渲染与导出为 PDF。

要求：
1. 题型、难度必须与目标年级严格匹配（若用户未指定年级，默认按一年级出题）。
2. 若用户未指定题目数量，默认生成 15 道题；若指定数量则按数量生成。
3. 支持题型：选择题、填空题、判断题、计算题（含竖式）、应用题等。若用户上传题目图片或在提示中说明"按图出题"，请先识别题型并生成同类题目扩展。
4. 每题输出包含：题号、题干、（若适用）选项。答案不出现在题目部分 答案要有 难度标签（简单/中等/困难）。
5. 在所有题目之后单独输出"答案"页，答案部分前必须插入标记 `<!-- PAGE_BREAK -->` 以便前端将答案分页打印到独立一页。
6. 输出不要包含任何生成模型、API 或调试信息，也不要额外说明调用方式。
7. 输出语言为中文，格式严格遵循 Markdown，便于用 marked.js 渲染。
8. 题号格式：使用阿拉伯数字加英文句点，如"1."、"2."、"10."、"11."等，题号与题干之间用一个空格分隔。
9. 选择题选项格式：每个选项单独一行，使用大写字母加英文句点，如"A. 选项内容"。
10. 比较大小/填运算符格式：使用方括号 `[   ]`（至少 3 个空格），如 `13 [   ] 17` 或 `12 [   ] 3 = 9`（填"＋"或"－"）。
11. 填空题格式：使用较长的下划线 `______`（至少 8 个下划线）或方框 `[     ]` 作为答题区域。
12. 题目不要有看图的
13. 填空题括号必须留足空格：`（     ）`（至少 10 个空格）、`[     ]`（至少 10 个空格）
15. 应用题需要在题目下方留出答题区域，格式：在题目后另起一行写"列式计算：______"并留 2 行空白（使用 `<br><br>` 或空行），方便学生写算式
16. **重要**：在输出内容的最前面，用一行单独的文本输出标题，格式为：`TITLE: 你的标题`（不超过 20 字），标题要能概括这份题目的内容，如"TITLE: 小学一年级 100 以内加减法混合运算"。

用户需求占位：{user_prompt}

示例输出（严格示范格式）：

TITLE: 小学一年级 100 以内加减法混合运算

# 小学一年级 口算练习
1. 7 + 2 =（         ）
2. 9 - 4 =（         ）
3. 10 - 5 + 3 =（         ）
4. 在 [   ] 里填上">""<"或"="：13 [   ] 17
5. 在 ○ 里填"＋"或"－"，使等式成立：12 [   ] 3 = 9
6. 小明有 8 个苹果，吃了 3 个，还剩几个？
   列式计算：______

7. 填空题：5 前面的数是 ______，7 后面的数是 ______。
...
10. 15 - 7 =（        ）
11. 6 + 9 =（        ）
12. 20 以内的加法：8 + 7 =（        ）
13. 应用题：妈妈买了 15 个苹果，小明吃了 3 个，又送给奶奶 5 个，还剩几个？
    列式计算：______


<!-- PAGE_BREAK -->

# 答案（单独一页）
1. 9  难度：简单
2. 5  难度：简单
3. 8  难度：中等
4. ＜  难度：简单
5. 5  难度：简单
6. 3 + 2 = 5  难度：中等
7. 4, 8  难度：中等
...
10. 8  难度：中等
11. 15  难度：中等
12. 15  难度：困难

"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    # 记录完整的请求信息
    qwen_logger.info(f"[调用模型] {QWEN_MODEL}")
    qwen_logger.info(f"[System Prompt] {_truncate_for_log(SYSTEM_PROMPT, 300)}")
    qwen_logger.info(f"[User Prompt 完整内容] {_truncate_for_log(user_content, 800)}")
    qwen_logger.info(f"[Messages 结构] {json.dumps(messages, ensure_ascii=False)[:2000]}...")

    # 调用 API
    qwen_logger.info("[API 调用] 开始调用千问 API...")
    api_start = time.time()

    response = Generation.call(
        model=QWEN_MODEL,
        messages=messages,
        result_format="message",
    )

    api_elapsed = time.time() - api_start
    qwen_logger.info(f"[API 调用] 耗时：{api_elapsed:.2f} 秒")

    # 记录响应详情
    qwen_logger.info(f"[API 响应] status_code: {response.status_code}")
    qwen_logger.info(f"[API 响应] code: {response.code}")
    qwen_logger.info(f"[API 响应] message: {response.message}")

    # 记录 token 使用情况
    if hasattr(response, 'usage') and response.usage:
        qwen_logger.info(f"[Token 使用] input_tokens: {response.usage.get('input_tokens', 'N/A')}, "
                        f"output_tokens: {response.usage.get('output_tokens', 'N/A')}, "
                        f"total_tokens: {response.usage.get('total_tokens', 'N/A')}")

    if response.status_code != 200:
        qwen_logger.error(f"[API 错误] 千问 API 调用失败：code={response.code}, message={response.message}")
        raise RuntimeError(f"千问 API 调用失败：{response.code} - {response.message}")

    content = response.output.choices[0].message.content
    total_elapsed = time.time() - start_time

    qwen_logger.info(f"[生成结果] 内容长度：{len(content) if content else 0} 字符")
    qwen_logger.info(f"[生成结果] 总耗时：{total_elapsed:.2f} 秒")
    qwen_logger.info(f"[生成结果] 输出预览] {_truncate_for_log(content, 500) if content else '<empty>'}")
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用结束】")
    qwen_logger.info("=" * 60)

    # 解析标题和内容
    title, questions_content = _parse_title_and_content(content or "")
    qwen_logger.info(f"[解析结果] 标题：{title}")

    return title, questions_content
