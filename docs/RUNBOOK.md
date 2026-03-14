# 运行手册 (Runbook)

> 题小宝 AI 题库生成器 运维指南

---

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   前端      │────▶│   后端       │────▶│  通义千问   │
│ React+Vite  │     │  FastAPI     │     │   DashScope │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   SQLite     │
                    │   数据库     │
                    └──────────────┘
```

---

## 部署清单

### 生产环境要求

| 资源 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 1 Core | 2+ Cores |
| 内存 | 512 MB | 2+ GB |
| 磁盘 | 1 GB | 5+ GB |
| 带宽 | 1 Mbps | 5+ Mbps |

### 依赖服务

- [ ] 通义千问 API Key (DashScope)
- [ ] SMTP 邮件服务 (163/Gmail/QQ)
- [ ] HTTPS 证书 (推荐使用 Let's Encrypt)
- [ ] 域名 (可选，用于生产访问)

---

## 部署步骤

### 1. 服务器准备

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python 3.8+
apt install python3 python3-pip python3-venv -y

# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y

# 安装 Nginx (可选，用于反向代理)
apt install nginx -y
```

### 2. 部署后端

```bash
# 克隆项目
git clone https://github.com/your-username/AI-QuestionBank-Generator.git
cd AI-QuestionBank-Generator

# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入生产配置

# 启动服务 (开发环境)
uvicorn main:app --host 0.0.0.0 --port 8000

# 启动服务 (生产环境 - 使用 Gunicorn)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. 部署前端

```bash
cd frontend

# 安装依赖
npm install

# 生产构建
npm run build

# 部署到 Cloudflare Pages
npm run deploy
```

### 4. 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/AI-QuestionBank-Generator/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 测试配置
nginx -t

# 重载 Nginx
systemctl reload nginx
```

### 5. 配置 HTTPS (可选)

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期 (已添加到 cron)
certbot renew --dry-run
```

### 6. 配置 systemd 服务 (开机自启)

```bash
# 创建服务文件
cat > /etc/systemd/system/tixiaobao.service <<EOF
[Unit]
Description=题小宝 AI 题库生成器后端服务
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/AI-QuestionBank-Generator/backend
Environment="PATH=/path/to/AI-QuestionBank-Generator/backend/venv/bin"
ExecStart=/path/to/AI-QuestionBank-Generator/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable tixiaobao
systemctl start tixiaobao

# 查看状态
systemctl status tixiaobao
```

---

## 健康检查

### 端点检查

```bash
# API 根端点
curl http://localhost:8000
# 预期返回：{"message": "题小宝 API"}

# API 文档
curl http://localhost:8000/docs

# 健康检查 (需自行添加端点)
curl http://localhost:8000/health
```

### 服务状态检查

```bash
# 后端服务状态
systemctl status tixiaobao

# Nginx 状态
systemctl status nginx

# 查看日志
journalctl -u tixiaobao -f
```

### 日志检查

```bash
# 后端日志
tail -f /path/to/AI-QuestionBank-Generator/backend/logs/api.log
tail -f /path/to/AI-QuestionBank-Generator/backend/logs/auth.log
tail -f /path/to/AI-QuestionBank-Generator/backend/logs/qwen.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log
```

---

## 监控告警

### 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| API 响应时间 | > 3s | 警告 |
| API 错误率 | > 5% | 严重 |
| 磁盘使用率 | > 80% | 警告 |
| 内存使用率 | > 90% | 严重 |
| CPU 使用率 | > 90% | 警告 |

### 监控方案

**方案一：Prometheus + Grafana**
```bash
# 安装 Prometheus
# 安装 Grafana
# 配置 FastAPI Prometheus Exporter
pip install prometheus-client
```

**方案二：第三方监控**
- 监控易
- 听云
- OneAPM

---

## 常见问题处理

### 1. 服务无法启动

**症状：** 访问 `http://localhost:8000` 失败

**排查步骤：**
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查服务状态
systemctl status tixiaobao

# 查看日志
journalctl -u tixiaobao -n 50

# 检查防火墙
ufw status
```

**解决方案：**
```bash
# 重启服务
systemctl restart tixiaobao

# 或手动启动
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. API 响应缓慢

**症状：** API 响应时间超过 3 秒

