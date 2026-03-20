// CSS is imported from MainContent.tsx

interface Shortcut {
  label: string
  prompt: string
  icon: string
}

interface ShortcutsProps {
  onSelect: (prompt: string) => void
}

const SHORTCUTS: Shortcut[] = [
  { label: '口算题', prompt: '小学一年级数学 数的组成，比大小、多少、长短、高矮、轻重、简单分类、统计', icon: '🔢' },
  { label: '综合题', prompt: '小学六年级数学 分数小数混合运算、百分数、圆、比例、统计', icon: '📝' },
  { label: '应用题', prompt: '小学二年级语文，多音字、形近字、同音字辨析、陈述句、疑问句、感叹句', icon: '📚' },
  { label: '选择题', prompt: '上海人沪教牛津版小学三年级英语选择题', icon: '✅' },
  { label: '阅读理解', prompt: '小学四年级语文 阅读理解 2 篇，每篇 3 道题', icon: '📖' },
  { label: '英语题', prompt: '小学 6 年级英语综合题，题型丰富', icon: '🔤' },
]

export default function Shortcuts({ onSelect }: ShortcutsProps) {
  return (
    <div className="shortcuts">
      {SHORTCUTS.map((s) => (
        <button
          key={s.label}
          type="button"
          className="btn-shortcut"
          onClick={() => onSelect(s.prompt)}
        >
          <span className="shortcut-icon">{s.icon}</span>
          {s.label}
        </button>
      ))}
    </div>
  )
}
