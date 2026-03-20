/**
 * 结构化题目类型定义
 * 用于 AI 题库数据结构升级
 */

// ===================== 基础类型 =====================

/** 学科类型（从后端 API 获取） */
export type Subject = string

/** 年级类型（从后端 API 获取） */
export type Grade = string

/** 学期类型（从后端 API 获取） */
export type Semester = string

/** 题型枚举 */
export type QuestionType =
  | 'SINGLE_CHOICE'    // 单选题
  | 'MULTIPLE_CHOICE'  // 多选题
  | 'TRUE_FALSE'       // 判断题
  | 'FILL_BLANK'       // 填空题
  | 'CALCULATION'      // 计算题
  | 'ORAL_CALCULATION' // 口算题
  | 'WORD_PROBLEM'     // 应用题
  | 'GEOMETRY'         // 几何题
  | 'READ_COMP'        // 阅读理解
  | 'POETRY_APP'       // 古诗文鉴赏/默写
  | 'CLOZE'            // 完形填空
  | 'ESSAY'            // 作文题

// ===================== 元数据 =====================

/** 元数据（完整格式，用于生成响应） */
export interface MetaData {
  subject: Subject
  grade: Grade
  title: string
}

/** 元数据（精简格式，用于历史记录 API 返回） */
export interface RecordMeta {
  record_id?: number
  short_id?: string
  title?: string
  created_at?: string
  subject?: Subject
  grade?: Grade
}

// ===================== 题目类型 =====================

/** 题目基类 */
export interface BaseQuestion {
  type: QuestionType
  stem: string
  knowledge_points: string[]
}

/** 带选项的题目 */
export interface QuestionWithOptions extends BaseQuestion {
  options: string[]
}

/** 带阅读材料的题目 */
export interface QuestionWithPassage extends BaseQuestion {
  passage: string
}

/** 带子题的题目 */
export interface QuestionWithSubQuestions extends BaseQuestion {
  sub_questions: Question[]
}

/** 完整的题目类型（联合类型） */
export interface Question {
  type: QuestionType
  stem: string
  knowledge_points: string[]

  // 可选字段
  options?: string[]
  passage?: string
  sub_questions?: Question[]
}

/** 题目渲染元数据 */
export interface QuestionRenderingMeta {
  // ========== 布局相关 ==========
  layout?: 'single' | 'multi' | 'inline'  // 单列/多列/行内布局
  columns?: number  // 多列布局时的列数（默认 3）

  // ========== 字体相关 ==========
  font_size?: number  // 12-24，默认 14

  // ========== LaTeX 相关（竖式专用） ==========
  latex_scale?: number  // MathJax 缩放，默认 1.0

  // ========== 作答区域 ==========
  rows_to_answer?: number  // 作答行数（计算题/应用题/作文题）
  answer_width?: number  // 作答宽度 px（填空题/口算题），-1 表示自适应宽度
  answer_style?: 'box' | 'line' | 'dashed_box' | 'circle' | 'parentheses' | 'blank'  // 答案样式类型
  answer_count?: number  // 答案位置数量（用于多空题）

  // ========== 打印控制 ==========
  keep_together?: boolean  // 避免分页打断（默认 true）

  // ========== 显示控制 ==========
  show_question_number?: boolean  // 是否显示题号（默认 true）
}

/** 带后端填充字段的题目 */
export interface StructuredQuestion extends Question {
  rows_to_answer: number  // 预留作答行数
  answer_blanks?: number  // 填空题空格数
  answer_text?: string    // 参考答案

  // 新增：渲染元数据
  rendering_meta?: QuestionRenderingMeta
}

// ===================== API 响应 =====================

/** 结构化题目生成响应 */
export interface StructuredGenerateResponse {
  meta: MetaData
  questions: StructuredQuestion[]
  record_id?: number
  short_id?: string
  created_at?: string
}

// ===================== 组件属性 =====================

/** QuestionRenderer 组件属性 */
export interface QuestionRendererProps {
  question: Question
  index?: number  // 题号
  mode?: 'render' | 'print'  // 渲染模式
  showAnswer?: boolean  // 是否显示答案
}

/** 题型组件 props */
export interface SingleChoiceProps extends QuestionRendererProps {
  question: QuestionWithOptions
}

export interface TrueFalseProps extends QuestionRendererProps {}

export interface FillBlankProps extends QuestionRendererProps {}

export interface CalculationProps extends QuestionRendererProps {}

export interface WordProblemProps extends QuestionRendererProps {}

export interface GeometryProps extends QuestionRendererProps {}

export interface ReadCompProps extends QuestionRendererProps {
  question: QuestionWithPassage & QuestionWithSubQuestions
}

export interface PoetryAppProps extends QuestionRendererProps {}

export interface ClozeProps extends QuestionRendererProps {
  question: QuestionWithPassage & QuestionWithSubQuestions
}

export interface EssayProps extends QuestionRendererProps {}

// ===================== 模板相关类型 =====================

/** 模板筛选条件 */
export interface TemplateFilter {
  grade?: Grade
  subject?: Subject
  semester?: Semester
  textbook_version?: string  // 教材版本 ID（如 "rjb", "bsd"）
}

/** 模板列表项 */
export interface TemplateItem {
  id: number
  name: string
  subject: string
  grade: string
  semester: string
  textbook_version: string  // 教材版本 ID（如 "rjb", "bsd"）
  example: string | null
}

/** 模板生成题目响应 */
export interface TemplateGenerateResponse {
  meta: MetaData
  questions: StructuredQuestion[]
}
