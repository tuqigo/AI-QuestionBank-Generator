# 认证模块安全修复实施计划

**生成时间**: 2026-03-14
**优先级**: CRITICAL
**预计工作量**: 1-2 天

---

## 执行摘要

本计划针对认证模块发现的安全漏洞进行全面修复，按风险等级分为三个阶段：

| 阶段 | 风险等级 | 修复项数 | 预计时间 |
|------|---------|---------|---------|
| Phase 1 | CRITICAL + HIGH | 4 项 | 4-6 小时 |
| Phase 2 | MEDIUM | 2 项 | 4-6 小时 |
| Phase 3 | LOW + 优化 | 3 项 | 2-3 小时 |

---

## Phase 1: 紧急安全修复（上线前必须完成）

### 1.1 JWT Secret 强制配置

**风险等级**: CRITICAL
**影响**: 攻击者可伪造任意用户 Token，完全绕过认证

#### 修改文件
- `backend/config.py`
- `backend/.env.example`

#### 实施步骤

**Step 1.1.1**: 修改 `backend/config.py`

```python
# 原代码 (Line 8):
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")

# 修改为:
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    raise ValueError(
        "JWT_SECRET must be configured in production environment. "
        "Generate a secure random string with at least 32 characters. "
        "Example: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )
```

**Step 1.1.2**: 更新 `backend/.env.example`

```bash
# 原内容:
JWT_SECRET=change-me-in-production

# 修改为:
# 生成方式：python -c 'import secrets; print(secrets.token_urlsafe(32))'
JWT_SECRET=your-secure-random-string-at-least-32-chars
```

**Step 1.1.3**: 添加部署检查脚本 `backend/scripts/check_security_config.py`

```python
#!/usr/bin/env python3
"""安全检查脚本 - 部署前运行"""
import os
import sys

def check_jwt_secret():
    secret = os.getenv("JWT_SECRET")
    if not secret:
        print("❌ JWT_SECRET not configured")
        return False
    if secret == "change-me-in-production":
        print("❌ JWT_SECRET using default value")
        return False
    if len(secret) < 32:
        print(f"❌ JWT_SECRET too short ({len(secret)} chars, need 32+)")
        return False
    print("✓ JWT_SECRET configured correctly")
    return True

def check_admin_password():
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        print("❌ ADMIN_PASSWORD not configured")
        return False
    if password == "admin123":
        print("❌ ADMIN_PASSWORD using default value")
        return False
    if len(password) < 8:
        print("❌ ADMIN_PASSWORD too short (need 8+ chars)")
        return False
    print("✓ ADMIN_PASSWORD configured correctly")
    return True

if __name__ == "__main__":
    results = [check_jwt_secret(), check_admin_password()]
    sys.exit(0 if all(results) else 1)
```

#### 测试要求
- [ ] 未配置 JWT_SECRET 时启动失败
- [ ] 使用默认值时启动失败
- [ ] 配置正确时正常启动

---

### 1.2 管理员密码加密存储 + 强度校验

**风险等级**: CRITICAL
**影响**: 默认密码易被猜测，明文存储易泄露

#### 修改文件
- `backend/services/admin_auth.py`
- `backend/routers/admin.py`
- `backend/.env.example`

#### 实施步骤

**Step 1.2.1**: 修改 `backend/services/admin_auth.py`

