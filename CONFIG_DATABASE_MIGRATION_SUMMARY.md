# 配置数据结构数据库化改造 - 完成总结

## 改造概述

成功将 `backend/core/constants.py` 中硬编码的配置数据迁移到数据库表，实现了配置数据的动态管理。

**最新简化** (2026-03-17): 删除知识点分组表和题型关联表，改为扁平结构存储。

---

## 完成的工作

### 一、数据库迁移（已完成）

#### 1. 迁移脚本

| 迁移文件 | 说明 |
|---------|------|
| `018_create_config_tables.sql` | 创建配置表并初始化基础数据 |
| `019_migrate_template_foreign_keys.sql` | 为 `question_templates` 表添加外键列 |
| `020_simplify_knowledge_points.sql` | **简化结构：删除分组表，改为扁平存储** |
| `migrate_knowledge_points.py` | Python 脚本，将 constants.py 中的 KNOWLEDGE_POINTS 数据迁移到数据库 |

#### 2. 当前数据库表结构

**配置表**:
| 表名 | 说明 | 记录数 |
|------|------|--------|
| `subjects` | 学科表 | 3 |
| `grades` | 年级表 | 9 |
| `semesters` | 学期表 | 2 |
| `textbook_versions` | 教材版本表 | 10 |
| `knowledge_points` | 知识点表（扁平结构） | 43 |
| `question_types` | 题型表（subjects 逗号分隔） | 10 |

**已删除的表**:
- `knowledge_point_groups` - 知识点分组表（已删除，改为扁平结构）
- `question_type_subjects` - 题型学科关联表（已删除，改为逗号分隔存储）

#### 3. 扁平结构设计

**knowledge_points 表结构**:
```sql
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject_code TEXT NOT NULL,          -- 学科代码
    grade_code TEXT NOT NULL,            -- 年级代码
    semester_code TEXT NOT NULL,         -- 学期代码
    textbook_version_code TEXT NOT NULL, -- 教材版本代码
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**question_types 表结构**:
```sql
CREATE TABLE question_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_name TEXT UNIQUE NOT NULL,
    zh_name TEXT NOT NULL,
    subjects TEXT NOT NULL DEFAULT 'math,chinese,english',  -- 逗号分隔
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. schema.sql 主文件

所有 CREATE TABLE 语句已移至 `backend/db/schema.sql`:
- `knowledge_points` - 知识点表（扁平结构）
- `question_types` - 题型表（subjects 字段）
- `question_templates` - 题目模板表（含 `knowledge_point_id` 外键）

迁移脚本仅处理数据迁移和表删除操作。

---

### 二、后端服务层（已完成）

#### 1. 数据模型 (`backend/models/config.py`)

**扁平结构模型**:
```python
class KnowledgePointBase(BaseModel):
    name: str
    subject_code: str
    grade_code: str
    semester_code: str
    textbook_version_code: str
    sort_order: int = 0
```

**题型模型** (自动解析逗号分隔字符串):
```python
class QuestionTypeInDB(BaseModel):
    id: int
    en_name: str
    zh_name: str
    subjects: str  # 数据库中是逗号分隔的字符串

    @field_validator('subjects', mode='before')
    @classmethod
    def parse_subjects(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(',') if s.strip()]
        return ["math", "chinese", "english"]
```

#### 2. 数据访问服务 (`backend/services/config/`)

| 服务文件 | 说明 |
|---------|------|
| `subject_store.py` | 学科数据访问（CRUD + 选项列表） |
| `grade_store.py` | 年级数据访问 |
| `semester_store.py` | 学期数据访问 |
| `textbook_version_store.py` | 教材版本数据访问 |
| `knowledge_point_store.py` | 知识点数据访问（扁平结构，支持条件筛选） |

**知识点筛选示例**:
```python
KnowledgePointStore.get_by_filters(
    subject_code='math',
    grade_code='grade1',
    semester_code='upper',
    textbook_version_code='rjb'
)
```

#### 3. API 路由 (`backend/api/v1/configs.py`)

**公共接口**:
| 接口 | 说明 |
|------|------|
| `GET /api/configs/configs` | 获取所有配置（保持向后兼容） |
| `GET /api/configs/subjects` | 获取学科列表 |
| `GET /api/configs/grades` | 获取年级列表 |
| `GET /api/configs/semesters` | 获取学期列表 |
| `GET /api/configs/textbook-versions` | 获取教材版本列表 |
| `GET /api/configs/knowledge-points` | 获取知识点列表（支持筛选） |
| `GET /api/configs/question-types` | 获取题型列表（含 subjects） |