**排查步骤：**
```bash
# 检查 CPU/内存
top -p $(pgrep -f gunicorn)

# 检查网络延迟
ping dashscope.aliyuncs.com

# 检查通义千问 API 状态
curl -v https://dashscope.aliyuncs.com
```

**解决方案：**
- 增加 Gunicorn worker 数量
- 优化数据库查询
- 添加缓存层 (Redis)

### 3. 验证码发送失败

**症状：** 用户无法收到邮箱验证码

**排查步骤：**
```bash
# 检查 SMTP 配置
cat backend/.env | grep SMTP

# 测试 SMTP 连接
telnet smtp.163.com 465

# 查看认证日志
tail -f backend/logs/auth.log
```

**解决方案：**
```bash
# 验证 SMTP 凭据
# 检查邮箱授权码是否正确
# 确认防火墙放行 SMTP 端口

# 临时方案：切换到其他 SMTP 服务商
```

### 4. 题目生成失败

**症状：** 提示词提交后返回 500 错误

**排查步骤：**
```bash
# 检查 API Key
cat backend/.env | grep DASHSCOPE

# 测试 DashScope 连通性
python -c "import dashscope; print(dashscope.Generation.call('qwen-plus', 'hello'))"

# 查看 Qwen 日志
tail -f backend/logs/qwen.log
```

**解决方案：**
```bash
# 确认 API Key 有效且未欠费
# 检查网络连接
# 增加请求超时时间
```

### 5. 数据库锁定

**症状：** 写入操作失败，提示 "database is locked"

**排查步骤：**
```bash
# 检查数据库文件
ls -la backend/data/*.db

# 查看进程占用
lsof backend/data/*.db
```

**解决方案：**
```bash
# 备份数据库
cp backend/data/main.db backend/data/main.db.backup

# 优化 SQLite 配置 (在 config.py 中添加)
# PRAGMA journal_mode=WAL;
# PRAGMA busy_timeout=5000;

# 长期方案：迁移到 PostgreSQL
```

---

## 回滚流程

### 快速回滚到上一版本

```bash
# 1. 查看 Git 历史
git log --oneline -n 5

# 2. 停止服务
systemctl stop tixiaobao

# 3. 回滚代码
git reset --hard <previous-commit-hash>

# 4. 恢复依赖
cd backend
pip install -r requirements.txt

# 5. 启动服务
systemctl start tixiaobao

# 6. 验证
curl http://localhost:8000
```

### 数据库回滚

```bash
# 备份当前数据库
cp backend/data/main.db backend/data/main.db.backup.$(date +%Y%m%d)

# 恢复旧备份
cp backend/data/main.db.backup.YYYYMMDD backend/data/main.db

# 重启服务
systemctl restart tixiaobao
```

---

## 备份策略

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/tixiaobao"

# 备份数据库
cp backend/data/*.db $BACKUP_DIR/db_$DATE

# 备份日志
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz backend/logs/

# 备份配置
cp backend/.env $BACKUP_DIR/env_$DATE

# 清理 30 天前的备份
find $BACKUP_DIR -mtime +30 -delete

echo "备份完成：$DATE"
```

### 定时任务

```bash
# 添加到 crontab (每天凌晨 2 点)
crontab -e
0 2 * * * /path/to/backup.sh
```

---

## 容量规划

### 当前容量

| 资源 | 使用量 | 总量 | 使用率 |
|------|--------|------|--------|
| 用户数 | - | - | - |
| 题目记录 | - | - | - |
| 数据库 | - | - | - |

### 扩容阈值

当达到以下阈值时考虑扩容：

- 数据库文件 > 500MB
- 日均 API 请求 > 100,000
- 活跃用户 > 1,000

### 扩容方案

1. **垂直扩容**：升级服务器配置
2. **水平扩容**：添加负载均衡 + 多实例
3. **数据库迁移**：SQLite → PostgreSQL
4. **添加缓存**：Redis 缓存热点数据

---

## 紧急联系方式

| 角色 | 联系人 | 电话 | 邮箱 |
|------|--------|------|------|
| 运维负责人 | - | - | - |
| 开发负责人 | - | - | - |
| 产品负责人 | - | - | - |

---

*最后更新：2026-03-14*