```python
"""管理员认证服务"""
import os
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

from config import JWT_SECRET, JWT_ALGORITHM
from utils.logger import auth_logger

# 管理员密码哈希（从环境变量读取）
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

# 管理员 Token 有效期（2 小时）
ADMIN_JWT_EXPIRE_MINUTES = int(os.getenv("ADMIN_JWT_EXPIRE_MINUTES", "120"))


def verify_admin_password(password: str) -> bool:
    """验证管理员密码"""
    if not ADMIN_PASSWORD_HASH:
        auth_logger.error("ADMIN_PASSWORD_HASH not configured")
        return False

    try:
        is_valid = bcrypt.checkpw(
            password.encode('utf-8'),
            ADMIN_PASSWORD_HASH.encode('utf-8')
        )
        auth_logger.debug(f"管理员密码验证：{'成功' if is_valid else '失败'}")
        return is_valid
    except Exception as e:
        auth_logger.error(f"管理员密码验证异常：{e}")
        return False


def hash_admin_password(password: str) -> str:
    """生成管理员密码哈希（用于初次配置）"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_admin_token() -> str:
    """创建管理员访问令牌"""
    expire = datetime.utcnow() + timedelta(minutes=ADMIN_JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": "admin",
        "role": "admin",
        "exp": expire
    }
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    auth_logger.info(f"管理员令牌创建成功，过期时间：{expire}")
    return token


def decode_admin_token(token: str) -> Optional[str]:
    """解码管理员令牌，返回 role"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = payload.get("role")
        if role == "admin":
            auth_logger.debug("管理员令牌验证成功")
            return role
        auth_logger.warning("令牌角色不是管理员")
        return None
    except JWTError as e:
        auth_logger.warning(f"管理员令牌解码失败：{e}")
        return None
    except Exception as e:
        auth_logger.error(f"管理员令牌解析异常：{e}")
        return None


def get_admin_token_expire_seconds() -> int:
    """获取 Token 有效期（秒）"""
    return ADMIN_JWT_EXPIRE_MINUTES * 60
```

**Step 1.2.2**: 添加工具脚本 `backend/scripts/generate_admin_password.py`

```python
#!/usr/bin/env python3
"""生成管理员密码哈希"""
import bcrypt
import getpass
import sys

def validate_password(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码至少 8 个字符"
    if len(password) > 64:
        return False, "密码不能超过 64 个字符"
    if not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"
    if not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, ""

if __name__ == "__main__":
    print("=== 管理员密码配置工具 ===\n")

    password = getpass.getpass("请输入管理员密码：")
    confirm = getpass.getpass("请再次输入密码确认：")

    if password != confirm:
        print("❌ 两次输入的密码不一致")
        sys.exit(1)

    valid, msg = validate_password(password)
    if not valid:
        print(f"❌ 密码强度不足：{msg}")
        sys.exit(1)

    # 生成哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    print("\n✓ 密码验证通过，哈希生成成功\n")
    print("请将以下内容添加到 .env 文件：\n")
    print(f"ADMIN_PASSWORD_HASH={hashed.decode('utf-8')}")
    print("\n⚠️ 请妥善保管此哈希值，不要泄露原始密码")
```

**Step 1.2.3**: 更新 `backend/.env.example`

```bash
# 原内容:
ADMIN_PASSWORD=admin123

# 修改为:
# 使用 scripts/generate_admin_password.py 生成哈希值
ADMIN_PASSWORD_HASH=your-bcrypt-hash-here
```

#### 测试要求
- [ ] 密码哈希工具正确生成 bcrypt 哈希
- [ ] 密码强度验证生效（8+ 字符，大小写，数字）
- [ ] 密码验证功能正常
- [ ] 未配置哈希值时启动报错

---

### 1.3 管理员登录速率限制

**风险等级**: HIGH
**影响**: 攻击者可暴力破解管理员密码

#### 修改文件
- `backend/routers/admin.py`
- `backend/services/admin_auth.py` (新增速率限制)

#### 实施步骤

**Step 1.3.1**: 在 `backend/services/admin_auth.py` 添加速率限制

