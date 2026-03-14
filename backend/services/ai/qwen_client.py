import atexit
import asyncio
import dashscope
import time
import re
import threading
import traceback
import json
from collections import deque
from typing import Tuple, Optional, List, Dict, Any
from concurrent.futures import Future, ThreadPoolExecutor
from dashscope import Generation
from config import (
    DASHSCOPE_API_KEY,
    QWEN_MODEL,
    QUESTION_PROMPT_TEMPLATE,
    QUESTION_SYSTEM_PROMPT
)
from utils.logger import qwen_logger
from services.question.ai_generation_record_store import create_record, AiGenerationRecordCreate

# 设置 DashScope API Key
if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY
    qwen_logger.info("[DashScope] API Key 已设置")
else:
    qwen_logger.error("[DashScope] API Key 未配置，请在 .env 中设置 DASHSCOPE_API_KEY")


# ===================== 1. 模型配置 =====================
MODEL_CONFIG = {
    "turbo": "qwen-turbo-latest",   # 低成本轻量版
    "plus": QWEN_MODEL               # 原有 Plus 版
}

# 简单/复杂问题判断规则
SIMPLE_QUESTION_MAX_LENGTH = 200
COMPLEX_KEYWORDS = ["解析", "推导", "多步骤", "证明", "详细解答", "综合分析", "压轴题", "奥数"]


# ===================== 3. Batch 请求类 =====================

class _BatchRequest:
    """Batch 请求内部类，封装单个请求信息"""
    __slots__ = ("user_prompt", "user_id", "future", "create_time", "is_simple")

    def __init__(self, user_prompt: str, user_id: Optional[int]):
        self.user_prompt = user_prompt
        self.user_id = user_id
        self.future = Future()  # 使用 concurrent.futures.Future (Python 3.8 兼容)
        self.create_time = time.time()
        self.is_simple = False


# ===================== 4. Batch 调用管理器 =====================

