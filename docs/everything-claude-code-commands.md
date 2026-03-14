# Everything Claude Code 插件命令大全

**插件名称**: everything-claude-code
**版本**: 1.8.0
**描述**: AI 智能体性能优化系统，提供技能、记忆、持续学习、安全扫描等功能

---

## 快速开始

### 安装插件

```bash
# 添加市场源
/plugin marketplace add affaan-m/everything-claude-code

# 安装插件
/plugin install everything-claude-code@everything-claude-code
```

### 使用命令

```bash
# 插件安装后使用命名空间形式
/everything-claude-code:plan "添加用户认证"

# 或手动安装后可使用短形式
/plan "添加用户认证"
```

---

## 核心命令列表

### 开发与测试

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/tdd` | 测试驱动开发工作流 | `/tdd "添加登录功能"` |
| `/e2e` | 生成并运行 E2E 测试 | `/e2e "测试登录流程"` |
| `/code-review` | 代码质量审查 | `/code-review` |
| `/build-fix` | 修复构建错误 | `/build-fix` |
| `/refactor-clean` | 死代码清理 | `/refactor-clean` |
| `/test-coverage` | 测试覆盖率分析 | `/test-coverage` |

### 计划与设计

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/plan` | 实现计划制定 | `/plan "添加用户认证"` |
| `/multi-plan` | 多智能体任务分解 | `/multi-plan "重构整个认证模块"` |
| `/orchestrate` | 多智能体协调 | `/orchestrate "完成用户模块开发"` |

### 学习与知识管理

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/learn` | 会话中提取模式 | `/learn` |
| `/learn-eval` | 提取、评估并保存模式 | `/learn-eval` |
| `/instinct-status` | 查看已学习的 instincts | `/instinct-status` |
| `/instinct-import` | 导入 instincts | `/instinct-import file.md` |
| `/instinct-export` | 导出 instincts | `/instinct-export` |
| `/evolve` | 将 instincts 聚类为技能 | `/evolve` |
| `/skill-create` | 从 git 历史生成技能 | `/skill-create` |

### 文档与验证

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/update-docs` | 更新文档 | `/update-docs` |
| `/update-codemaps` | 更新代码地图 | `/update-codemaps` |
| `/verify` | 运行验证循环 | `/verify` |
| `/checkpoint` | 保存验证状态 | `/checkpoint` |
| `/eval` | 根据标准评估 | `/eval "代码符合 PEP 8"` |

### 多服务编排

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/pm2` | PM2 服务生命周期管理 | `/pm2 start` |
| `/multi-execute` | 多智能体协调执行 | `/multi-execute` |
| `/multi-backend` | 后端多服务编排 | `/multi-backend` |
| `/multi-frontend` | 前端多服务编排 | `/multi-frontend` |
| `/multi-workflow` | 通用多服务工作流 | `/multi-workflow` |

### 工具与配置

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/setup-pm` | 配置包管理器 | `/setup-pm pnpm` |
| `/sessions` | 会话历史管理 | `/sessions` |
| `/harness-audit` | 智能体 harness 审计 | `/harness-audit` |
| `/loop-start` | 启动循环任务 | `/loop-start 5m /verify` |
| `/loop-status` | 查看循环状态 | `/loop-status` |
| `/quality-gate` | 质量门控 | `/quality-gate` |
| `/model-route` | 模型路由配置 | `/model-route` |

---

## Go 语言特定命令

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/go-review` | Go 代码审查 | `/go-review` |
| `/go-test` | Go TDD 工作流 | `/go-test "添加 API 处理函数"` |
| `/go-build` | 修复 Go 构建错误 | `/go-build` |

---

## Python 语言特定命令

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/python-review` | Python 代码审查 | `/python-review` |

---

## 安全命令

| 命令 | 说明 | 使用示例 |
|------|------|----------|
| `/security-scan` | 安全漏洞扫描 | `/security-scan` |
| `/security-review` | 安全审查 | `/security-review` |

---

## 研究类技能

| 技能 | 说明 | 使用示例 |
|------|------|----------|
| `deep-research` | 多源深度研究 | `/everything-claude-code:deep-research "AI 教育应用"` |
| `exa-search` | Exa 神经搜索 | `/everything-claude-code:exa-search "最新 LLM 进展"` |
| `market-research` | 市场调研 | `/everything-claude-code:market-research "在线教育市场"` |

---

## 领域特定技能（部分）

### 前端
- `frontend-patterns` - React/Next.js 模式
- `frontend-slides` - HTML 演示文稿制作
- `liquid-glass-design` - iOS 26 液态玻璃设计系统

### 后端
- `backend-patterns` - API/数据库/缓存模式
- `postgres-patterns` - PostgreSQL 优化
- `docker-patterns` - Docker 容器化
- `springboot-patterns` - Spring Boot 架构
- `django-patterns` - Django 架构

### 测试
- `e2e-testing` - Playwright E2E 测试
- `python-testing` - Python pytest 测试
- `golang-testing` - Go 测试模式
- `kotlin-testing` - Kotlin 测试

### 内容创作
- `article-writing` - 长文写作
- `content-engine` - 多平台内容生成
- `investor-materials` - 投资人材料
- `investor-outreach` - 投资人联络

---

## 可用智能体 (Agents)

| 智能体 | 用途 |
|--------|------|
| `planner` | 功能实现计划 |
| `architect` | 系统设计决策 |
| `tdd-guide` | 测试驱动开发 |
| `code-reviewer` | 代码质量审查 |
| `security-reviewer` | 安全漏洞分析 |
| `build-error-resolver` | 构建错误修复 |
| `e2e-runner` | Playwright E2E 测试 |
| `refactor-cleaner` | 死代码清理 |
| `doc-updater` | 文档更新 |
| `database-reviewer` | 数据库审查 |

---

## 使用建议

### 何时使用哪个智能体

1. **开始新功能** → 先用 `/plan` 制定计划
2. **写代码** → 用 `/tdd` 测试驱动开发
3. **代码完成后** → 用 `/code-review` 审查
4. **构建失败** → 用 `/build-fix` 修复
5. **准备提交前** → 用 `/verify` 验证
6. **安全相关代码** → 用 `/security-review` 审查

### 最佳实践

1. **计划先行**: 复杂功能先用 `/plan` 生成分步计划
2. **测试第一**: 始终用 `/tdd` 先写测试
3. **及时审查**: 代码完成后立即用 `/code-review`
4. **持续学习**: 会话结束前用 `/learn-eval` 保存经验

---

## 注意事项

### 规则安装

插件不自动分发 rules，需手动安装：

```bash
# 克隆仓库
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code

# 安装规则 (选择需要的语言)
./install.sh typescript    # TypeScript/JavaScript
./install.sh python        # Python
./install.sh golang        # Go
./install.sh swift         # Swift
./install.sh php           # PHP
```

### 版本要求

- **Claude Code CLI**: v2.1.0 或更高版本

---

## 相关资源

- **GitHub**: https://github.com/affaan-m/everything-claude-code
- **简短指南**: https://x.com/affaanmustafa/status/2012378465664745795
- **详细指南**: https://x.com/affaanmustafa/status/2014040193557471352
- **AgentShield 安全扫描**: https://github.com/affaan-m/agentshield

---

*文档最后更新：2026-03-14*
