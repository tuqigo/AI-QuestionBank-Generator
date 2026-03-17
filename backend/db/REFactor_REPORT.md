# 数据库改造完成报告：题型字段统一化

## 改造日期
2026-03-17

## 设计原则

**核心原则**：不显式 FK 约束，保留"逻辑上的 FK 关联"，将 FK 的校验从"数据库层面"转移到"应用层面"。

### 为什么不使用数据库 FK 约束/触发器？

1. **SQLite 的 FK 限制**：需要手动执行 `PRAGMA foreign_keys = ON` 才生效，且每个连接都需要设置
2. **错误提示不友好**：数据库层报错无法提供详细的错误信息（如列出有效题型）
3. **灵活性差**：应用层验证可以在插入前进行数据清洗、转换或降级处理
4. **调试困难**：数据库层约束错误难以追踪上下文
5. **迁移复杂度**：触发器需要额外的回滚脚本，增加维护成本

## 改造目标

将 `questions.type` 和 `question_templates.question_type` 字段改为引用 `question_types.en_name` 的逻辑关联字段，通过应用层验证确保数据一致性。

## 改造内容

### 1. 数据库迁移

题型数据初始化在 `020_add_question_types_table.sql` 中完成：
- 创建 `question_types` 表
- 初始化 10 种题型（SINGLE_CHOICE, MULTIPLE_CHOICE, CALCULATION 等）

应用层验证设计说明：
- `questions.type` 存储题型 en_name（如 `SINGLE_CHOICE`, `CALCULATION`）
- `question_templates.question_type` 存储题型 en_name
- 题型有效性校验在应用层完成

**不使用**：
- FOREIGN KEY 约束（schema.sql 中已存在的 FK 定义仅作为文档说明）
- TRIGGER 触发器验证

### 2. 后端代码修改

#### services/question/question_store.py

添加 `_validate_question_type()` 函数，支持两种模式：

```python
def _validate_question_type(conn: sqlite3.Connection, question_type: str, auto_fix: bool = False) -> str:
    """
    验证题型是否有效

    Args:
        conn: 数据库连接
        question_type: 题型名称
        auto_fix: 是否自动修复无效题型

    Returns:
        验证通过的题型名称，或 auto_fix=True 时的默认题型

    Raises:
        ValueError: 如果题型无效且 auto_fix=False
    """
```

**两种验证模式**：
- **严格模式** (`auto_fix=False`)：遇到无效题型抛出异常，提供友好错误提示
- **自动修复模式** (`auto_fix=True`)：遇到无效题型记录警告并使用默认题型 `SINGLE_CHOICE`

**应用场景**：
- `batch_insert_questions()`：使用自动修复模式（AI 生成的题目可能包含无效题型）
- `template_store.py`：使用严格模式（用户手动输入，应立即报错）

#### services/template/template_store.py

- 在 `create_template()` 中调用 `_validate_question_type()`（严格模式）
- 在 `update_template()` 中调用（仅当提供 question_type 时，严格模式）

#### api/v1/configs.py
添加题型管理 CRUD 接口：
- `GET /api/configs/question-types` - 获取题型列表
- `POST /api/configs/admin/question-types/create` - 创建题型
- `PUT /api/configs/admin/question-types/{id}/update` - 更新题型
- `DELETE /api/configs/admin/question-types/{id}/delete` - 删除题型

### 3. 前端代码修改

#### frontend/src/api/config.ts
添加题型管理 API 调用函数：
- `getQuestionTypes()` - 获取题型列表
- `createQuestionType()` - 创建题型
- `updateQuestionType()` - 更新题型
- `deleteQuestionType()` - 删除题型

#### frontend/src/admin/pages/ConfigsPage.tsx
添加题型配置管理 Tab：
- 在配置管理页面新增"题型配置"标签页
- 支持题型列表展示（ID、英文名称、中文名称、适用学科、排序、状态）
- 支持创建新题型（英文名称、中文名称、适用学科、排序）
- 支持编辑题型（禁用英文名称修改，支持修改中文名称、适用学科、排序）
- 支持删除题型
- 支持启用/禁用题型

### 4. 清理 FK 相关配置

#### db/migrations/__init__.py
删除 `conn.execute("PRAGMA foreign_keys = ON")` 调用

#### services/question/question_store.py
删除 `conn.execute("PRAGMA foreign_keys = ON")` 调用