**管理端接口**:
| 接口 | 说明 |
|------|------|
| `POST /api/configs/admin/subjects/create` | 创建学科 |
| `PUT /api/configs/admin/subjects/{id}/update` | 更新学科 |
| `DELETE /api/configs/admin/subjects/{id}/delete` | 删除学科（软删除） |
| `POST /api/configs/admin/knowledge-points/create` | 创建知识点 |
| `PUT /api/configs/admin/knowledge-points/{id}/update` | 更新知识点 |
| `DELETE /api/configs/admin/knowledge-points/{id}/delete` | 删除知识点（软删除） |

**已移除的接口**:
- `GET /api/configs/knowledge-point-groups` - 知识点分组接口（已删除）
- `POST /api/configs/admin/knowledge-point-groups/create` - 创建分组接口（已删除）

#### 4. 题型服务 (`backend/services/question/question_type_store.py`)

```python
@staticmethod
def get_all_with_subjects() -> List[Dict[str, Any]]:
    """获取所有题型及其关联的学科列表"""
    # 从 subjects 字段解析学科列表（逗号分隔）
    subjects_str = qt_dict.get('subjects', 'math,chinese,english')
    subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
```

---

### 三、前端实现（已完成）

#### 1. 类型定义 (`frontend/src/api/config.ts`)

**扁平结构接口**:
```typescript
export interface KnowledgePoint {
  id: number
  name: string
  subject_code: string
  grade_code: string
  semester_code: string
  textbook_version_code: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface KnowledgePointCreate {
  name: string
  subject_code: string
  grade_code: string
  semester_code: string
  textbook_version_code: string
  sort_order: number
}
```

**已移除的类型**:
- `KnowledgePointGroup` - 知识点分组类型
- `KnowledgePointGroupCreate` - 创建分组请求体

**API 函数**:
```typescript
// 获取知识点列表（支持筛选）
export async function getKnowledgePoints(params?: {
  subject_code?: string
  grade_code?: string
  semester_code?: string
  textbook_version_code?: string
}): Promise<KnowledgePoint[]>

// 创建知识点（扁平结构）
export async function createKnowledgePoint(data: KnowledgePointCreate): Promise<KnowledgePoint>
```

#### 2. 配置管理页面 (`frontend/src/admin/pages/ConfigsPage.tsx`)

**Tab 切换**:
- 学科配置
- 年级配置
- 学期配置
- 教材版本
- **知识点配置**（原"知识点分组"，已简化）

**知识点列表展示**:
```tsx
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>知识点名称</th>
      <th>学科</th>
      <th>年级</th>
      <th>学期</th>
      <th>教材版本</th>
      <th>排序</th>
      <th>状态</th>
      <th>操作</th>
    </tr>
  </thead>
  <tbody>
    {knowledgePoints.map((point) => (...))}
  </tbody>
</table>
```

**创建知识点表单**:
- 学科选择（数学/语文/英语）
- 年级选择（一年级 ~ 九年级）
- 学期选择（上学期/下学期）
- 教材版本选择（人教版/北师大版等）
- 知识点名称输入
- 排序输入

#### 3. 样式文件 (`frontend/src/admin/pages/ConfigsPage.css`)

- 响应式布局
- 标签页样式
- 弹窗样式
- 表单样式

#### 4. 路由配置 (`frontend/src/admin/App.tsx`)

- 新增 `/admin/configs` 路由
- 侧边栏导航菜单添加"配置管理"入口

#### 5. 构建验证

```bash
✓ 189 modules transformed.
dist/index.html                  1.59 kB │ gzip:   0.88 kB
dist/assets/index-CpuPPjBB.css  101.04 kB │ gzip:  17.17 kB
dist/assets/index-CeV4Eb3W.js   499.36 kB │ gzip: 157.55 kB
✓ built in 1.66s
```

---

## 文件清单

