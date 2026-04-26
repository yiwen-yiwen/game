import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/ending.css'

function EndingPage() {
  const navigate = useNavigate()
  const [state, setState] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('gameState')
    if (saved) {
      setState(JSON.parse(saved))
    }
  }, [])

  const handleRestart = () => {
    localStorage.removeItem('gameId')
    localStorage.removeItem('gameState')
    navigate('/')
  }

  if (!state) {
    return <div className="ending-container"><p>加载中...</p></div>
  }

  const isPass = state.ending === 'pass'

  return (
    <div className={`ending-container ${isPass ? 'pass' : 'fail'}`}>
      <div className="ending-card">
        <h1 className="ending-title">
          {isPass ? '考试通过！' : '考试失败...'}
        </h1>
        <div className="ending-icon">
          {isPass ? '🎉' : '😭'}
        </div>
        <div className="ending-stats">
          <div className="ending-stat">
            <span className="stat-label">复习进度</span>
            <span className="stat-value">{state.study_progress}/100</span>
          </div>
          <div className="ending-stat">
            <span className="stat-label">剩余精力</span>
            <span className="stat-value">{state.energy}/100</span>
          </div>
          <div className="ending-stat">
            <span className="stat-label">金币</span>
            <span className="stat-value">{state.coins}</span>
          </div>
        </div>
        <p className="ending-desc">
          {isPass 
            ? '恭喜你！经过不懈努力，你成功通过了期末考试！' 
            : '很遗憾，你的复习进度不足，期末考试挂科了...'}
        </p>
        <button className="btn btn-restart" onClick={handleRestart}>
          重新开始
        </button>
      </div>
    </div>
  )
}

export default EndingPage
