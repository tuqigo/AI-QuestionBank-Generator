"""千问多模态 API：识别图片中的题目并生成扩展题"""

import base64
import time
import json
import os
from typing import Tuple, Optional
from dashscope import MultiModalConversation
from requests.exceptions import SSLError, RequestException

from config import DASHSCOPE_API_KEY, VISION_SYSTEM_PROMPT
from services.ai.qwen_client import generate_questions
from utils.logger import qwen_logger
from services.question.ai_generation_record_store import create_record, AiGenerationRecordCreate

VISION_MODEL = os.getenv("QWEN_VISION_MODEL", "qwen-vl-plus")


def recognize_question_from_image(image_base64: str, image_media_type: str = "jpeg", max_retries: int = 3, user_id: Optional[int] = None) -> str:
    """识别图片中的题目，返回描述文字"""
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】recognize_question_from_image")
    qwen_logger.info("=" * 60)

    qwen_logger.info(f"[图片信息] media_type: {image_media_type}, base64 长度：{len(image_base64)} 字符")

    if not DASHSCOPE_API_KEY:
        qwen_logger.error("DASHSCOPE_API_KEY 未配置")
        error_msg = "DASHSCOPE_API_KEY 未配置"
        # 记录失败日志
        if user_id:
            try:
                record = AiGenerationRecordCreate(
                    user_id=user_id,
                    prompt="图片识别",
                    prompt_type="vision",
                    success=False,
                    duration=round(time.time() - start_time, 2),
                    error_message=error_msg
                )
                create_record(record)
            except Exception as e:
                qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")
        raise ValueError(error_msg)

    data_uri = f"data:image/{image_media_type};base64,{image_base64}"
    messages = [
        {
            "role": "user",
            "content": [
                {"image": data_uri},
                {"text": VISION_SYSTEM_PROMPT},
            ],
        }
    ]

    # 记录请求信息
    qwen_logger.info(f"[调用模型] {VISION_MODEL}")
    qwen_logger.info(f"[Messages 结构] {json.dumps(messages, ensure_ascii=False, separators=(',', ':'))[:500]}...")

    # 调用 API（带重试）
    qwen_logger.info("[API 调用] 开始调用千问视觉 API...")

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
                # 记录失败日志
                if user_id:
                    try:
                        record = AiGenerationRecordCreate(
                            user_id=user_id,
                            prompt="图片识别",
                            prompt_type="vision",
                            success=False,
                            duration=round(time.time() - start_time, 2),
                            error_message=error_msg
                        )
                        create_record(record)
                    except Exception as e:
                        qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")
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

    # 记录成功日志
    if user_id:
        try:
            record = AiGenerationRecordCreate(
                user_id=user_id,
                prompt="图片识别",
                prompt_type="vision",
                success=True,
                duration=round(total_elapsed, 2)
            )
            create_record(record)
            qwen_logger.info(f"[记录保存] AI 生成记录保存成功：user_id={user_id}")
        except Exception as e:
            qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")

    return text.strip()


def extend_questions_from_image(image_base64: str, image_media_type: str = "jpeg", hint: str = "", user_id: Optional[int] = None) -> Tuple[str, str]:
    """识别图片题目并生成同类型扩展题
    返回：(标题，题目内容)
    """
    start_time = time.time()
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】extend_questions_from_image")
    qwen_logger.info("=" * 60)

    qwen_logger.info(f"[用户补充] hint: {hint[:100] if hint else '无'}")

    # 第一步：识别图片中的题目
    description = recognize_question_from_image(image_base64, image_media_type, user_id=user_id)

    # 第二步：组合用户 prompt（图片识别结果 + 用户补充）
    if hint:
        user_prompt = f"{description}。用户补充说明：{hint}"
    else:
        user_prompt = description

    qwen_logger.info(f"[图片识别描述] {description[:100]}...")
    qwen_logger.info(f"[最终 prompt] {user_prompt}")

    # 第三步：复用 generate_questions 生成题目（逻辑完全一致）
    title, questions_content = generate_questions(user_prompt, user_id=user_id)

    # 如果 AI 没有返回 TITLE 前缀，使用默认标题
    if not title or title == "AI 题目生成":
        title = f"扩展练习题（基于图片识别）"

    total_elapsed = time.time() - start_time
    qwen_logger.info(f"[扩展题生成] 最终结果长度：{len(questions_content) if questions_content else 0} 字符")
    qwen_logger.info(f"[扩展题生成] 总耗时：{total_elapsed:.2f} 秒")
    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用结束】extend_questions_from_image")
    qwen_logger.info("=" * 60)

    return title, questions_content
