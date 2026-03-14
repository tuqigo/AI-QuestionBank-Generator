# 贡献指南

> 欢迎为 **题小宝 AI 题库生成器** 项目做出贡献！

## 开发环境设置

### 前置要求

- Python 3.8+
- Node.js 18+
- Git

### 克隆项目

```bash
git clone https://github.com/your-username/AI-QuestionBank-Generator.git
cd AI-QuestionBank-Generator
```

### 后端设置

```bash
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 填入必要的配置
# - DASHSCOPE_API_KEY: 通义千问 API Key
# - JWT_SECRET: 随机字符串作为密钥
```

### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务
npm run dev
```

---

## 代码风格

### Python 后端

遵循 [PEP 8](https://pep8.org/) 编码规范：

- 使用 4 空格缩进
- 函数和变量使用 `snake_case`
- 类使用 `PascalCase`
- 添加类型注解
- 编写 docstring

```python
def generate_questions(prompt: str, user_id: int) -> Tuple[str, str]:
    """生成题目并返回标题和 Markdown 内容"""
    pass
```

### TypeScript 前端

遵循项目 ESLint 配置：

- 使用 2 空格缩进
- 使用单引号
- 箭头函数优先
- 添加类型定义

```typescript
interface GenerateResponse {
  title: string;
  markdown: string;
  record_id?: number;
}
```

#### 题目组件开发规范

前端采用**双模式渲染架构**，支持屏幕显示和打印输出两种模式：

**1. 模式定义**

```typescript
type RenderMode = 'render' | 'print'
```

- `render` - 屏幕渲染模式：包含背景色、圆角边框、较大间距等视觉效果
- `print` - 打印输出模式：紧凑布局、无背景色、适合 PDF 导出

**2. CSS 变量系统**

通过 CSS 变量控制两种模式的样式差异：

```css
/* 渲染模式 */
.question-render-mode {
  --question-padding: 16px;
  --option-background: #fafafa;
  --question-border: 1px solid #e0e0e0;
}

/* 打印模式 */
.question-print-mode {
  --question-padding: 0;
  --option-background: transparent;
  --question-border: none;
}
```

**3. 组件 Props 规范**

所有题目组件必须支持 `mode` prop：

```typescript
interface QuestionProps {
  question: StructuredQuestion
  index: number
  mode?: 'render' | 'print'
}
```

**4. 配置中心**

题型配置统一在 `src/config/questionConfig.ts` 管理：

```typescript
export interface QuestionTypeConfig {
  showAnswerArea: boolean
  answerAreaType: 'none' | 'blank' | 'lined' | 'grid'
  optionLayout: 'horizontal' | 'vertical'
  // ...
}
```

---

## 提交流程

### 1. 创建分支

```bash
# 基于 main 创建功能分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/bug-description
```

### 2. 开发与测试

- 确保本地测试通过
- 后端 API 使用 `http://localhost:8000/docs` 测试
- 前端在 `http://localhost:5173` 验证

### 3. 提交代码

提交信息遵循 [约定式提交](https://www.conventionalcommits.org/)：

```bash
git commit -m "feat: 添加新的题型支持"
git commit -m "fix: 修复验证码发送失败问题"
git commit -m "docs: 更新 API 文档"
git commit -m "refactor: 重构用户认证逻辑"
git commit -m "test: 添加题目生成测试"
```

**类型说明：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

### 4. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

在 GitHub 上创建 Pull Request，填写：
- 变更说明
- 测试步骤
- 相关 Issue 链接

---

## 测试

### 后端测试

```bash
cd backend

# 运行测试 (如有)
pytest

# 代码检查
python -m flake8 .
python -m mypy .
```

### 前端测试

```bash
cd frontend

# 类型检查
npm run build

# 代码检查 (如有配置 ESLint)
npm run lint
```

---

## 目录规范

### 添加新的路由

```bash
# 1. 创建路由文件
touch backend/routers/new_feature.py

# 2. 定义路由
from fastapi import APIRouter
router = APIRouter(prefix="/api/new-feature", tags=["new_feature"])

# 3. 在 main.py 注册
# app.include_router(new_feature.router)
```

### 添加新的服务

```bash
# 1. 创建服务文件
touch backend/services/new_service.py

# 2. 实现业务逻辑
def new_feature_logic():
    pass
```

### 添加新的模型

```bash
# 1. 创建模型文件
touch backend/models/new_model.py

# 2. 定义数据模型
from pydantic import BaseModel

class NewModel(BaseModel):
    id: int
    name: str
```

---

## 发布流程

### 版本号规范

遵循 [语义化版本](https://semver.org/)：

- `MAJOR.MINOR.PATCH` (如 1.2.3)
- 不兼容变更：`MAJOR++`
- 向后兼容功能：`MINOR++`
- Bug 修复：`PATCH++`

### 发布步骤

1. 更新版本号 (如有配置)
2. 更新 CHANGELOG.md
3. 创建 Git Tag
4. 发布 GitHub Release

```bash
git tag v1.2.3
git push origin v1.2.3
```

---

## 问题反馈

### Bug 报告

创建 Issue 时请包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息 (OS, Python/Node 版本)
- 日志或截图

### 功能建议

创建 Issue 时请包含：
- 功能描述
- 使用场景
- 预期效果

---

## 联系方式

- GitHub Issues: [项目 Issue 页](https://github.com/your-username/AI-QuestionBank-Generator/issues)
- 邮箱：your-email@example.com

---

## 许可证

MIT License - 参见 [LICENSE](../LICENSE) 文件

---

*最后更新：2026-03-14*
