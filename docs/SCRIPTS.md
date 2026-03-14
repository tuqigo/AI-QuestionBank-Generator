# 脚本命令参考

> 本项目可用的脚本命令和快捷操作

---

## 前端命令 (frontend/package.json)

| 命令 | 说明 | 使用场景 |
|------|------|----------|
| `npm run dev` | 启动 Vite 开发服务器，支持热重载 | 本地开发调试 |
| `npm run build` | TypeScript 类型检查 + Vite 生产构建 | 生产环境部署 |
| `npm run build:cf` | 使用 Cloudflare Workers 构建脚本 | Cloudflare 部署 |
| `npm run preview` | 预览生产构建结果 | 部署前验证 |
| `npm run deploy` | 构建并部署到 Cloudflare Pages | CI/CD 自动部署 |

### 命令详解

#### `npm run dev`

启动开发服务器：

```bash
cd frontend
npm run dev
```

默认访问：`http://localhost:5173`

#### `npm run build`

生产构建：

```bash
cd frontend
npm run build
# 输出目录：dist/
```

#### `npm run deploy`

部署到 Cloudflare Pages：

```bash
cd frontend
npm run deploy
```

需要配置 `wrangler.toml` 和 Cloudflare 认证。

---

## 前端架构说明

### 双模式渲染

前端支持**屏幕渲染**和**打印输出**两种模式：

- **渲染模式** (`render`): 用于浏览器预览，包含丰富的视觉效果
- **打印模式** (`print`): 用于打印/PDF 导出，布局紧凑

### 题目组件位置

| 组件 | 路径 | 说明 |
|------|------|------|
| QuestionRenderer | `src/components/QuestionRenderer.tsx` | 题目渲染入口 |
| StructuredPreviewShared | `src/components/StructuredPreviewShared.tsx` | 预览/分享通用组件 |
| 单选题 | `src/components/questions/SingleChoice.tsx` | 单选题渲染 |
| 多选题 | `src/components/questions/MultipleChoice.tsx` | 多选题渲染 |
| 判断题 | `src/components/questions/TrueFalse.tsx` | 判断题渲染 |
| 填空题 | `src/components/questions/FillBlank.tsx` | 填空题渲染 |
| 计算题 | `src/components/questions/Calculation.tsx` | 计算题渲染 |
| 应用题 | `src/components/questions/WordProblem.tsx` | 应用题渲染 |
| 阅读理解 | `src/components/questions/ReadComp.tsx` | 阅读理解渲染 |
| 完形填空 | `src/components/questions/Cloze.tsx` | 完形填空渲染 |
| 作文 | `src/components/questions/Essay.tsx` | 作文渲染 |

### 打印功能

打印功能由 `src/utils/printUtils.ts` 提供：

```typescript
import { handlePrint } from '@/utils/printUtils'

// 调用打印
await handlePrint(
  undefined,           // markdown (可选，向后兼容)
  title,               // 试卷标题
  questions,           // 结构化题目数据
  null                 // 答案 (可选)
)
```

---

## 后端命令

### 基础命令

| 命令 | 说明 |
|------|------|
| `uvicorn main:app --reload` | 开发模式启动，支持热重载 |
| `uvicorn main:app --host 0.0.0.0 --port 8000` | 生产模式启动 |
| `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker` | Gunicorn 多 worker 模式 |

### 开发调试

```bash
cd backend

# 虚拟环境激活
source venv/bin/activate  # Windows: venv\Scripts\activate

# 开发模式启动
uvicorn main:app --reload --log-level debug

# 查看 API 文档
# 浏览器访问 http://localhost:8000/docs
```

### 生产部署

```bash
cd backend

# 安装 Gunicorn
pip install gunicorn

# 多 worker 启动 (4 个 worker)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或 systemd 托管
systemctl start tixiaobao
```

---

## Git 命令

| 命令 | 说明 |
|------|------|
| `git checkout -b feature/xxx` | 创建功能分支 |
| `git commit -m "feat: xxx"` | 提交新功能 |
| `git commit -m "fix: xxx"` | 提交 Bug 修复 |
| `git push origin feature/xxx` | 推送分支 |
| `git tag v1.0.0` | 打版本标签 |

---

## 数据库操作

### SQLite (当前)

```bash
cd backend

# 查看数据库文件
ls -la data/*.db

# 使用 SQLite CLI
sqlite3 data/main.db

# 查看表
.tables

# 查看数据
SELECT * FROM users LIMIT 10;
SELECT * FROM question_records ORDER BY created_at DESC LIMIT 10;
```

### 迁移到 PostgreSQL (未来)

```bash
# 安装 PostgreSQL 适配器
pip install psycopg2-binary

# 更新数据库连接 (config.py)
# DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

---

## 日志查看

```bash
# 后端 API 日志
tail -f backend/logs/api.log

# 认证日志
tail -f backend/logs/auth.log

# Qwen API 日志
tail -f backend/logs/qwen.log

# 实时跟踪
tail -f backend/logs/*.log
```

---

## 系统维护

### 清理临时文件

```bash
# Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node 缓存
cd frontend
rm -rf node_modules/.cache
```

### 依赖更新

```bash
# Python 依赖
cd backend
pip install --upgrade -r requirements.txt

# Node 依赖
cd frontend
npm update
```

### 数据库备份

```bash
# 手动备份
cp backend/data/main.db backend/data/main.db.backup.$(date +%Y%m%d)

# 恢复备份
cp backend/data/main.db.backup.YYYYMMDD backend/data/main.db
```

---

## 故障排查命令

### 网络检查

```bash
# 测试后端 API
curl http://localhost:8000

# 测试通义千问 API
curl -v https://dashscope.aliyuncs.com

# 测试 SMTP
telnet smtp.163.com 465
```

### 进程检查

```bash
# 查看 Python 进程
ps aux | grep python

# 查看端口占用
netstat -tlnp | grep 8000
netstat -tlnp | grep 5173

# 查看文件句柄
lsof -i :8000
```

### 资源检查

```bash
# CPU/内存
top -p $(pgrep -f gunicorn)

# 磁盘使用
df -h
du -sh backend/data/*
du -sh frontend/dist/*
```

---

## 环境变量检查

```bash
# 查看当前环境变量
cat backend/.env | grep -v "^#"

# 验证必要变量
echo "DASHSCOPE_API_KEY: $DASHSCOPE_API_KEY"
echo "JWT_SECRET: $JWT_SECRET"
```

---

## API 测试

### 使用 curl 测试

```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 获取当前用户
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# 生成题目
curl -X POST http://localhost:8000/api/questions/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt":"生成三年级数学练习题"}'
```

### 使用 HTTPie 测试 (更友好)

```bash
# 安装
pip install httpie

# 登录
http POST :8000/api/auth/login email=test@example.com password=password123

# 获取用户信息
http GET :8000/api/auth/me Authorization:"Bearer YOUR_TOKEN"

# 生成题目
http POST :8000/api/questions/generate prompt="生成三年级数学练习题" Authorization:"Bearer YOUR_TOKEN"
```

---

*最后更新：2026-03-14*
