import dashscope
import time
import json
import re
import asyncio
from typing import Tuple, Optional
from dashscope import Generation
from config import DASHSCOPE_API_KEY, QWEN_MODEL, QUESTION_SYSTEM_PROMPT, QUESTION_PROMPT_TEMPLATE
from utils.logger import qwen_logger
from services.ai_generation_record_store import create_record, AiGenerationRecordCreate

# 全局设置 API key
dashscope.api_key = DASHSCOPE_API_KEY


def _truncate_for_log(text: str, max_length: int = 500) -> str:
    """截断文本用于日志显示"""
    if not text:
        return "<empty>"
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"... [共 {len(text)} 字符]"


def _parse_title_and_content(content: str) -> Tuple[str, str]:
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


def generate_questions(user_prompt: str, user_id: Optional[int] = None) -> Tuple[str, str]:
    """生成题目（同步版本，用于向后兼容）"""
    import concurrent.futures
    # 始终在线程池中执行，避免事件循环问题
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: asyncio.run(generate_questions_async(user_prompt, user_id)))
        return future.result()


async def generate_questions_async(user_prompt: str, user_id: Optional[int] = None) -> Tuple[str, str]:
    """生成题目（异步版本）"""
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】generate_questions")
    qwen_logger.info("=" * 60)

    # 记录用户原始 prompt
    qwen_logger.info(f"[用户输入] {user_prompt}")
    qwen_logger.info(f"[用户输入长度] {len(user_prompt)} 字符")

    if not DASHSCOPE_API_KEY:
        qwen_logger.error("DASHSCOPE_API_KEY 未配置")
        error_msg = "DASHSCOPE_API_KEY 未配置，请在 .env 中设置"
        # 记录失败日志
        if user_id:
            try:
                record = AiGenerationRecordCreate(
                    user_id=user_id,
                    prompt=user_prompt,
                    prompt_type="text",
                    success=False,
                    duration=round(time.time() - start_time, 2),
                    error_message=error_msg
                )
                create_record(record)
            except Exception as e:
                qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")
        raise ValueError(error_msg)

    user_content = QUESTION_PROMPT_TEMPLATE.format(user_prompt=user_prompt)
    messages = [
        {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    # 记录完整的请求信息
    qwen_logger.info(f"[调用模型] {QWEN_MODEL}")
    qwen_logger.info(f"[System Prompt] {_truncate_for_log(QUESTION_SYSTEM_PROMPT, 300)}")
    qwen_logger.info(f"[User Prompt 完整内容] {_truncate_for_log(user_content, 800)}")
    qwen_logger.info(f"[Messages 结构] {json.dumps(messages, ensure_ascii=False)[:2000]}...")

    # 调用 API（在线程池中执行，避免阻塞事件循环）
    qwen_logger.info("[API 调用] 开始调用千问 API...")
    api_start = time.time()

    # 使用 loop.run_in_executor 将同步调用放入线程池（Python 3.8 兼容）
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,  # 使用默认线程池
        lambda: Generation.call(
            model=QWEN_MODEL,
            messages=messages,
            result_format="message",
        )
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
        error_msg = f"千问 API 调用失败：code={response.code}, message={response.message}"
        qwen_logger.error(f"[API 错误] {error_msg}")
        # 记录失败日志
        if user_id:
            try:
                record = AiGenerationRecordCreate(
                    user_id=user_id,
                    prompt=user_prompt,
                    prompt_type="text",
                    success=False,
                    duration=round(time.time() - start_time, 2),
                    error_message=error_msg
                )
                create_record(record)
            except Exception as e:
                qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")
        raise RuntimeError(error_msg)

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

    # 记录成功日志（异步，不阻塞）
    if user_id:
        try:
            record = AiGenerationRecordCreate(
                user_id=user_id,
                prompt=user_prompt,
                prompt_type="text",
                success=True,
                duration=round(total_elapsed, 2)
            )
            create_record(record)
            qwen_logger.info(f"[记录保存] AI 生成记录保存成功：user_id={user_id}")
        except Exception as e:
            qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")

    return title, questions_content
