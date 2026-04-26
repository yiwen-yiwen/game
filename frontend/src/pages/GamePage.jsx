import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/game.css'

function GamePage() {
  const navigate = useNavigate()
  const [state, setState] = useState(null)
  const [showEventModal, setShowEventModal] = useState(false)
  const [eventResult, setEventResult] = useState(null)
  const [midnightModal, setMidnightModal] = useState(false)
  const [loading, setLoading] = useState(true)

  const gameId = localStorage.getItem('gameId')

  useEffect(() => {
    if (!gameId) {
      navigate('/')
      return
    }
    fetchState()
  }, [gameId])

  const fetchState = async () => {
    try {
      const res = await fetch(`/api/game/${gameId}`)
      if (!res.ok) throw new Error('获取状态失败')
      const data = await res.json()
      setState(data)
      setLoading(false)
      
      if (data.game_over) {
        navigate('/ending')
        return
      }
      
      if (data.is_midnight_rest) {
        setMidnightModal(true)
      }
    } catch (err) {
      alert('获取游戏状态失败')
      navigate('/')
    }
  }

  const handleEvent = async (choice) => {
    try {
      const res = await fetch(`/api/game/${gameId}/event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ choice })
      })
      const data = await res.json()
      setState(data.state)
      setEventResult(data.result)
      
      if (data.result.ending) {
        localStorage.setItem('gameState', JSON.stringify(data.state))
        setTimeout(() => navigate('/ending'), 2000)
      }
    } catch (err) {
      alert('事件处理失败')
    }
  }

  const handleMidnightContinue = async () => {
    try {
      const res = await fetch(`/api/game/${gameId}/midnight`, { method: 'POST' })
      const data = await res.json()
      setState(data)
      setMidnightModal(false)
    } catch (err) {
      alert('处理失败')
    }
  }

  const getTimeLabel = () => {
    if (!state) return ''
    const { day, hour } = state
    const period = hour >= 8 && hour < 20 ? '白天' : '夜晚'
    const displayHour = String(hour).padStart(2, '0')
    return `第 ${day} 天 · ${period} · ${displayHour}:00`
  }

  const getAvailableEvents = () => {
    if (!state) return []
    const hour = state.hour
    const isDay = hour >= 8 && hour < 20
    
    if (isDay) {
      return [
        { id: 'review', label: '复习', desc: '复习进度 +5，精力 -30' },
        { id: 'go_out', label: '外出', desc: '精力 -30，可能触发随机事件' },
      ]
    } else {
      return [
        { id: 'sleep', label: '睡觉', desc: '精力 +20' },
        { id: 'go_out', label: '外出', desc: '精力 -30，可能触发随机事件' },
      ]
    }
  }

  if (loading || !state) {
    return <div className="game-container"><p>加载中...</p></div>
  }

  return (
    <div className="game-container">
      <div className="game-header">
        <h2 className="game-time">{getTimeLabel()}</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">精力</span>
            <div className="progress-bar-bg">
              <div 
                className="progress-bar-fill energy" 
                style={{ width: `${state.energy}%` }}
              />
            </div>
            <span className="stat-value">{state.energy}/100</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">复习进度</span>
            <div className="progress-bar-bg">
              <div 
                className="progress-bar-fill study" 
                style={{ width: `${state.study_progress}%` }}
              />
            </div>
            <span className="stat-value">{state.study_progress}/100</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">金币</span>
            <span className="stat-value coins">{state.coins}</span>
          </div>
        </div>
      </div>

      <div className="game-actions">
        <button 
          className="btn btn-event"
          onClick={() => {
            setShowEventModal(true)
            setEventResult(null)
          }}
        >
          选择行动
        </button>
      </div>

      {showEventModal && (
        <div className="modal-overlay" onClick={() => setShowEventModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>选择行动（消耗4小时）</h3>
            <div className="event-buttons">
              {getAvailableEvents().map(event => (
                <button
                  key={event.id}
                  className="btn btn-event-choice"
                  onClick={() => {
                    handleEvent(event.id)
                    setShowEventModal(false)
                  }}
                >
                  <span className="event-name">{event.label}</span>
                  <span className="event-desc">{event.desc}</span>
                </button>
              ))}
            </div>
            <button className="btn btn-close" onClick={() => setShowEventModal(false)}>
              取消
            </button>
          </div>
        </div>
      )}

      {eventResult && (
        <div className="result-panel">
          <p className="result-message">{eventResult.message}</p>
          {eventResult.random_event && (
            <p className="random-event">{eventResult.random_event.message}</p>
          )}
        </div>
      )}

      {midnightModal && (
        <div className="modal-overlay">
          <div className="modal-content midnight">
            <h3>午夜休息</h3>
            <p>时间到了午夜，你自动进入休息状态。</p>
            <p>精力恢复 80 点，进入新的一天。</p>
            <button className="btn btn-primary" onClick={handleMidnightContinue}>
              继续
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default GamePage