```python
# 添加到文件顶部
import time
from typing import Dict

# 内存存储速率限制（生产环境应使用 Redis）
_login_attempts: Dict[str, list] = {}

# 速率限制配置
ADMIN_LOGIN_MAX_ATTEMPTS = int(os.getenv("ADMIN_LOGIN_MAX_ATTEMPTS", "5"))
ADMIN_LOGIN_WINDOW_MINUTES = int(os.getenv("ADMIN_LOGIN_WINDOW_MINUTES", "30"))


def check_admin_login_rate_limit(ip: str) -> bool:
    """检查管理员登录速率限制"""
    now = time.time()
    window_seconds = ADMIN_LOGIN_WINDOW_MINUTES * 60

    # 清理过期记录
    if ip in _login_attempts:
        _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < window_seconds]

    # 检查是否超出限制
    attempts = len(_login_attempts.get(ip, []))
    if attempts >= ADMIN_LOGIN_MAX_ATTEMPTS:
        auth_logger.warning(f"管理员登录速率限制触发 IP: {ip}, attempts: {attempts}")
        return False

    return True


def record_admin_login_attempt(ip: str):
    """记录管理员登录尝试"""
    now = time.time()
    if ip not in _login_attempts:
        _login_attempts[ip] = []
    _login_attempts[ip].append(now)


def get_lockout_remaining_seconds(ip: str) -> int:
    """获取锁定剩余时间（秒）"""
    now = time.time()
    window_seconds = ADMIN_LOGIN_WINDOW_MINUTES * 60
    attempts = _login_attempts.get(ip, [])

    if len(attempts) >= ADMIN_LOGIN_MAX_ATTEMPTS:
        oldest = min(attempts)
        remaining = window_seconds - (now - oldest)
        return max(0, int(remaining))

    return 0
```

**Step 1.3.2**: 修改 `backend/routers/admin.py` 登录接口

```python
# 原代码 (Line 46-67):
@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(request: AdminLogin, req: Request):
    """管理员登录"""
    ip = req.client.host if req.client else "unknown"

    # 验证密码
    if not verify_admin_password(request.password):
        api_logger.warning(f"管理员登录失败 - 密码错误，IP: {ip}")
        log_operation(operator="unknown", action="login_failed", target_type="admin", ip=ip, details="密码错误")
        raise HTTPException(status_code=401, detail="密码错误")

    # 创建 token
    token = create_admin_token()
    expires_in = get_admin_token_expire_seconds()

    api_logger.info(f"管理员登录成功，IP: {ip}")
    log_operation(operator="admin", action="login_success", target_type="admin", ip=ip)

    return AdminTokenResponse(
        access_token=token,
        expires_in=expires_in
    )

# 修改为:
@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(request: AdminLogin, req: Request):
    """管理员登录"""
    from services.admin_auth import (
        check_admin_login_rate_limit,
        record_admin_login_attempt,
        get_lockout_remaining_seconds
    )

    ip = req.client.host if req.client else "unknown"

    # 速率限制检查
    if not check_admin_login_rate_limit(ip):
        remaining = get_lockout_remaining_seconds(ip)
        api_logger.warning(f"管理员登录失败 - 速率限制，IP: {ip}")
        log_operation(
            operator="unknown",
            action="login_rate_limited",
            target_type="admin",
            ip=ip,
            details=f"速率限制触发，剩余{remaining}秒"
        )
        raise HTTPException(
            status_code=429,
            detail=f"登录尝试过于频繁，请{remaining // 60}分钟后再试"
        )

    # 记录登录尝试
    record_admin_login_attempt(ip)

    # 验证密码
    if not verify_admin_password(request.password):
        api_logger.warning(f"管理员登录失败 - 密码错误，IP: {ip}")
        log_operation(operator="unknown", action="login_failed", target_type="admin", ip=ip, details="密码错误")
        raise HTTPException(status_code=401, detail="密码错误")

    # 创建 token
    token = create_admin_token()
    expires_in = get_admin_token_expire_seconds()

    api_logger.info(f"管理员登录成功，IP: {ip}")
    log_operation(operator="admin", action="login_success", target_type="admin", ip=ip)

    return AdminTokenResponse(
        access_token=token,
        expires_in=expires_in
    )
```

**Step 1.3.3**: 更新 `backend/.env.example`

```bash
# 管理员登录速率限制
ADMIN_LOGIN_MAX_ATTEMPTS=5
ADMIN_LOGIN_WINDOW_MINUTES=30
```

#### 测试要求
- [ ] 连续失败 5 次后返回 429
- [ ] 锁定时间内无法登录
- [ ] 锁定时间过后可以重试
- [ ] 登录成功后计数器重置

---

### 1.4 CORS 配置收紧

**风险等级**: HIGH
**影响**: 可能导致 CSRF 攻击

#### 修改文件
- `backend/main.py`
- `backend/.env.example`

#### 实施步骤

**Step 1.4.1**: 修改 `backend/main.py`

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sql import init_database

