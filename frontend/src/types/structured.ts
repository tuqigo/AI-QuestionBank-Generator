/**
 * 结构化题目类型定义
 * 用于 AI 题库数据结构升级
 */

// ===================== 基础类型 =====================

/** 学科类型 */
export type Subject = 'math' | 'chinese' | 'english';

/** 年级类型 */
export type Grade = 'grade1' | 'grade2' | 'grade3' | 'grade4' | 'grade5'
  | 'grade6' | 'grade7' | 'grade8' | 'grade9';

/** 题型枚举 */
export type QuestionType =
  | 'SINGLE_CHOICE'    // 单选题
  | 'MULTIPLE_CHOICE'  // 多选题
  | 'TRUE_FALSE'       // 判断题
  | 'FILL_BLANK'       // 填空题
  | 'CALCULATION'      // 计算题
  | 'WORD_PROBLEM'     // 应用题
  | 'GEOMETRY'         // 几何题
  | 'READ_COMP'        // 阅读理解
  | 'POETRY_APP'       // 古诗文鉴赏/默写
  | 'CLOZE'            // 完形填空
  | 'ESSAY';           // 作文题

// ===================== 元数据 =====================

/** 元数据 */
export interface MetaData {
  subject: Subject;
  grade: Grade;
  title: string;
}

// ===================== 题目类型 =====================

/** 题目基类 */
export interface BaseQuestion {
  type: QuestionType;
  stem: string;
  knowledge_points: string[];
}

/** 带选项的题目 */
export interface QuestionWithOptions extends BaseQuestion {
  options: string[];
}

/** 带阅读材料的题目 */
export interface QuestionWithPassage extends BaseQuestion {
  passage: string;
}

/** 带子题的题目 */
export interface QuestionWithSubQuestions extends BaseQuestion {
  sub_questions: Question[];
}

/** 完整的题目类型（联合类型） */
export interface Question {
  type: QuestionType;
  stem: string;
  knowledge_points: string[];

  // 可选字段
  options?: string[];
  passage?: string;
  sub_questions?: Question[];
}

/** 带后端填充字段的题目 */
export interface StructuredQuestion extends Question {
  rows_to_answer: number;  // 预留作答行数
}

// ===================== API 响应 =====================

/** 结构化题目生成响应 */
export interface StructuredGenerateResponse {
  meta: MetaData;
  questions: StructuredQuestion[];
  record_id?: number;
  short_id?: string;
  created_at?: string;
}

// ===================== 组件属性 =====================

/** QuestionRenderer 组件属性 */
export interface QuestionRendererProps {
  question: Question;
  index?: number;  // 题号
  showAnswer?: boolean;  // 是否显示答案
}

/** 题型组件 props */
export interface SingleChoiceProps extends QuestionRendererProps {
  question: QuestionWithOptions;
}

export interface TrueFalseProps extends QuestionRendererProps {}

export interface FillBlankProps extends QuestionRendererProps {}

export interface CalculationProps extends QuestionRendererProps {}

export interface WordProblemProps extends QuestionRendererProps {}

export interface GeometryProps extends QuestionRendererProps {}

export interface ReadCompProps extends QuestionRendererProps {
  question: QuestionWithPassage & QuestionWithSubQuestions;
}

export interface PoetryAppProps extends QuestionRendererProps {}

export interface ClozeProps extends QuestionRendererProps {
  question: QuestionWithPassage & QuestionWithSubQuestions;
}

export interface EssayProps extends QuestionRendererProps {}
