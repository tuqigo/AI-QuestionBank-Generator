# 环境变量配置指南

> 详细说明所有可用的环境变量及其用途

---

## 后端环境变量 (backend/.env)

### AI 服务配置

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `DASHSCOPE_API_KEY` | **是** | 通义千问 API 密钥 | - | `sk-xxxxxxxxxxxxxxxx` |
| `QWEN_MODEL` | 否 | 文本生成模型 | `qwen-plus-latest` | `qwen-plus` |
| `QWEN_VISION_MODEL` | 否 | 视觉识别模型 | `qwen-vl-plus` | `qwen-vl-max` |

**获取 API Key：**
1. 访问 [DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 登录/注册阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key

**模型选择建议：**
- `qwen-plus-latest`: 性价比高，适合题目生成
- `qwen-max`: 最强模型，适合复杂任务
- `qwen-vl-plus`: 图片识别，性价比高
- `qwen-vl-max`: 高精度图片识别

---

### 认证配置

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `JWT_SECRET` | **是** | JWT 签名密钥 | `change-me-in-production` | `your-random-secret-123` |
| `JWT_ALGORITHM` | 否 | JWT 签名算法 | `HS256` | `HS256` |
| `JWT_EXPIRE_MINUTES` | 否 | Token 有效期 (分钟) | `10080` (7 天) | `1440` (1 天) |

**安全建议：**
```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用 openssl
openssl rand -hex 32
```

---

### 邮件服务配置 (SMTP)

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `SMTP_HOST` | 否 | SMTP 服务器地址 | `smtp.163.com` | `smtp.gmail.com` |
| `SMTP_PORT` | 否 | SMTP 端口 | `465` | `587` |
| `SMTP_USER` | 否 | SMTP 用户名 (邮箱) | - | `your-email@163.com` |
| `SMTP_PASS` | 否 | SMTP 密码/授权码 | - | `your-auth-code` |
| `SMTP_FROM_NAME` | 否 | 发件人名称 | `题小宝` | `AI 题库` |
| `SMTP_USE_TLS` | 否 | 使用 TLS 加密 | `true` | `true`/`false` |

**常用 SMTP 配置：**

| 服务商 | SMTP_HOST | SMTP_PORT | TLS | 说明 |
|--------|-----------|-----------|-----|------|
| 163 邮箱 | smtp.163.com | 465 | 是 | 需开启 SMTP 服务 |
| QQ 邮箱 | smtp.qq.com | 465 | 是 | 使用授权码，非登录密码 |
| Gmail | smtp.gmail.com | 587 | 是 | 需开启"不安全应用" |
| Outlook | smtp.office365.com | 587 | 是 | 企业邮箱 |

**获取授权码 (以 163 邮箱为例)：**
1. 登录 163 邮箱网页版
2. 设置 → POP3/SMTP/IMAP
3. 开启 SMTP 服务
4. 生成授权码

---

### OTP 验证码配置

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `OTP_EXPIRE_MINUTES` | 否 | 验证码有效期 | `5` | `10` |
| `TARGET_USER_IDS` | 否 | 运营目标用户 ID 列表 | - | `1,2,3` |

---

### 管理员配置

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `ADMIN_PASSWORD` | 否 | 管理员登录密码 | `admin123` | `your-admin-password` |
| `ADMIN_JWT_EXPIRE_MINUTES` | 否 | 管理员 Token 有效期 | `120` | `480` |

**安全建议：**
- 生产环境务必修改默认管理员密码
- 密码建议 12 位以上，包含大小写字母、数字、符号

---

### CORS 配置

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `ALLOW_ORIGINS` | 否 | 允许的前端来源 | `http://localhost:5173` | `https://your-domain.com` |

**生产环境配置示例：**
```bash
ALLOW_ORIGINS=https://tixiaobao.example.com,https://www.tixiaobao.example.com
```

**多个来源用逗号分隔：**
```bash
ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-domain.com
```

---

## 前端环境变量

前端使用 Vite，环境变量以 `VITE_` 开头：

| 变量 | 必填 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `VITE_API_BASE_URL` | 否 | API 基础地址 | `/api` | `https://api.tixiaobao.com` |
| `VITE_CLOUDFLARE_PROJECT` | 否 | Cloudflare Pages 项目名 | - | `tixiaobao` |

### 创建前端 .env 文件

```bash
cd frontend
cat > .env << EOF
VITE_API_BASE_URL=/api
VITE_CLOUDFLARE_PROJECT=tixiaobao
EOF
```

---

## 环境检查脚本

```bash
#!/bin/bash
# check_env.sh

echo "=== 后端环境检查 ==="

cd backend

if [ ! -f .env ]; then
    echo "❌ .env 文件不存在"
    exit 1
fi

echo "✓ .env 文件存在"

# 检查必要变量
REQUIRED_VARS=("DASHSCOPE_API_KEY" "JWT_SECRET")

for var in "${REQUIRED_VARS[@]}"; do
    value=$(grep "^$var=" .env | cut -d'=' -f2)
    if [ -z "$value" ] || [[ "$value" == *"change-me"* ]] || [[ "$value" == *"your-"* ]]; then
        echo "❌ $var 未配置或使用默认值"
    else
        echo "✓ $var 已配置"
    fi
done

echo ""
echo "=== 环境变量摘要 ==="
grep -v "^#" .env | grep -v "^$" | while read line; do
    key=$(echo $line | cut -d'=' -f1)
    value=$(echo $line | cut -d'=' -f2)
    if [[ "$key" == *"SECRET"* ]] || [[ "$key" == *"PASS"* ]] || [[ "$key" == *"KEY"* ]]; then
        echo "$key=**** (隐藏)"
    else
        echo "$key=$value"
    fi
done
```

使用：
```bash
chmod +x check_env.sh
./check_env.sh
```

---

## 配置文件示例

### 开发环境 (.env.development)

```bash
# AI 服务
DASHSCOPE_API_KEY=sk-test-key-here
QWEN_MODEL=qwen-plus-latest
QWEN_VISION_MODEL=qwen-vl-plus

# 认证
JWT_SECRET=dev-secret-change-me
JWT_EXPIRE_MINUTES=10080

# 邮件 (开发环境可不配)
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=
SMTP_PASS=
SMTP_FROM_NAME=题小宝
SMTP_USE_TLS=true

# 管理员
ADMIN_PASSWORD=admin123

# CORS
ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 生产环境 (.env.production)

```bash
# AI 服务
DASHSCOPE_API_KEY=sk-your-production-api-key
QWEN_MODEL=qwen-max
QWEN_VISION_MODEL=qwen-vl-max

# 认证
JWT_SECRET=$(openssl rand -hex 32)
JWT_EXPIRE_MINUTES=1440

# 邮件
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASS=your-auth-code
SMTP_FROM_NAME=题小宝
SMTP_USE_TLS=true

# 管理员
ADMIN_PASSWORD=$(openssl rand -base64 16)

# CORS
ALLOW_ORIGINS=https://your-domain.com
```

---

## 故障排查

### 问题：API 调用失败

```bash
# 检查 API Key
echo $DASHSCOPE_API_KEY

# 测试连通性
curl -H "Authorization: Bearer $DASHSCOPE_API_KEY" https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

### 问题：验证码发送失败

```bash
# 检查 SMTP 配置
cat .env | grep SMTP

# 测试 SMTP 连接
telnet smtp.163.com 465

# 检查授权码是否正确
# 重新生成授权码并更新 .env
```

### 问题：Token 验证失败

```bash
# 检查 JWT_SECRET 是否一致
# 多实例部署时，确保所有实例使用相同的 JWT_SECRET

# 检查 Token 是否过期
# JWT_EXPIRE_MINUTES 设置是否合理
```

---

## 安全最佳实践

1. **永远不要提交 .env 到 Git**
   ```bash
   # .env 已在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **使用环境变量注入 (生产环境)**
   ```bash
   # systemd 服务中使用
   Environment="DASHSCOPE_API_KEY=your-key"
   ```

3. **定期轮换密钥**
   ```bash
   # 每月更换一次 JWT_SECRET
   # 每季度更换一次 ADMIN_PASSWORD
   ```

4. **使用密钥管理服务**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

---

*最后更新：2026-03-14*