# 初始化数据库
init_database()

from routers import questions, auth, extend, history, admin

app = FastAPI(title="题小宝 API")

# CORS 配置 - 从环境变量读取允许的来源
allow_origins_raw = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")
allow_origins = [origin.strip() for origin in allow_origins_raw.split(",") if origin.strip()]

# 验证 CORS 配置
if not allow_origins:
    raise ValueError("ALLOW_ORIGINS must be configured with at least one origin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    # 收紧允许的方法
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # 收紧允许的头部
    allow_headers=["Authorization", "Content-Type"],
    # 预检请求缓存时间
    max_age=3600,
)

app.include_router(auth.router)
app.include_router(questions.router)

# ... 其余代码不变
```

**Step 1.4.2**: 更新 `backend/.env.example`

```bash
# CORS 配置 - 多个来源用逗号分隔
# 生产环境示例:
# ALLOW_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### 测试要求
- [ ] 未配置的 Origin 被拒绝
- [ ] 配置的 Origin 正常访问
- [ ] 非允许的方法（如 PATCH）被拒绝
- [ ] 非允许的头部被拒绝

---

## Phase 2: 中等优先级修复

### 2.1 Token 存储迁移到 HttpOnly Cookie

**风险等级**: MEDIUM
**影响**: 防御 XSS 攻击导致的 Token 窃取

#### 修改文件
- `backend/routers/auth.py` (添加 Cookie 设置)
- `frontend/src/core/auth/authFactory.ts`
- `frontend/src/core/auth/userAuth.ts`
- `frontend/src/admin/auth.ts`

#### 实施步骤

**Step 2.1.1**: 后端添加 Set-Cookie 响应头

```python
# backend/routers/auth.py - 修改登录响应
from fastapi import Response

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, response: Response):
    """邮箱 + 密码登录"""
    # ... 原有逻辑 ...

    token = create_access_token({"sub": email})

    # 设置 HttpOnly Cookie
    response.set_cookie(
        key="qbank_token",
        value=token,
        httponly=True,      # JavaScript 无法访问
        secure=True,        # 仅 HTTPS (开发环境可设为 False)
        samesite="lax",     # CSRF 防护
        max_age=7 * 24 * 60 * 60,  # 7 天
        domain=None,        # 生产环境配置实际域名
    )

    api_logger.info(f"登录成功，email: {email}")
    return TokenResponse(access_token=token)
```

**Step 2.1.2**: 后端修改认证依赖从 Cookie 读取

```python
# backend/routers/auth.py
def get_current_user_email(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None,
) -> str:
    """获取当前登录用户邮箱 - 支持 Cookie 和 Header 两种方式"""
    token = None

    # 优先从 Header 读取
    if credentials:
        token = credentials.credentials
    # 备选从 Cookie 读取
    elif request:
        token = request.cookies.get("qbank_token")

    if not token:
        api_logger.warning("未提供认证凭据")
        raise HTTPException(status_code=401, detail="未登录")

    email = decode_token(token)
    if not email:
        api_logger.warning("令牌无效或已过期")
        raise HTTPException(status_code=401, detail="登录已过期")

    user = get_user(email)
    if not user:
        api_logger.warning(f"用户不存在：{email}")
        raise HTTPException(status_code=401, detail="用户不存在")

    return email
```

**Step 2.1.3**: 前端修改（如需支持 Cookie 方式）

```typescript
// frontend/src/core/auth/userAuth.ts
// 修改 fetchWithAuth 添加 credentials: 'include'

export const fetchWithAuth = createFetchWithAuth(
  auth,
  REQUEST_TIMEOUT,
  () => {
    // 401 回调 - 跳转登录
    window.location.href = '/'
  }
)

// 在 API 调用时使用
const response = await fetch(url, {
  ...options,
  credentials: 'include',  // 发送 Cookie
})
```

#### 测试要求
- [ ] 登录后 Cookie 正确设置
- [ ] Cookie 无法通过 JavaScript 读取
- [ ] 后续请求自动携带 Cookie
- [ ] 登出时 Cookie 被清除

---

### 2.2 密码长度上限验证