class QwenBatchManager:
    """
    Batch 请求管理器
    - 数量触发：攒够 batch_size 条立即提交
    - 超时触发：距离首个请求超过 max_wait_seconds 自动提交

    注意：DashScope 的 Batch API 是异步任务模式，不适合实时请求。
    此处使用并发单条调用来实现批量效果。
    """

    def __init__(self, batch_size: int = 10, max_wait_seconds: int = 5):
        self.batch_size = batch_size
        self.max_wait_seconds = max_wait_seconds
        self.request_queue = deque()  # type: deque[_BatchRequest]
        self.lock = threading.RLock()  # 使用 RLock 允许重入，避免死锁
        self.is_running = True

        # 启动定时检查线程
        self.thread = threading.Thread(target=self._check_timeout, daemon=True)
        self.thread.start()

        # 等待线程启动
        time.sleep(0.1)

        qwen_logger.info(
            f"[Batch 管理器] 初始化完成，批次大小={batch_size}，超时={max_wait_seconds}秒，线程启动={self.thread.is_alive()}"
        )

    @staticmethod
    def _is_simple_question(prompt: str) -> bool:
        """判断是否为简单问题，简单问题用 Turbo，复杂用 Plus"""
        if len(prompt.strip()) > SIMPLE_QUESTION_MAX_LENGTH:
            return False
        return not any(keyword in prompt for keyword in COMPLEX_KEYWORDS)

    def _check_timeout(self):
        """定时检查队列，超时自动提交"""
        qwen_logger.info("[Batch 超时检查] 线程启动")
        while self.is_running:
            time.sleep(0.5)  # 每 0.5 秒检查一次，提高响应速度
            batch_to_submit = None
            try:
                with self.lock:
                    if not self.request_queue:
                        continue

                    # 检查最早的请求是否超时
                    first_req_time = self.request_queue[0].create_time
                    elapsed = time.time() - first_req_time
                    qwen_logger.info(f"[Batch 超时检查] 队列有 {len(self.request_queue)} 条，最早请求已等待 {elapsed:.2f}秒")

                    if elapsed >= self.max_wait_seconds and len(self.request_queue) > 0:
                        qwen_logger.info(
                            f"[Batch 管理器] 超时触发提交，当前队列数={len(self.request_queue)}"
                        )
                        # 在锁内复制要提交的请求
                        batch_size = min(len(self.request_queue), self.batch_size)
                        batch_to_submit = list(self.request_queue)[:batch_size]
                        # 从队列移除已提交的请求
                        self.request_queue = deque(list(self.request_queue)[batch_size:])

                # 在锁外处理批次
                if batch_to_submit:
                    self._process_batch(batch_to_submit)
            except Exception as e:
                qwen_logger.error(f"[Batch 超时检查] 异常：{e}")
                qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")

    def add_request(self, user_prompt: str, user_id: Optional[int] = None) -> Future:
        """添加请求到队列，返回 Future 对象"""
        request = _BatchRequest(user_prompt, user_id)
        request.is_simple = self._is_simple_question(user_prompt)

        batch_to_submit = None
        with self.lock:
            self.request_queue.append(request)
            queue_size = len(self.request_queue)
            qwen_logger.info(f"[Batch 管理器] 添加请求，当前队列数={queue_size}")
            qwen_logger.info(f"[Batch 管理器] 请求 is_simple={request.is_simple}, prompt={user_prompt[:50]}...")

            # 攒够批次大小则提交
            if queue_size >= self.batch_size:
                qwen_logger.info(f"[Batch 管理器] 数量触发提交，队列数={queue_size}")
                # 在锁内复制要提交的请求
                batch_to_submit = list(self.request_queue)[:self.batch_size]
                # 从队列移除已提交的请求
                self.request_queue = deque(list(self.request_queue)[self.batch_size:])

        # 在锁外处理批次
        if batch_to_submit:
            self._process_batch(batch_to_submit)

        qwen_logger.info(f"[Batch 管理器] 返回 future，done={request.future.done()}")
        return request.future

    def _process_batch(self, batch_requests: List[_BatchRequest]):
        """处理批次请求（在锁外调用）"""
        qwen_logger.info("[Batch 处理] _process_batch 被调用")

        if not batch_requests:
            qwen_logger.warning("[Batch 处理] batch_requests 为空")
            return

        try:
            # 按模型分组（Turbo/Plus 分开调用）
            turbo_reqs = [req for req in batch_requests if req.is_simple]
            plus_reqs = [req for req in batch_requests if not req.is_simple]

            qwen_logger.info(f"[Batch 处理] turbo_reqs={len(turbo_reqs)}, plus_reqs={len(plus_reqs)}")

            if turbo_reqs:
                qwen_logger.info(f"[Batch 处理] 调用 turbo 模型")
                self._call_model_batch(MODEL_CONFIG["turbo"], turbo_reqs)
            if plus_reqs:
                qwen_logger.info(f"[Batch 处理] 调用 plus 模型")
                self._call_model_batch(MODEL_CONFIG["plus"], plus_reqs)

            qwen_logger.info("[Batch 处理] _process_batch 完成")
        except Exception as e:
            qwen_logger.error(f"[Batch 处理] 异常：{e}")
            qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
            # 确保失败的请求也设置异常
            for req in batch_requests:
                if not req.future.done():
                    req.future.set_exception(e)

    def _call_model_batch(self, model_name: str, batch_requests: List[_BatchRequest]):
        """
        并发调用模型 API（使用 ThreadPoolExecutor 实现并发）

        注意：DashScope 的 Batch API 是异步任务模式，不适合实时请求。
        此处使用并发单条调用来实现批量效果。
        """
        start_time = time.time()
        request_count = len(batch_requests)
        qwen_logger.info(f"[Batch 调用] 开始调用{model_name}，请求数={request_count}")
        for req in batch_requests:
            qwen_logger.info(f"[Batch 调用] 请求完整 prompt:\n{req.user_prompt}")

        try:
            success_count = 0
            error_count = 0

            def call_api(request: _BatchRequest) -> Tuple[Optional[str], Optional[Exception]]:
                """单个请求的 API 调用"""
                qwen_logger.info(f"[API 调用] 输入完整 prompt:\n{request.user_prompt}")
                try:
                    messages = [
                        {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
                        {"role": "user", "content": QUESTION_PROMPT_TEMPLATE.format(user_prompt=request.user_prompt)}
                    ]

                    qwen_logger.info(f"[API 调用] 调用 Generation.call，model={model_name}")
                    response = Generation.call(
                        model=model_name,
                        messages=messages,
                        result_format="message",
                        max_tokens=1500
                    )
                    qwen_logger.info(f"[API 调用] 响应返回，status={response.status_code}")

                    if response.status_code == 200 and response.output and response.output.choices:
                        content = response.output.choices[0].message.content
                        qwen_logger.info(f"[API 调用] 请求成功，内容长度={len(content) if content else 0}")
                        return content, None
                    else:
                        error = RuntimeError(f"API 调用失败：code={response.code}, message={response.message}")
                        qwen_logger.error(f"[API 调用] 失败：{error}")
                        return None, error
                except Exception as e:
                    qwen_logger.error(f"[API 调用] 异常：{e}")
                    qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
                    return None, e

            # 使用线程池并发调用
            qwen_logger.info(f"[Batch 调用] 准备调用 {request_count} 条请求，创建线程池")
            executor = ThreadPoolExecutor(max_workers=min(request_count, 5))  # 最多 5 个并发
            try:
                futures = {executor.submit(call_api, req): req for req in batch_requests}
                qwen_logger.info(f"[Batch 调用] 已提交 {len(futures)} 个任务到线程池")

                for future in futures:
                    req = futures[future]
                    try:
                        content, error = future.result(timeout=30)  # 单个请求最多 30 秒
                        if error:
                            req.future.set_exception(error)
                            error_count += 1
                            qwen_logger.error(f"[Batch 调用] 请求失败：{error}")
                        else:
                            req.future.set_result(content)
                            success_count += 1
                            qwen_logger.info(f"[Batch 调用] 请求成功，内容长度={len(content) if content else 0}")
                    except Exception as e:
                        req.future.set_exception(e)
                        error_count += 1
                        qwen_logger.error(f"[Batch 调用] 请求异常：{str(e)}")
                qwen_logger.info(f"[Batch 调用] 所有任务完成，成功={success_count}, 失败={error_count}")
            finally:
                executor.shutdown(wait=False)
                qwen_logger.info("[Batch 调用] 线程池已关闭")

            elapsed = time.time() - start_time
            qwen_logger.info(f"[Batch 调用] 完成，成功={success_count}, 失败={error_count}, 耗时={elapsed:.2f}秒")

            # 批量保存生成记录
            self._save_batch_records(batch_requests, success=True, elapsed=elapsed)

        except Exception as e:
            qwen_logger.error(f"[Batch 调用] 异常：{str(e)}")
            qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
            for req in batch_requests:
                if not req.future.done():
                    req.future.set_exception(e)
            self._save_batch_records(batch_requests, success=False, elapsed=time.time() - start_time, error=str(e))

    def _save_batch_records(self, batch_requests: List[_BatchRequest], success: bool,
                            elapsed: float, error: Optional[str] = None):
        """批量保存 AI 生成记录"""
        for req in batch_requests:
            if not req.user_id:
                continue
            try:
                record = AiGenerationRecordCreate(
                    user_id=req.user_id,
                    prompt=req.user_prompt,
                    prompt_type="text",
                    success=success,
                    duration=round(elapsed, 2),
                    error_message=error if error else None
                )
                create_record(record)
            except Exception as e:
                qwen_logger.error(f"[Batch 记录] 保存失败 user_id={req.user_id}: {e}")

    def stop(self):
        """停止 Batch 管理器"""
        self.is_running = False
        self.thread.join(timeout=1.0)
        qwen_logger.info("[Batch 管理器] 已停止")


# ===================== 4. 全局 Batch 管理器 =====================
# batch_size=10: 每 10 条请求批量提交一次
# max_wait_seconds=3: 即使不足 10 条，等待 3 秒后也会提交（避免单个请求等待太久）
batch_manager = QwenBatchManager(batch_size=10, max_wait_seconds=3)


# ===================== 5. 工具函数 =====================

def _format_for_log(text: str) -> str:
    """格式化文本用于日志显示，完整输出不截断"""
    if not text:
        return "<empty>"
    return text


import json
import traceback


def _fix_latex_escapes_in_json(json_str: str) -> str:
    """
    修复 JSON 字符串中的 LaTeX 转义问题（简化版，用于标题解析）

    将 $...$ 公式中的单反斜杠 LaTeX 命令修复为双反斜杠
    """
    LATEX_COMMANDS = {
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
    }

    result = []
    i = 0
    while i < len(json_str):
        if json_str[i] == '$':
            # 找到匹配的结束 $
            j = i + 1
            while j < len(json_str) and json_str[j] != '$':
                j += 1

            if j < len(json_str):
                # 修复公式内容中的 LaTeX 转义
                formula_content = json_str[i:j + 1]
                fixed_content = []
                k = 0
                while k < len(formula_content):
                    if formula_content[k] == '\\' and k + 1 < len(formula_content):
                        # 检查是否是双反斜杠
                        if formula_content[k + 1] == '\\':
                            fixed_content.append('\\\\')
                            k += 2
                            continue
                        # 检查是否是 LaTeX 命令
                        cmd_start = k + 1
                        cmd_end = cmd_start
                        while cmd_end < len(formula_content) and formula_content[cmd_end].isalpha():
                            cmd_end += 1
                        cmd = formula_content[cmd_start:cmd_end]
                        if cmd.lower() in LATEX_COMMANDS:
                            fixed_content.append('\\\\' + cmd)
                            k = cmd_end
                        else:
                            fixed_content.append(formula_content[k])
                            k += 1
                    else:
                        fixed_content.append(formula_content[k])
                        k += 1
                result.append(''.join(fixed_content))
                i = j + 1
            else:
                result.append(json_str[i])
                i += 1
        else:
            result.append(json_str[i])
            i += 1

    return ''.join(result)


def _parse_title_and_content(content: str) -> Tuple[str, str]:
    """解析 AI 返回的内容，提取标题和正文"""
    if not content:
        return "AI 题目生成", ""

    content_stripped = content.strip()

    # 检查是否是结构化 JSON（包含 meta.title）
    if content_stripped.startswith('{'):
        try:
            data = json.loads(content_stripped)
            # 尝试从 meta.title 提取
            if data.get('meta') and data['meta'].get('title'):
                title = data['meta']['title']
                if len(title) > 100:
                    title = title[:100] + "..."
                return title, content_stripped
        except (json.JSONDecodeError, KeyError):
            # JSON 解析失败，可能是 LaTeX 转义问题，尝试修复后重试
            try:
                fixed_content = _fix_latex_escapes_in_json(content_stripped)
                data = json.loads(fixed_content)
                if data.get('meta') and data['meta'].get('title'):
                    title = data['meta']['title']
                    if len(title) > 100:
                        title = title[:100] + "..."
                    return title, fixed_content
            except (json.JSONDecodeError, KeyError):
                # 修复后仍失败，继续其他解析
                pass

    # 检查是否有 TITLE: 前缀
    lines = content.split('\n', 1)
    title_line = lines[0].strip()
    match = re.match(r'^TITLE:\s*(.+)$', title_line, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        if len(title) > 100:
            title = title[:100] + "..."
        remaining_content = lines[1] if len(lines) > 1 else ""
        return title, remaining_content.strip()

    # 检查是否为 Markdown 标题
    first_line_match = re.match(r'^#\s*(.+)$', title_line)
    if first_line_match:
        return first_line_match.group(1).strip(), content

    # 默认标题
    return "AI 题目生成", content_stripped


# ===================== 6. 题目生成接口 =====================

def generate_questions(user_prompt: str, user_id: Optional[int] = None) -> Tuple[str, str]:
    """
    生成题目（同步版本，向后兼容）
    使用 ThreadPoolExecutor 包装异步调用
    """
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(_generate_questions_sync_wrapper, user_prompt, user_id)
        return future.result(timeout=15)  # 总超时 15 秒
    finally:
        executor.shutdown(wait=False)


def _generate_questions_sync_wrapper(user_prompt: str, user_id: Optional[int]) -> Tuple[str, str]:
    """同步包装器，在新线程中运行 asyncio 代码"""
    # Python 3.8 兼容：使用新的事件循环
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(generate_questions_async(user_prompt, user_id))
    finally:
        loop.close()


async def generate_questions_async(user_prompt: str, user_id: Optional[int] = None) -> Tuple[str, str]:
    """生成题目（异步版本，接入 Batch 管理器）"""
    start_time = time.time()

    qwen_logger.info("=" * 60)
    qwen_logger.info("【AI 调用开始】generate_questions（Batch 模式）")
    qwen_logger.info("=" * 60)
    qwen_logger.info(f"[用户输入] {user_prompt}")
    qwen_logger.info(f"[用户输入长度] {len(user_prompt)} 字符")

    if not DASHSCOPE_API_KEY:
        error_msg = "DASHSCOPE_API_KEY 未配置，请在 .env 中设置"
        qwen_logger.error(error_msg)
        _save_error_record(user_id, user_prompt, error_msg, time.time() - start_time)
        raise ValueError(error_msg)

    try:
        # 提交到 Batch 管理器
        future = batch_manager.add_request(user_prompt, user_id)

        # 等待结果（超时 30 秒）
        # 超时时间需要足够长，包括：Batch 等待时间（最多 5 秒）+ API 调用时间（最多 20 秒）+ 缓冲
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, lambda: future.result(timeout=30))

        total_elapsed = time.time() - start_time

        qwen_logger.info(f"[生成结果] 内容长度：{len(content) if content else 0} 字符")
        qwen_logger.info(f"[生成结果] 总耗时：{total_elapsed:.2f} 秒")
        qwen_logger.info(f"[生成结果] 输出内容预览：{content if content else '<empty>'}")

        title, questions_content = _parse_title_and_content(content or "")
        qwen_logger.info(f"[解析结果] 标题：{title}")

        qwen_logger.info("=" * 60)
        qwen_logger.info("【AI 调用结束】")
        qwen_logger.info("=" * 60)

        return title, questions_content

    except asyncio.TimeoutError:
        error_msg = "Batch 请求超时（超过 30 秒），请重试"
        qwen_logger.error(f"[Batch 超时] {error_msg}")
        qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        _save_error_record(user_id, user_prompt, error_msg, time.time() - start_time)
        raise RuntimeError(error_msg)

    except Exception as e:
        error_msg = f"Batch 调用失败：{str(e)}"
        qwen_logger.error(f"[Batch 异常] {error_msg}")
        qwen_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        _save_error_record(user_id, user_prompt, error_msg, time.time() - start_time)
        raise RuntimeError(error_msg)


def _save_error_record(user_id: Optional[int], prompt: str, error_msg: str, duration: float):
    """保存错误记录"""
    if not user_id:
        return
    try:
        record = AiGenerationRecordCreate(
            user_id=user_id,
            prompt=prompt,
            prompt_type="text",
            success=False,
            duration=round(duration, 2),
            error_message=error_msg
        )
        create_record(record)
    except Exception as e:
        qwen_logger.error(f"[记录保存] AI 生成记录保存失败：{e}")


# ===================== 7. 程序退出时停止 Batch 管理器 =====================
atexit.register(batch_manager.stop)
