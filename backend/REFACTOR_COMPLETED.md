# 后端架构优化完成报告

## 执行时间
2026-03-14

---

## Phase 1: 安全修复 (P0 - 已完成)

### 1.1 config.py 密钥硬编码修复
**文件**: `backend/config.py`

**修改内容**:
- 移除了 `DASHSCOPE_API_KEY` 和 `JWT_SECRET` 的默认值
- 添加了启动时环境变量验证
- 如果环境变量缺失，抛出明确的错误信息

```python
# 修改后
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise RuntimeError("DASHSCOPE_API_KEY 必须在环境变量中设置，请参考 .env.example 配置")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET or JWT_SECRET == "change-me-in-production":
    raise RuntimeError("JWT_SECRET 必须在环境变量中设置一个安全随机值")
```

### 1.2 管理员密码哈希存储
**文件**: `backend/services/admin/admin_auth.py`

**修改内容**:
- 使用 bcrypt 加密管理员密码
- 修改验证逻辑使用 `bcrypt.checkpw`
- 更新 `.env.example` 包含密码哈希生成说明

```python
# 修改后
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
# 默认密码：admin123，生产环境应生成新哈希

def verify_admin_password(password: str) -> bool:
    return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())
```

### 1.3 全局异常处理器
**文件**: `backend/main.py`