#### services/template/template_store.py
删除 `conn.execute("PRAGMA foreign_keys = ON")` 调用

## 验证结果

### 数据库验证
```
迁移状态：全部成功
触发器：无

Active question types (10):
  SINGLE_CHOICE: 单选题
  MULTIPLE_CHOICE: 多选题
  TRUE_FALSE: 判断题
  FILL_BLANK: 填空题
  CALCULATION: 计算题
  WORD_PROBLEM: 应用题
  ORAL_CALCULATION: 口算题
  READ_COMP: 阅读理解
  ESSAY: 作文
  CLOZE: 完形填空
```

### 代码验证
```
Test 1 - Valid type: CALCULATION
Test 2 - Invalid type (auto_fix): SINGLE_CHOICE
Test 3 - Invalid type (strict): Correctly raised ValueError
Test 4 - Empty type (auto_fix): SINGLE_CHOICE
All tests passed!
```

## 改造收益

1. **数据一致性提升**
   - 防止拼写错误导致脏数据
   - 确保所有题型都经过统一管理

2. **错误提示友好**
   - 无效的题型会返回明确的错误消息
   - 列出所有有效题型供参考

3. **灵活性强**
   - 应用层可以根据业务需要调整验证逻辑
   - 支持数据清洗和降级处理（auto_fix 模式）

4. **调试友好**
   - 验证逻辑在代码中，易于打断点和日志记录
   - 错误堆栈清晰，便于定位问题

## 系统 FK 设计审查

### 当前 schema.sql 中的 FK 定义（仅作为文档说明）

| 表 | 字段 | 引用 | 实际约束 |
|----|------|------|----------|
| questions | record_id | user_question_records(id) | 逻辑关联，无强制约束 |
| template_usage_logs | template_id | question_templates(id) | 逻辑关联，无强制约束 |
| template_usage_logs | user_id | users(id) | 逻辑关联，无强制约束 |

**说明**：这些 FOREIGN KEY 定义在 SQLite 中默认不生效（需要 `PRAGMA foreign_keys = ON`），仅作为文档说明表之间的逻辑关联关系。

### 应用层验证覆盖

| 字段 | 验证位置 | 验证模式 | 验证时机 |
|------|----------|----------|----------|
| questions.type | question_store.py | auto_fix=True | 批量插入时 |
| question_templates.question_type | template_store.py | auto_fix=False (严格) | 创建/更新时 |

**题型常量同步**：

| 文件 | 说明 | 状态 |
|------|------|------|
| question_types 表 | 数据库中的题型定义（10 种） | ✅ 数据源 |
| services/ai/question_data_cleaner.py | 题型枚举常量（10 种） | ✅ 已同步 |
| services/question/question_type_store.py | 题型 CRUD 服务 | ✅ 已实现 |

## 已删除的 FK/触发器相关代码

| 文件 | 删除内容 | 原因 |
|------|----------|------|
| db/migrations/__init__.py | `PRAGMA foreign_keys = ON` | 不依赖数据库 FK 约束 |
| services/question/question_store.py | `PRAGMA foreign_keys = ON` | 不依赖数据库 FK 约束 |
| services/template/template_store.py | `PRAGMA foreign_keys = ON` | 不依赖数据库 FK 约束 |
| db/migrations/021_question_type_documentation.sql | 整个文件 | 空迁移，仅注释无实际 SQL |

## 后续建议

1. 考虑在管理后台添加题型管理页面（复用现有 CRUD API）
2. 定期审查 question_types 表，清理未使用的题型
3. 如需处理历史脏数据，可编写一次性数据清洗脚本

## 附录：题型常量同步检查

### question_types 表中的数据（10 种）
```
SINGLE_CHOICE: 单选题
MULTIPLE_CHOICE: 多选题
TRUE_FALSE: 判断题
FILL_BLANK: 填空题
CALCULATION: 计算题
WORD_PROBLEM: 应用题
ORAL_CALCULATION: 口算题
READ_COMP: 阅读理解
ESSAY: 作文
CLOZE: 完形填空
```

### question_data_cleaner.py 中的常量
- [x] SINGLE_CHOICE
- [x] MULTIPLE_CHOICE
- [x] TRUE_FALSE
- [x] FILL_BLANK
- [x] CALCULATION
- [x] WORD_PROBLEM
- [x] ORAL_CALCULATION（2026-03-17 补充）
- [x] READ_COMP
- [x] CLOZE
- [x] ESSAY
