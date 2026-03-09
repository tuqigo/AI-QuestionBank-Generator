# Cloudflare Pages 部署指南

## 前提条件

1. 拥有 Cloudflare 账号
2. 后端服务需要部署在公网可访问的地址（如 Railway、Render、云服务器等）

## 部署步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 本地开发

由于 Cloudflare Functions 需要后端服务，本地开发时：

1. 启动后端服务：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端（使用 Vite 原生代理）：
```bash
cd frontend
npm run dev
```

### 3. 部署到 Cloudflare Pages

#### 方法一：使用 Wrangler CLI（推荐）

1. 登录 Cloudflare：
```bash
npx wrangler login
```

2. 部署项目：
```bash
npx wrangler pages deploy dist --project-name=zyb-frontend --commit-dirty=true
```

3. 设置环境变量（在 Cloudflare Dashboard）：
   - 进入项目页面
   - Settings → Functions → Environment Variables
   - 添加 `BACKEND_URL` = 你的后端地址

#### 方法二：使用 Cloudflare Dashboard（Direct Upload）

适用于不使用 Git 仓库，直接上传构建文件的场景。

1. **构建项目（包含 Functions）**
   ```bash
   cd frontend
   npm install
   # 使用 build:cf 命令，会自动编译 functions 到 _worker.js
   npm run build:cf
   ```
   构建完成后，`dist` 目录包含：
   - `index.html` 等静态资源
   - `assets/` 目录
   - `_worker.js`（Cloudflare Functions，处理 API 代理）

2. **创建 Pages 项目**
   - 访问 https://pages.cloudflare.com
   - 点击 "Create a project"
   - 选择 **"Direct Upload"**（不是 "Connect to Git"）

3. **上传构建文件**
   - 将 `dist` 目录中的**所有文件和文件夹**（包括 `_worker.js` 和 `assets`）拖拽到上传区域
   - 或者点击 "Select files" 选择 `dist` 目录下的所有文件
   - 点击 "Deploy"

4. **配置环境变量**
   - 部署完成后，进入项目页面
   - 点击 "Settings" > "Functions" > "Environment Variables"
   - 点击 "Add variable"
   - 添加：
     - Variable name: `BACKEND_URL`
     - Value: 你的后端服务地址（如 `https://api.yourdomain.com`）
   - 点击 "Save"

5. **重新部署（应用环境变量）**
   - 回到 "Deployments" 标签页
   - 点击最新部署右侧的 "..." > "Redeploy"

### 4. 自定义域名（可选）

在 Cloudflare Pages Dashboard 中绑定自定义域名。

---

## 后续代码修改后的部署流程

每次修改前端代码或 Functions 后，需要重新构建并部署：

### 使用 Wrangler CLI 部署（推荐）

```bash
cd frontend

# 1. 重新构建项目
npm run build:cf

# 2. 部署到 Cloudflare Pages
npx wrangler pages deploy dist --project-name=zyb-frontend --commit-dirty=true
```

部署完成后会输出新的预览 URL，访问该 URL 即可看到更新。

### 使用 Direct Upload 部署

```bash
cd frontend

# 1. 重新构建项目
npm run build:cf

# 2. 生成 zip 文件（可选，方便上传）
# Windows PowerShell:
Compress-Archive -Path dist\* -DestinationPath dist.zip -Force
```

然后登录 Cloudflare Dashboard：
1. 进入你的 Pages 项目
2. 点击 "Deployments" → "Create new deployment" 或直接上传
3. 上传 `dist` 目录的所有内容（或 `dist.zip`）
4. 等待部署完成

### 注意事项

- **每次代码修改后都需要重新构建**：`npm run build:cf` 会同时构建 Vite 项目和 Cloudflare Functions
- **环境变量修改后需要重新部署**：在 Dashboard 修改 `BACKEND_URL` 后，点击 "Redeploy" 使变更生效
- **浏览器缓存**：部署后如果看不到更新，使用 `Ctrl+Shift+R` 强制刷新清除缓存

---

## 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `BACKEND_URL` | 后端 API 服务地址 | `https://zuoyebang.092201.xyz` |

**设置方式**：
1. Cloudflare Dashboard → 你的 Pages 项目 → Settings
2. Functions → Environment Variables
3. 点击 "Add variable"
4. 添加 `BACKEND_URL`，值为你的后端地址
5. 保存后点击 "Redeploy" 使环境变量生效

## 注意事项

1. **CORS**: Functions 已配置 CORS 头，支持跨域请求
2. **认证**: JWT token 会通过 Authorization 头正常传递到后端
3. **请求限制**: Cloudflare Pages Functions 有 10ms CPU 时间和 15 分钟总执行时间限制
4. **后端地址**: 后端必须部署在公网可访问的 HTTPS 地址

## 后端部署建议

推荐将后端部署到以下平台：

- **Railway** (https://railway.app) - 免费额度，支持 Docker
- **Render** (https://render.com) - 免费套餐
- **Fly.io** - 免费额度
- **云服务器** - 任何支持 HTTPS 的服务器

确保后端启用 HTTPS，因为 Cloudflare Pages 只支持 HTTPS 后端。

## 故障排查

### API 请求失败

1. 检查 `BACKEND_URL` 环境变量是否正确设置
2. 确保后端服务可公开访问且使用 HTTPS
3. 查看 Cloudflare Pages 的 Functions 日志

### 构建失败

```bash
# 本地测试构建
npm run build
```

### CORS 错误

检查后端 CORS 配置，确保允许来自 `*.pages.dev` 域名的请求。