### 后端文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `backend/db/schema.sql` | **主表结构定义（扁平结构）** | ✅ |
| `backend/db/migrations/018_create_config_tables.sql` | 配置表创建迁移 | ✅ |
| `backend/db/migrations/019_migrate_template_foreign_keys.sql` | 外键迁移 | ✅ |
| `backend/db/migrations/020_simplify_knowledge_points.sql` | **简化结构迁移** | ✅ |
| `backend/db/migrations/migrate_knowledge_points.py` | 知识点数据迁移脚本 | ✅ |
| `backend/models/config.py` | Pydantic 数据模型（扁平结构） | ✅ |
| `backend/services/config/subject_store.py` | 学科数据访问 | ✅ |
| `backend/services/config/grade_store.py` | 年级数据访问 | ✅ |
| `backend/services/config/semester_store.py` | 学期数据访问 | ✅ |
| `backend/services/config/textbook_version_store.py` | 教材版本数据访问 | ✅ |
| `backend/services/config/knowledge_point_store.py` | 知识点数据访问（扁平结构） | ✅ |
| `backend/services/config/__init__.py` | 包导出 | ✅ |
| `backend/api/v1/configs.py` | API 路由（简化后） | ✅ |
| `backend/core/constants.py` | 常量 fallback | ✅ |
| `backend/services/question/question_type_store.py` | 题型服务（subjects 逗号分隔） | ✅ |

### 前端文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `frontend/src/api/config.ts` | API 调用 + 类型定义（扁平结构） | ✅ |
| `frontend/src/admin/pages/ConfigsPage.tsx` | 配置管理页面（简化后） | ✅ |
| `frontend/src/admin/pages/ConfigsPage.css` | 页面样式 | ✅ |
| `frontend/src/admin/App.tsx` | 路由配置 | ✅ |

---

## 验证步骤

### 1. 数据库验证
```bash
cd backend
python -c "
from services.config import *
print(f'学科：{len(SubjectStore.get_all())} 条')
print(f'年级：{len(GradeStore.get_all())} 条')
print(f'学期：{len(SemesterStore.get_all())} 条')
print(f'教材版本：{len(TextbookVersionStore.get_all())} 条')
print(f'知识点：{len(KnowledgePointStore.get_all())} 条')
print(f'题型：{len(QuestionTypeStore.get_all_with_subjects())} 条')
"

# 输出:
# 学科：3 条
# 年级：9 条
# 学期：2 条
# 教材版本：10 条
# 知识点：43 条
# 题型：10 条
```

### 2. 后端 API 验证
```bash
# 启动服务
uvicorn main:app --reload

# 测试配置接口
curl http://localhost:8000/api/configs/configs
curl http://localhost:8000/api/configs/subjects
curl http://localhost:8000/api/configs/knowledge-points?subject_code=math
```

### 3. 前端验证
```bash
cd frontend
npm run dev
# 访问 http://localhost:5173/admin/configs
```

---

## 简化改造前后对比

| 项目 | 改造前 | 改造后 |
|------|--------|--------|
| knowledge_points 表 | group_id 外键关联 | 直接存储 4 个维度字段 |
| knowledge_point_groups 表 | 存在（10 条记录） | **已删除** |
| question_type_subjects 表 | 存在（关联表） | **已删除** |
| question_types.subjects | 单数字段 | 逗号分隔字符串 |
| 创建知识点流程 | 先创建分组再创建知识点 | 直接创建，一次性完成 |
| 前端表单字段 | group_id | subject_code + grade_code + semester_code + textbook_version_code |

---

## 后续优化建议

1. **TemplatesPage 适配**: 将模板管理页面的学科/年级/学期/教材版本下拉框改为从 API 加载
2. **缓存层**: Redis 缓存配置数据，减少数据库查询
3. **操作审计**: 记录所有配置变更日志到 `admin_operation_logs`
4. **批量导入**: 支持 Excel/CSV 批量导入配置数据
5. **多语言扩展**: 添加 `name_en`、`name_zh-TW` 等字段

---

## 注意事项

1. **扁平结构优势**: 减少表关联，查询更简单，前端使用更直观
2. **数据冗余**: 每个知识点直接存储 4 个维度字段，少量冗余换取查询性能
3. **逗号分隔设计**: `question_types.subjects` 使用逗号分隔，避免关联表复杂度
4. **软删除**: 所有配置项使用 `is_active` 字段实现软删除，保持数据完整性
5. **向后兼容**: `/api/configs/configs` 接口保持原有响应格式，确保现有功能不受影响
6. **fallback 机制**: 数据库不可用时自动 fallback 到 constants.py 中的常量定义

---

**改造完成日期**: 2026-03-17
**简化完成日期**: 2026-03-17
**版本**: v2.0（扁平结构）