**风险等级**: MEDIUM
**影响**: bcrypt 截断导致长密码安全性降低

#### 修改文件
- `backend/routers/auth.py`
- `backend/services/admin_auth.py`

#### 实施步骤

**Step 2.2.1**: 修改用户密码验证

```python
# backend/routers/auth.py - _validate_password 函数

def _validate_password(password: str) -> Tuple[bool, str]:
    """验证密码强度，返回 (是否有效，错误信息)"""
    if len(password) < 6:
        return False, "密码至少 6 个字符"
    if len(password) > 32:  # 新增上限
        return False, "密码不能超过 32 个字符"

    # 建议添加：密码复杂度检查
    # if not re.search(r'[a-zA-Z]', password):
    #     return False, "密码必须包含字母"
    # if not re.search(r'\d', password):
    #     return False, "密码必须包含数字"

    return True, ""
```

**Step 2.2.2**: 修改管理员密码验证

```python
# backend/services/admin_auth.py - validate_password 函数

def validate_password(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码至少 8 个字符"
    if len(password) > 32:  # 新增上限
        return False, "密码不能超过 32 个字符"
    if not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"
    if not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, ""
```

#### 测试要求
- [ ] 超过 32 字符的密码被拒绝
- [ ] 错误信息明确提示长度限制

---

## Phase 3: 低优先级修复和优化

### 3.1 错误信息 sanitization

**风险等级**: LOW
**影响**: 可能泄露系统信息

#### 修改文件
- `backend/services/auth.py`
- `backend/routers/auth.py`

#### 实施步骤

```python
# backend/services/auth.py - decode_token 函数

def decode_token(token: str) -> Optional[str]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        auth_logger.debug(f"令牌解码成功，用户：{username}")
        return username
    except JWTError as e:
        # 不记录详细错误信息到日志
        auth_logger.warning("令牌解码失败")
        return None
    except Exception as e:
        auth_logger.error("令牌解析异常")
        return None
```

---

### 3.2 邮箱大小写统一处理审计

**风险等级**: LOW

#### 实施步骤

全局搜索所有邮箱处理代码，确保统一使用 `.lower()`:

```bash
# 使用 grep 检查
grep -r "\.email" backend/routers/
grep -r "email =" backend/
```

---

### 3.3 添加安全部署检查清单

创建 `DEPLOYMENT_SECURITY_CHECKLIST.md`:

```markdown
# 部署安全检查清单

## 环境变量检查
- [ ] JWT_SECRET 已配置且长度 >= 32
- [ ] ADMIN_PASSWORD_HASH 已配置（非默认值）
- [ ] ALLOW_ORIGINS 已配置为实际域名
- [ ] 已删除/覆盖 .env.example 中的默认值

## 运行检查脚本
```bash
python scripts/check_security_config.py
```

## 网络检查
- [ ] 已配置 HTTPS
- [ ] CORS 配置正确
- [ ] 管理后台不对外网开放（可选）
```

---

## 回滚计划

如修复后出现问题，可按以下步骤回滚：

1. **JWT Secret 问题**: 临时配置默认值恢复服务
2. **管理员密码**: 保留旧密码哈希，可同时支持新旧密码验证
3. **CORS**: 临时放宽配置

---

## SESSION_ID (用于 /ccg:execute)

- CODEX_SESSION: N/A (本计划由 Claude 生成)
- GEMINI_SESSION: N/A

---

## 附录：完整文件修改清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `backend/config.py` | 修改 | JWT Secret 强制校验 |
| `backend/services/admin_auth.py` | 修改 | 密码加密 + 速率限制 |
| `backend/routers/admin.py` | 修改 | 登录速率限制 |
| `backend/routers/auth.py` | 修改 | Cookie 认证支持 |
| `backend/main.py` | 修改 | CORS 收紧 |
| `backend/.env.example` | 修改 | 更新配置示例 |
| `backend/scripts/check_security_config.py` | 新增 | 安全检查脚本 |
| `backend/scripts/generate_admin_password.py` | 新增 | 密码哈希生成工具 |
| `frontend/src/core/auth/userAuth.ts` | 修改 | Cookie 支持 (可选) |
