"""千问多模态 API：识别图片中的题目并生成扩展题"""

import base64
import time
import json
import os
from dashscope import MultiModalConversation
from requests.exceptions import SSLError, RequestException

from config import DASHSCOPE_API_KEY
from services.qwen_client import generate_questions, _truncate_for_log, _parse_title_and_content
from utils.logger import qwen_logger

VISION_MODEL = os.getenv("QWEN_VISION_MODEL", "qwen-vl-plus")

VISION_SYSTEM = """你是一个小学题目识别专家。用户会上传一张包含数学或语文题目的图片。请识别图片中的题目内容、题型、难度和年级，并用一段简短的文字描述（50 字以内），便于后续生成同类型的扩展题目。只输出描述文字，不要输出其他内容。"""

EXTEND_PROMPT_TEMPLATE = """
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
14. 应用题需要在题目下方留出答题区域，格式：在题目后另起一行写"列式计算：______"并留 2 行空白（使用 `<br><br>` 或空行），方便学生写算式

用户需求：{description}
"""


def recognize_question_from_image(image_base64: str, image_media_type: str = "jpeg", max_retries: int = 3) -> str:
    """识别图片中的题目，返回描述文字"""
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】recognize_question_from_image")
    qwen_logger.info("=" * 60)

    qwen_logger.info(f"[图片信息] media_type: {image_media_type}, base64 长度：{len(image_base64)} 字符")

    if not DASHSCOPE_API_KEY:
        qwen_logger.error("DASHSCOPE_API_KEY 未配置")
        raise ValueError("DASHSCOPE_API_KEY 未配置")

    data_uri = f"data:image/{image_media_type};base64,{image_base64}"
    messages = [
        {
            "role": "user",
            "content": [
                {"image": data_uri},
                {"text": "请识别这张图片中的题目内容、题型、难度和年级，用一段简短的文字描述（50 字以内）。"},
            ],
        }
    ]

    # 记录请求信息
    qwen_logger.info(f"[调用模型] {VISION_MODEL}")
    qwen_logger.info(f"[Messages 结构] {json.dumps(messages, ensure_ascii=False, separators=(',', ':'))[:500]}...")

    # 调用 API（带重试）
    qwen_logger.info("[API 调用] 开始调用千问视觉 API...")

    last_error = None
    for attempt in range(max_retries):
        api_start = time.time()

        try:
            response = MultiModalConversation.call(
                model=VISION_MODEL,
                messages=messages,
                result_format="message",
                stream=False,
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
                error_msg = f"千问视觉 API 调用失败：code={response.code}, message={response.message}"
                qwen_logger.error(f"[API 错误] {error_msg}")
                # 如果是可重试的错误，继续重试
                if response.code in ['Stochastic', 'GatewayTimeout', 'ServiceUnavailable']:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指数退避：1s, 2s, 4s
                        qwen_logger.warning(f"[重试] 第 {attempt + 1} 次失败，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                raise RuntimeError(error_msg)

            # 成功获取响应，跳出重试循环
            break

        except (SSLError, RequestException) as e:
            last_error = e
            qwen_logger.warning(f"[网络错误] 第 {attempt + 1} 次尝试失败：{str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                qwen_logger.warning(f"[重试] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                qwen_logger.error(f"[网络错误] 重试 {max_retries} 次后仍然失败：{str(e)}")
                raise RuntimeError(f"网络连接失败，请检查网络环境或稍后重试：{str(e)}")
        except Exception as e:
            qwen_logger.error(f"[未知错误] {str(e)}")
            raise

    # 解析响应
    content = response.output.choices[0].message.content
    if isinstance(content, list):
        text = content[0].get("text", "") if content else ""
    else:
        text = str(content) if content else ""

    total_elapsed = time.time() - start_time
    qwen_logger.info(f"[识别结果] 描述长度：{len(text.strip())} 字符")
    qwen_logger.info(f"[识别结果] 描述内容：{text.strip()[:200]}...")
    qwen_logger.info(f"[识别结果] 总耗时：{total_elapsed:.2f} 秒")
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用结束】")
    qwen_logger.info("=" * 60)

    return text.strip()


def extend_questions_from_image(image_base64: str, image_media_type: str = "jpeg", hint: str = "") -> tuple[str, str]:
    """识别图片题目并生成同类型扩展题
    返回：(标题，题目内容)
    """
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】extend_questions_from_image")
    qwen_logger.info("=" * 60)

    qwen_logger.info(f"[用户补充] hint: {hint[:100] if hint else '无'}")

    description = recognize_question_from_image(image_base64, image_media_type)
    if hint:
        user_prompt = f"{description}。用户补充说明：{hint}"
    else:
        user_prompt = description

    qwen_logger.info(f"[图片识别描述] {description[:100]}...")
    qwen_logger.info(f"[最终 prompt] {user_prompt}")

    # 直接调用千问 API，避免 prompt 被重复包装
    from dashscope import Generation
    messages = [
        {"role": "system", "content": "你是小学 1-6 年级题库生成专家，根据用户需求生成练习题，输出 Markdown 格式。"},
        {"role": "user", "content": EXTEND_PROMPT_TEMPLATE.format(description=user_prompt)},
    ]

    qwen_logger.info(f"[调用模型] {os.getenv('QWEN_MODEL', 'qwen-plus-latest')}")
    api_start = time.time()

    response = Generation.call(
        model=os.getenv("QWEN_MODEL", "qwen-plus-latest"),
        messages=messages,
        result_format="message",
    )

    api_elapsed = time.time() - api_start
    qwen_logger.info(f"[API 调用] 耗时：{api_elapsed:.2f} 秒")

    if response.status_code != 200:
        raise RuntimeError(f"千问 API 调用失败：{response.code} - {response.message}")

    content = response.output.choices[0].message.content or ""

    # 解析标题和内容
    title, questions_content = _parse_title_and_content(content)
    qwen_logger.info(f"[解析结果] 标题：{title}")

    # 如果 AI 没有返回 TITLE 前缀，使用默认标题
    if not title or title == "AI 题目生成":
        title = f"扩展练习题（基于图片识别）"

    result = questions_content

    total_elapsed = time.time() - start_time
    qwen_logger.info(f"[扩展题生成] 最终结果长度：{len(result) if result else 0} 字符")
    qwen_logger.info(f"[扩展题生成] 总耗时：{total_elapsed:.2f} 秒")
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用结束】extend_questions_from_image")
    qwen_logger.info("=" * 60)

    return title, result
