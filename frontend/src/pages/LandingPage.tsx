import { useEffect, useState, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import './LandingPage.css'
import LoginModal from '../components/LoginModal'
import { getToken } from '../auth'

export default function LandingPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [inputValue, setInputValue] = useState('')
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [loginModalMode, setLoginModalMode] = useState<'register' | 'login'>('register')
  const inputRef = useRef<HTMLInputElement>(null)

  // 已登录用户直接跳转到工作台
  useEffect(() => {
    const token = getToken()
    if (token) {
      navigate('/workbench')
    }
  }, [navigate])

  // SEO: 动态设置 meta 标签
  useEffect(() => {
    document.title = '题小宝'

    let metaDesc = document.querySelector('meta[name="description"]')
    if (!metaDesc) {
      metaDesc = document.createElement('meta')
      metaDesc.setAttribute('name', 'description')
      document.head.appendChild(metaDesc)
    }
    metaDesc.setAttribute('content', 'AI 智能生成中小学题库，支持数学、语文、英语多学科，按年级精准定制，一键导出 PDF 打印。家长和老师的首选出题工具。')

    let metaKeywords = document.querySelector('meta[name="keywords"]')
    if (!metaKeywords) {
      metaKeywords = document.createElement('meta')
      metaKeywords.setAttribute('name', 'keywords')
      document.head.appendChild(metaKeywords)
    }
    metaKeywords.setAttribute('content', '小学题库，数学题，语文题，英语题，AI 出题，练习题生成，试卷打印')

    let ogTitle = document.querySelector('meta[property="og:title"]')
    if (!ogTitle) {
      ogTitle = document.createElement('meta')
      ogTitle.setAttribute('property', 'og:title')
      document.head.appendChild(ogTitle)
    }
    ogTitle.setAttribute('content', 'AI 题库生成器 - 30 秒搞定一张练习卷')

    let ogDesc = document.querySelector('meta[property="og:description"]')
    if (!ogDesc) {
      ogDesc = document.createElement('meta')
      ogDesc.setAttribute('property', 'og:description')
      document.head.appendChild(ogDesc)
    }
    ogDesc.setAttribute('content', '支持数学、语文、英语多学科，一键导出 PDF')

    let ogType = document.querySelector('meta[property="og:type"]')
    if (!ogType) {
      ogType = document.createElement('meta')
      ogType.setAttribute('property', 'og:type')
      document.head.appendChild(ogType)
    }
    ogType.setAttribute('content', 'website')

    let structuredData = document.getElementById('landing-structured-data') as HTMLScriptElement
    if (!structuredData) {
      structuredData = document.createElement('script')
      structuredData.id = 'landing-structured-data'
      structuredData.type = 'application/ld+json'
      structuredData.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: '题小宝',
        description: 'AI 智能生成中小学题库，支持数学、语文、英语多学科',
        applicationCategory: 'EducationalApplication',
        operatingSystem: 'Web',
        offers: {
          '@type': 'Offer',
          price: '0',
          priceCurrency: 'CNY',
        },
        aggregateRating: {
          '@type': 'AggregateRating',
          ratingValue: '4.8',
          ratingCount: '1250',
        },
      })
      document.head.appendChild(structuredData)
    }
  }, [])

  // 检查 URL 参数，决定是否自动打开弹框
  useEffect(() => {
    const action = searchParams.get('action')
    if (action === 'register') {
      setShowLoginModal(true)
    }
  }, [searchParams])

  // 打字效果
  useEffect(() => {
    const placeholder = '请输入题目要求，例如：一年级数学 20 以内加减法 15 道题'
    let index = 0
    const typingInterval = setInterval(() => {
      if (index < placeholder.length) {
        setInputValue(placeholder.slice(0, index + 1))
        index++
        if (inputRef.current) {
          inputRef.current.value = placeholder.slice(0, index + 1)
        }
      } else {
        clearInterval(typingInterval)
        // 打完字后清空，让用户自己输入
        setTimeout(() => {
          if (inputRef.current) {
            inputRef.current.value = ''
            inputRef.current.placeholder = '请输入题目要求，例如：一年级数学 20 以内加减法 15 道题'
            inputRef.current.focus()
          }
          setInputValue('')
        }, 1500)
      }
    }, 80)

    return () => clearInterval(typingInterval)
  }, [])

  const handleOpenModal = (mode: 'register' | 'login') => {
    setLoginModalMode(mode)
    setShowLoginModal(true)
  }

  const handleLoginClick = () => {
    handleOpenModal('login')
  }

  const handleRegisterClick = () => {
    handleOpenModal('register')
  }

  const features = [
    {
      icon: '📝',
      title: '智能出题',
      description: 'AI 根据年级精准定制难度，告别手动查找',
    },
    {
      icon: '📚',
      title: '多学科支持',
      description: '数学/语文/英语全覆盖，知识点全面',
    },
    {
      icon: '🖨️',
      title: '打印、PDF 导出',
      description: '一键下载打印，格式美观规范',
    },
    {
      icon: '⏱️',
      title: '30 秒生成',
      description: '快速高效，节省宝贵时间',
    },
    {
      icon: '💾',
      title: '历史记录',
      description: '云端存储，随时查看题目记录',
    },
    {
      icon: '📱',
      title: '多端同步',
      description: '手机电脑都能用，随时随地',
    },
  ]

  const useCases = [
    {
      icon: '👨‍👩‍👧',
      title: '家长',
      scenarios: ['课后练习', '巩固知识点'],
    },
    {
      icon: '👩‍🏫',
      title: '老师',
      scenarios: ['课堂测验', '快速出卷'],
    },
    {
      icon: '🏫',
      title: '培训机构',
      scenarios: ['标准化题库', '批量生成'],
    },
  ]

  const demos = [
    {
      subject: '数学',
      grade: '一年级',
      topic: '20 以内加减法',
      color: 'from-blue-400 to-blue-600',
    },
    {
      subject: '语文',
      grade: '三年级',
      topic: '古诗词填空',
      color: 'from-pink-400 to-pink-600',
    },
    {
      subject: '英语',
      grade: '五年级',
      topic: '单词拼写练习',
      color: 'from-green-400 to-green-600',
    },
  ]

  // 20+ 条用户评价
  const testimonials = [
    { content: '以前每天要找各种题，现在 1 分钟生成，太方便了！', author: '北京 妈妈', color: '#FEF3C7' },
    { content: '周末终于有时间陪孩子了，不用到处找题了', author: '上海 爸爸', color: '#FEE2E2' },
    { content: '班上孩子都说题目有趣，学习积极性提高了', author: '广州 老师', color: '#E0E7FF' },
    { content: '题目质量很好，和教材同步，孩子进步明显', author: '深圳 妈妈', color: '#F3E8FF' },
    { content: '每天给孩子出 10 道题，坚持一个月，数学成绩提高了', author: '杭州 爸爸', color: '#ECFDF5' },
    { content: '老师推荐的，确实好用，题目类型丰富', author: '成都 妈妈', color: '#FFFBEB' },
    { content: '打印出来给孩子做，比手机 APP 好，不伤眼睛', author: '武汉 爸爸', color: '#F0F9FF' },
    { content: '可以按知识点出题，针对性练习，很实用', author: '南京 妈妈', color: '#FAF5FF' },
    { content: '孩子说题目有趣，不像作业，像玩游戏', author: '西安 爸爸', color: '#FEF2F2' },
    { content: '周末在家就能练习，不用去补习班了', author: '重庆 妈妈', color: '#F0FDFA' },
    { content: '题目难度适中，孩子不会抵触，很好', author: '苏州 爸爸', color: '#FFF7ED' },
    { content: '可以反复练习，错题也能记录，方便复习', author: '天津 妈妈', color: '#F5F3FF' },
    { content: '比买的练习册好用，可以定制，孩子喜欢', author: '长沙 爸爸', color: '#FDF2F8' },
    { content: '价格实惠，效果好，值得推荐', author: '郑州 妈妈', color: '#ECFDF5' },
    { content: '孩子主动要求做题，老母亲很欣慰', author: '青岛 爸爸', color: '#FEF3C7' },
    { content: '题目解析清楚，家长辅导也轻松', author: '宁波 妈妈', color: '#E0E7FF' },
    { content: '每天 15 分钟，孩子习惯养成了', author: '厦门 爸爸', color: '#FEE2E2' },
    { content: '期中考了双百，感谢这个工具！', author: '合肥 妈妈', color: '#F3E8FF' },
    { content: '孩子从 70 分到 90 分，进步太大了', author: '福州 爸爸', color: '#F0F9FF' },
    { content: '老师也夸孩子进步快，要继续加油', author: '南昌 妈妈', color: '#FFFBEB' },
    { content: '终于不用为孩子的学习发愁了', author: '沈阳 爸爸', color: '#FAF5FF' },
    { content: '孩子说班上的同学都在用，很流行', author: '大连 妈妈', color: '#FEF2F2' },
  ]

  return (
    <div className="landing-page">
      {/* 1. 导航栏 */}
      <nav className="landing-nav">
        <div className="landing-nav-content">
          <div className="landing-nav-logo" onClick={() => window.location.href = '/'}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3L1 9L12 15L21 9L12 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>题小宝</span>
          </div>
          <div className="landing-nav-actions">
            <button className="btn-nav-login" onClick={handleLoginClick}>
              登录
            </button>
            <button className="btn-nav-register" onClick={handleRegisterClick}>
              免费开始
            </button>
          </div>
        </div>
      </nav>

      {/* 2. Hero 区域 */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <h1 className="landing-hero-title">
            AI 智能生成中小学题库，30 秒搞定一张练习卷
          </h1>
          <p className="landing-hero-subtitle">
            支持数学、语文、英语多学科，按年级精准定制，一键导出 PDF 打印
          </p>

          {/* 可输入框 */}
          <div className="hero-input-wrapper">
            <div className="hero-input-demo">
              <span className="hero-input-icon">📝</span>
              <input
                ref={inputRef}
                type="text"
                placeholder="请输入题目要求，例如：一年级数学 20 以内加减法 15 道题"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                aria-label="题目输入"
              />
            </div>
            <div className="hero-input-hint">
              💡 支持：混合运算 | 应用题 | 选择题 | 填空题 | 比较大小
            </div>
          </div>

          <button className="btn-hero-cta" onClick={handleRegisterClick}>
            🚀 免费试用 - 立即开始
          </button>

        </div>
      </section>

      {/* 3. 功能特性 */}
      <section className="landing-features">
        <h2 className="section-title">核心功能</h2>
        <div className="features-scroll-wrapper">
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. 使用场景 */}
      <section className="landing-use-cases">
        <h2 className="section-title">适用人群</h2>
        <div className="use-cases-scroll-wrapper">
          <div className="use-cases-grid">
            {useCases.map((useCase, index) => (
              <div key={index} className="use-case-card">
                <div className="use-case-icon">{useCase.icon}</div>
                <h3 className="use-case-title">{useCase.title}</h3>
                <div className="use-case-scenarios">
                  {useCase.scenarios.map((scenario, i) => (
                    <span key={i} className="scenario-tag">
                      {scenario}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. 示例展示 */}
      <section className="landing-demos">
        <h2 className="section-title">试卷示例</h2>
        <div className="demos-scroll-wrapper">
          <div className="demos-grid">
            {demos.map((demo, index) => (
              <div key={index} className="demo-card" onClick={handleRegisterClick}>
                <div className={`demo-preview ${demo.color}`}>
                  <span className="demo-subject">{demo.subject}</span>
                  <span className="demo-grade">{demo.grade}</span>
                </div>
                <div className="demo-info">
                  <h3 className="demo-topic">{demo.topic}</h3>
                  <span className="demo-action">点击查看 →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 6. 用户评价 - 横向滚动 */}
      <section className="landing-testimonials">
        <h2 className="section-title">用户使用反馈</h2>
        <div className="testimonials-scroll-wrapper">
          <div className="testimonials-scroll">
            {/* 第一份 */}
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="testimonial-card"
                style={{ backgroundColor: testimonial.color }}
              >
                <p className="testimonial-content">"{testimonial.content}"</p>
                <p className="testimonial-author">—— {testimonial.author}</p>
              </div>
            ))}
            {/* 复制一份实现无缝滚动 */}
            {testimonials.map((testimonial, index) => (
              <div
                key={`copy-${index}`}
                className="testimonial-card"
                style={{ backgroundColor: testimonial.color }}
              >
                <p className="testimonial-content">"{testimonial.content}"</p>
                <p className="testimonial-author">—— {testimonial.author}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. 底部 CTA */}
      <section className="landing-cta">
        <h2 className="cta-title">立即开始，让孩子爱上学习</h2>
        <button className="btn-cta-primary" onClick={handleRegisterClick}>
          🎁 免费注册
        </button>
      </section>

      {/* 8. 页脚 */}
      <footer className="landing-footer">
        <p className="footer-copyright">
          © 2026 题小宝
        </p>
         <p className="footer-copyright">
          沪1CP备12022346号-6沪公网安备33037108502004号
        </p>
      </footer>

      {/* 登录注册弹框 */}
      {showLoginModal && (
        <LoginModal
          mode={loginModalMode}
          onClose={() => setShowLoginModal(false)}
          onSuccess={() => {
            setShowLoginModal(false)
            // 登录成功后刷新页面或跳转到 workbench
            window.location.href = '/workbench'
          }}
        />
      )}
    </div>
  )
}
