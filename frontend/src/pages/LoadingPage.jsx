import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/loading.css'

function LoadingPage() {
  const navigate = useNavigate()
  const [progress, setProgress] = useState(0)
  const [tip, setTip] = useState('')

  const tips = [
    '正在生成试卷...',
    '学霸正在复习...',
    '室友正在打游戏...',
    '咖啡机正在加热...',
    '图书馆正在占座...',
    '教授正在出题...',
  ]

  useEffect(() => {
    setTip(tips[Math.floor(Math.random() * tips.length)])
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setTimeout(() => navigate('/game'), 500)
          return 100
        }
        return prev + Math.random() * 15 + 5
      })
    }, 300)

    return () => clearInterval(interval)
  }, [navigate])

  const displayProgress = Math.min(Math.round(progress), 100)

  return (
    <div className="loading-container">
      <div className="loading-card">
        <h2 className="loading-title">正在进入期末周...</h2>
        <div className="loading-bar-bg">
          <div 
            className="loading-bar-fill" 
            style={{ width: `${displayProgress}%` }}
          />
        </div>
        <p className="loading-percent">{displayProgress}%</p>
        <p className="loading-tip">{tip}</p>
      </div>
    </div>
  )
}

export default LoadingPage