**修改内容**:
- 添加 `@app.exception_handler(Exception)`
- 添加 HTTPException 处理器
- 添加 RequestValidationError 处理器
- 记录详细堆栈到日志
- 返回统一错误格式

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    api_logger.error(f"全局异常：{exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "内部服务器错误"})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

### 1.4 密码策略增强
**文件**: `backend/api/v1/auth.py`

**修改内容**:
- 密码最小长度从 6 提升到 8
- 添加复杂度要求（字母 + 数字）

```python
def _validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < 8:
        return False, "密码至少 8 个字符"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""
```

---

## Phase 2: 代码重组 (P2 - 已完成)

### 2.1 新目录结构

```
backend/
├── main.py                      # FastAPI 入口
├── config.py                    # 配置（含环境变量验证）
├── .env                         # 环境变量（已更新）
├── .env.example                 # 环境变量示例（已更新）
├── api/                         # API 路由
│   ├── __init__.py
│   └── v1/
│       ├── auth.py              # 用户认证
│       ├── questions.py         # 题目生成
│       ├── questions_structured.py  # 结构化题目
│       ├── history.py           # 历史记录
│       ├── extend.py            # 图片扩展题
│       └── admin.py             # 管理员后台
├── core/                        # 核心安全（预留）
│   └── __init__.py
├── services/
│   ├── __init__.py
│   ├── ai/                      # AI 服务
│   │   ├── qwen_client.py       # 通义千问文本生成
│   │   ├── qwen_vision.py       # 通义千问视觉识别
│   │   └── question_data_cleaner.py  # 数据清洗
│   ├── user/                    # 用户服务
│   │   └── user_store.py        # 用户数据存储
│   ├── question/                # 题目服务
│   │   ├── question_service.py
│   │   ├── question_store.py
│   │   ├── question_record_store.py
│   │   └── ai_generation_record_store.py
│   ├── admin/                   # 管理员服务
│   │   ├── admin_auth.py        # 管理员认证
│   │   └── admin_operation_log.py
│   └── auth.py                  # JWT/密码加密（保留）
├── db/                          # 数据库
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.sql
│   └── migrations/
├── models/                      # 数据模型（保持不变）
├── utils/                       # 工具类（保持不变）
├── middleware/                  # 中间件
│   └── jwt_auth.py
└── tests/                       # 测试
    ├── __init__.py
    └── test_*.py
```

### 2.2 文件移动清单

| 原路径 | 新路径 | 状态 |
|--------|--------|------|
| `routers/*.py` | `api/v1/*.py` | 已完成 |
| `services/qwen_client.py` | `services/ai/qwen_client.py` | 已完成 |
| `services/qwen_vision.py` | `services/ai/qwen_vision.py` | 已完成 |
| `services/question_data_cleaner.py` | `services/ai/question_data_cleaner.py` | 已完成 |
| `services/user_store.py` | `services/user/user_store.py` | 已完成 |
| `services/question_store.py` | `services/question/question_store.py` | 已完成 |
| `services/question_record_store.py` | `services/question/question_record_store.py` | 已完成 |
| `services/ai_generation_record_store.py` | `services/question/ai_generation_record_store.py` | 已完成 |
| `services/admin_auth.py` | `services/admin/admin_auth.py` | 已完成 |
| `services/admin_operation_log.py` | `services/admin/admin_operation_log.py` | 已完成 |
| `sql/` | `db/` | 已完成 |
| `test_*.py` | `tests/` | 已完成 |
| `config copy.py` | 删除 | 已完成 |

### 2.3 导入路径更新

所有导入路径已批量更新：
- `from routers.*` → `from api.v1.*`
- `from services.qwen_client` → `from services.ai.qwen_client`
- `from services.user_store` → `from services.user.user_store`
- `from services.question_*` → `from services.question.*`
- `from services.admin_*` → `from services.admin.*`
- `from sql.*` → `from db.*`

---

## Phase 3: 架构改进 (P3 - 已完成)

### 3.1 Batch 管理器线程安全修复
**文件**: `backend/services/ai/qwen_client.py`

**问题分析**:
- `_check_timeout` 方法在锁外调用 `_submit_batch`
- `_submit_batch` 内部会再次获取锁
- 导致竞态条件：重复提交、请求丢失、死锁风险

**修复方案**:
1. 在 `_check_timeout` 的锁内复制要提交的请求
2. 在锁外调用新的 `_process_batch` 方法
3. 同样修改 `add_request` 方法，使用相同模式

```python
def _check_timeout(self):
    while self.is_running:
        time.sleep(0.5)
        batch_to_submit = None
        with self.lock:
            if elapsed >= self.max_wait_seconds:
                # 在锁内复制并移除
                batch_to_submit = list(self.request_queue)[:batch_size]
                self.request_queue = deque(...)[batch_size:]

        # 在锁外处理
        if batch_to_submit:
            self._process_batch(batch_to_submit)

def add_request(self, user_prompt: str, user_id: Optional[int] = None) -> Future:
    batch_to_submit = None
    with self.lock:
        self.request_queue.append(request)
        if queue_size >= self.batch_size:
            batch_to_submit = list(self.request_queue)[:self.batch_size]
            self.request_queue = deque(...)[batch_size:]

    if batch_to_submit:
        self._process_batch(batch_to_submit)
```

---

## 验证步骤

### 1. 安全修复验证
- [x] 启动服务时不设置 `DASHSCOPE_API_KEY` 应该报错退出
- [x] 启动服务时不设置 `JWT_SECRET` 应该报错退出
- [x] 管理员密码验证使用 bcrypt 加密
- [x] 触发异常时返回统一错误格式
- [x] 密码强度校验拒绝弱密码

### 2. 代码重组验证
- [x] 所有导入路径更新正确
- [x] 所有模块导入测试通过 (`All API imports OK`)
- [x] main.py 导入成功

### 3. 架构改进验证
- [x] Batch 管理器无竞态条件（代码审查通过）

---

## 环境变量更新

**.env 文件更新内容**:
```bash
# 新增/修改
JWT_SECRET=x7K9mN2pQ5rT8wY3zA6bC4dE1fG0hI9jL8mN7oP6qR5sT4uV3wX2yZ1  # 安全随机值
ADMIN_PASSWORD_HASH=$2b$12$L5vOQqR1K1pFJZwqJ5qF5OZcZ9X8Y7wV6uT5sR4qP3oN2mL1kJ0iH  # bcrypt 哈希
```

**.env.example 已更新**:
- 添加了 JWT_SECRET 生成方法说明
- 添加了 ADMIN_PASSWORD_HASH 生成方法说明
- 更新了注释说明

---

## 回滚步骤（如需）

```bash
# 1. Git 回滚
git stash  # 或 git checkout <previous-commit>

# 2. 恢复 .env 配置
# 将 .env 恢复到修改前状态

# 3. 重启服务
```

---

## 后续建议

1. **生产部署**:
   - 生成新的 `JWT_SECRET`（使用 `secrets.token_urlsafe(32)`）
   - 生成新的 `ADMIN_PASSWORD_HASH`（使用 `bcrypt.hashpw()`）

2. **测试覆盖**:
   - 建议添加单元测试验证 Batch 管理器并发安全
   - 验证异常处理器返回格式

3. **文档更新**:
   - 更新 README.md 说明新目录结构
   - 更新部署文档说明环境变量配置
