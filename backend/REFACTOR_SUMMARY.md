# 题目与答案分离改造完成报告

## 改造日期
2026-03-14

---

## 一、改造目标

解决原有系统无法返回题目详细信息（如 `rows_to_answer`、`answer_blanks`）的问题，实现：
1. 题目与答案分离存储
2. 后端自动填充作答辅助字段
3. 支持历史记录详情页和分享页获取结构化题目数据

---

## 二、数据库变更

### 新增表：`questions`

```sql
CREATE TABLE questions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    short_id         TEXT UNIQUE,
    record_id        INTEGER NOT NULL,           -- 所属试卷 ID
    question_index   INTEGER NOT NULL,           -- 第几题
    type             TEXT NOT NULL,              -- 题型
    stem             TEXT NOT NULL,              -- 题干
    options          TEXT,                       -- 选项 JSON
    passage          TEXT,                       -- 阅读材料 JSON
    sub_questions    TEXT,                       -- 子题 JSON
    knowledge_points TEXT NOT NULL,              -- 知识点 JSON
    answer_blanks    INTEGER,                    -- 填空题空格数
    rows_to_answer   INTEGER,                    -- 作答行数
    answer_text      TEXT,                       -- 标准答案
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 表关系
- `user_question_records` (试卷表) → 一对多 → `questions` (题目表)

---

## 三、新增服务

### 1. `services/question_data_cleaner.py`
题目数据清洗服务，负责：
- 解析 AI 返回的原始 JSON
- 根据题型自动计算 `rows_to_answer`
- 检测填空题的 `answer_blanks` 数量
- 提取/预留 `answer_text` 答案字段

**作答行数规则：**
| 题型 | 行数 |
|------|------|
| 单选题/判断题/填空题 | 1 行 |
| 计算题/应用题/几何题 | 3 行 |
| 古诗文鉴赏 | 3 行 |
| 作文题 | 10 行 |
| 阅读理解/完形填空 | 题干行数 + 子题数 × 2 |

### 2. `services/question_store.py`
题目存储服务，提供：
- `batch_insert_questions()` - 批量插入题目
- `get_questions_by_record_id()` - 获取整卷题目
- `get_answers_by_record_id()` - 获取整卷答案
- `get_question_by_id()` - 获取单题详情
- `get_question_answer()` - 获取单题答案

---

## 四、新增 API 接口

### 历史记录相关（需登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/history/{record_id}/questions` | GET | 获取试卷题目详情（含 `rows_to_answer`） |
| `/api/history/{record_id}/answers` | GET | 获取整卷答案 |

### 分享页相关（无需登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/share/history/{record_id}/questions` | GET | 分享页获取试卷题目 |
| `/api/share/history/{record_id}/answers` | GET | 分享页获取整卷答案 |

---

## 五、数据流程

```
用户请求生成题目
    ↓
AI 生成原始 JSON
    ↓
┌─────────────────────────────────────┐
│ 后端数据处理                         │
│                                     │
│ 1. 保存原始 JSON → ai_response     │
│ 2. 数据清洗 → 填充辅助字段          │
│ 3. 批量插入 → questions 表          │
└─────────────────────────────────────┘
    ↓
返回前端（record_id + short_id）
```

---

## 六、前端调用示例

### 获取历史记录列表
```typescript
// 获取用户的历史记录列表
const records = await fetch('/api/history?cursor=0&size=20')

// records.data[] 包含：
// - id, short_id, title, created_at
```

### 获取试卷题目详情
```typescript
// 获取某套试卷的完整题目（含 rows_to_answer）
const { meta, questions } = await fetch(`/api/history/${shortId}/questions`)

// questions[] 包含：
// - id, type, stem, options, knowledge_points
// - rows_to_answer, answer_blanks, answer_text
```

### 获取整卷答案
```typescript
// 获取某套试卷的所有答案
const { record_id, answers } = await fetch(`/api/history/${shortId}/answers`)

// answers[] 包含：
// - question_id, type, answer_text, rows_to_answer
```

---

## 七、文件变更清单

### 新增文件
- `backend/sql/migrations/001_add_questions_table.sql` - 数据库迁移脚本
- `backend/services/question_data_cleaner.py` - 数据清洗服务
- `backend/services/question_store.py` - 题目存储服务
- `backend/test_question_cleaner.py` - 测试脚本

### 修改文件
- `backend/sql/schema.sql` - 添加 questions 表定义
- `backend/routers/history.py` - 添加题目详情和答案接口
- `backend/routers/questions_structured.py` - 集成数据清洗和题目存储

---

## 八、测试验证

### 运行测试
```bash
cd backend
python test_question_cleaner.py
```

### 测试结果
```
题目 1 (SINGLE_CHOICE): rows_to_answer=1, answer_blanks=None
题目 2 (CALCULATION):   rows_to_answer=3, answer_blanks=None
题目 3 (FILL_BLANK):    rows_to_answer=1, answer_blanks=6
```

---

## 九、后续工作（前端改造）

1. **HistoryDetail.tsx** - 调用新接口 `/api/history/{shortId}/questions`
2. **StructuredPreview.tsx** - 使用 `rows_to_answer` 预留作答区域
3. **分享页** - 调用 `/api/share/history/{shortId}/questions`
4. **答案查看功能** - 调用 `/api/history/{shortId}/answers`

---

## 十、注意事项

1. **数据库迁移**：已自动执行，生产环境需手动运行
   ```bash
   python -c "import sqlite3; conn=sqlite3.connect('data/users.db'); conn.executescript(open('sql/migrations/001_add_questions_table.sql').read())"
   ```

2. **数据兼容**：
   - 现有 `user_question_records.ai_response` 保留
   - 历史数据无 `questions` 表记录，前端需兼容空数据

3. **答案录入**：
   - 当前 `answer_text` 字段为"答案待录入"占位符
   - 未来可通过管理后台人工录入答案

---

**改造完成，可以开始前端对接。**
