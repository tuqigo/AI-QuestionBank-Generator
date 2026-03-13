/**
 * StructuredPreview - 结构化题目预览页面
 * 用于测试 QuestionRenderer 组件
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getToken } from '@/auth'
import QuestionRenderer from '@/components/QuestionRenderer'
import './StructuredPreview.css'
import type { StructuredGenerateResponse, Question } from '@/types/structured'

// 测试数据 - 模拟 API 返回
const TEST_DATA: StructuredGenerateResponse = {
  meta: {
    subject: 'math',
    grade: 'grade7',
    title: '初一数学综合练习题'
  },
  questions: [
    {
      type: 'SINGLE_CHOICE',
      stem: '下列各数中，属于负有理数的是',
      options: ['A. $3$', 'B. $0$', 'C. $-\\sqrt{2}$', 'D. $-0.5$'],
      knowledge_points: ['有理数的概念'],
      rows_to_answer: 1
    },
    {
      type: 'TRUE_FALSE',
      stem: '一个数的绝对值一定是正数。',
      knowledge_points: ['绝对值'],
      rows_to_answer: 1
    },
    {
      type: 'FILL_BLANK',
      stem: '数轴上表示$-3$的点到原点的距离是___。',
      knowledge_points: ['数轴与绝对值'],
      rows_to_answer: 1
    },
    {
      type: 'CALCULATION',
      stem: '计算：$(-2)+3-(-5)+(-4)$',
      knowledge_points: ['有理数的加减运算'],
      rows_to_answer: 3
    },
    {
      type: 'WORD_PROBLEM',
      stem: '甲、乙两人相距$1000$米，甲每分钟走$60$米，乙每分钟走$40$米，两人同时相向而行，经过多少分钟相遇？',
      knowledge_points: ['一元一次方程的应用（行程问题）'],
      rows_to_answer: 3
    },
    {
      type: 'GEOMETRY',
      stem: '已知线段$AB=8\\text{cm}$，点$C$是$AB$的中点，求线段$AC$的长度。',
      knowledge_points: ['线段中点'],
      rows_to_answer: 3
    },
    {
      type: 'READ_COMP',
      stem: '阅读下面文字，完成题目。',
      passage: '文学是灯，照亮人性之美。文学是灯，是一种有温度、有光芒的存在，它能照亮我们的内心，让我们在纷繁的世界中保持清醒与善良。',
      knowledge_points: ['现代文阅读'],
      rows_to_answer: 5,
      sub_questions: [
        {
          type: 'SINGLE_CHOICE',
          stem: '选段中"文学是灯"运用的修辞手法是',
          options: ['A. 比喻', 'B. 拟人', 'C. 排比', 'D. 夸张'],
          knowledge_points: ['修辞手法'],
          rows_to_answer: 1
        },
        {
          type: 'FILL_BLANK',
          stem: '选段的中心句是___。',
          knowledge_points: ['概括中心'],
          rows_to_answer: 1
        }
      ]
    },
    {
      type: 'CLOZE',
      stem: 'Read the passage and fill in the blanks.',
      passage: 'I have a happy family. There are three people in my family. My parents love me very much. We always help __1__ other.',
      knowledge_points: ['完形填空'],
      rows_to_answer: 5,
      sub_questions: [
        {
          type: 'FILL_BLANK',
          stem: 'I have a happy family. There are three people in my family. My parents love me very much. We always help ___ other.',
          knowledge_points: ['固定搭配'],
          rows_to_answer: 1
        }
      ]
    },
    {
      type: 'POETRY_APP',
      stem: '赏析"落红不是无情物，化作春泥更护花"的思想感情。',
      knowledge_points: ['古诗文鉴赏'],
      rows_to_answer: 3
    },
    {
      type: 'ESSAY',
      stem: '请以"成长的力量"为题，写一篇不少于600字的文章，文体不限（诗歌除外）。',
      knowledge_points: ['写作'],
      rows_to_answer: 5
    }
  ]
}

export default function StructuredPreview() {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 加载 MathJax
  useEffect(() => {
    if (!window.MathJax) {
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
      script.async = true
      document.head.appendChild(script)

      script.onload = () => {
        window.MathJax?.typesetPromise()
      }
    }
  }, [])

  // 题目更新后重新渲染 MathJax
  useEffect(() => {
    if (questions.length > 0 && window.MathJax) {
      window.MathJax.typesetPromise()
    }
  }, [questions])

  useEffect(() => {
    // 模拟 API 调用
    const fetchQuestions = async () => {
      try {
        const token = getToken()
        if (!token) {
          navigate('/')
          return
        }

        // 使用测试数据
        setQuestions(TEST_DATA.questions)
        setLoading(false)
      } catch (err) {
        console.error('加载失败:', err)
        setError('加载失败')
        setLoading(false)
      }
    }

    fetchQuestions()
  }, [navigate])

  const handleBack = () => {
    navigate('/workbench')
  }

  const handlePrint = async () => {
    window.print()
  }

  if (loading) {
    return (
      <div className="preview-page">
        <div className="loading">加载中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="preview-page">
        <div className="error">{error}</div>
        <button onClick={handleBack} className="btn-back">返回</button>
      </div>
    )
  }

  return (
    <div className="preview-page">
      {/* 顶部栏 */}
      <div className="preview-header">
        <h2>{TEST_DATA.meta.title}</h2>
        <div className="preview-actions">
          <button onClick={handlePrint} className="btn-print">打印</button>
          <button onClick={handleBack} className="btn-back">返回</button>
        </div>
      </div>

      {/* 题目列表 */}
      <div className="preview-content">
        <div className="questions-container">
          {questions.map((question, index) => (
            <div key={index} className="question-wrapper">
              <QuestionRenderer question={question} index={index + 1} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
