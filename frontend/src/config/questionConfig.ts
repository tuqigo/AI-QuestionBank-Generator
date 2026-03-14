/**
 * 题型配置中心
 * 为每种题型提供渲染（屏幕显示）和打印两套配置
 * 支持后续自定义扩展
 */
import type { QuestionType } from '@/types/structured'

/** 选项排列方式 */
export type OptionLayout = 'horizontal' | 'vertical'

/** 答案区域类型 */
export type AnswerAreaType = 'none' | 'blank' | 'lined' | 'grid'

/** 单套配置（渲染或打印） */
export interface QuestionModeConfig {
  /** 是否显示答案区域 */
  showAnswerArea: boolean
  /** 答案区域提示文字 */
  answerAreaText: string
  /** 答案区域类型 */
  answerAreaType: AnswerAreaType
  /** 选项排列方式 */
  optionLayout: OptionLayout
  /** 是否显示题号 */
  showQuestionNumber: boolean
  /** 题号后缀（如 ". " 或 "、"） */
  numberSuffix: string
  /** 自定义 class 名 */
  customClass?: string
}

/** 题型完整配置（包含渲染和打印） */
export interface QuestionTypeConfig {
  /** 屏幕渲染配置 */
  render: QuestionModeConfig
  /** 打印配置 */
  print: QuestionModeConfig
}

/** 题型配置映射 */
export const QUESTION_TYPE_CONFIGS: Record<QuestionType, QuestionTypeConfig> = {
  // ==================== 数学题型 ====================

  /** 单选题 */
  SINGLE_CHOICE: {
    render: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-single-choice'
    },
    print: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-single-choice'
    }
  },

  /** 多选题 */
  MULTIPLE_CHOICE: {
    render: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-multiple-choice'
    },
    print: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-multiple-choice'
    }
  },

  /** 判断题 */
  TRUE_FALSE: {
    render: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'horizontal',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-true-false'
    },
    print: {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'horizontal',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-true-false'
    }
  },

  /** 填空题 */
  FILL_BLANK: {
    render: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-fill-blank'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-fill-blank'
    }
  },

  /** 计算题 */
  CALCULATION: {
    render: {
      showAnswerArea: true,
      answerAreaText: '解：________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-calculation'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '解：________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-calculation'
    }
  },

  /** 应用题 */
  WORD_PROBLEM: {
    render: {
      showAnswerArea: true,
      answerAreaText: '答：________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-word-problem'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '答：________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-word-problem'
    }
  },

  /** 几何题 - 暂用计算题配置 */
  GEOMETRY: {
    render: {
      showAnswerArea: true,
      answerAreaText: '解：________________________',
      answerAreaType: 'blank',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-geometry'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '解：________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-geometry'
    }
  },

  // ==================== 语文题型 ====================

  /** 阅读理解 */
  READ_COMP: {
    render: {
      showAnswerArea: true,
      answerAreaText: '答：________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-read-comp'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '答：________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-read-comp'
    }
  },

  /** 古诗文鉴赏/默写 */
  POETRY_APP: {
    render: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-poetry-app'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-poetry-app'
    }
  },

  /** 完形填空 */
  CLOZE: {
    render: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-cloze'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '________________________',
      answerAreaType: 'lined',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-cloze'
    }
  },

  /** 作文题 */
  ESSAY: {
    render: {
      showAnswerArea: true,
      answerAreaText: '',
      answerAreaType: 'grid',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'render-essay'
    },
    print: {
      showAnswerArea: true,
      answerAreaText: '',
      answerAreaType: 'grid',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. ',
      customClass: 'print-essay'
    }
  }
}

/**
 * 获取题型配置
 * @param questionType - 题型
 * @param mode - 模式：'render'（渲染）或 'print'（打印）
 * @returns 题型配置
 */
export function getQuestionConfig(
  questionType: QuestionType,
  mode: 'render' | 'print' = 'render'
): QuestionModeConfig {
  const config = QUESTION_TYPE_CONFIGS[questionType]
  if (!config) {
    // 返回默认配置
    return {
      showAnswerArea: false,
      answerAreaText: '',
      answerAreaType: 'none',
      optionLayout: 'vertical',
      showQuestionNumber: true,
      numberSuffix: '. '
    }
  }
  return config[mode]
}

/**
 * 根据题型和模式获取 CSS 类名
 * @param questionType - 题型
 * @param mode - 模式
 * @returns CSS 类名字符串
 */
export function getQuestionClassName(
  questionType: QuestionType,
  mode: 'render' | 'print' = 'render'
): string {
  const config = getQuestionConfig(questionType, mode)
  const modeClass = mode === 'print' ? 'print-mode' : 'render-mode'
  return `${modeClass} ${config.customClass || ''}`.trim()
}
