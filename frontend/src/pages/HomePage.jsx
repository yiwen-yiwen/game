import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/home.css'

function HomePage() {
  const navigate = useNavigate()
  const [hasSave, setHasSave] = useState(false)

  useEffect(() => {
    const gameId = localStorage.getItem('gameId')
    setHasSave(!!gameId)
  }, [])

  const handleNewGame = async () => {
    try {
      const res = await fetch('/api/game/new', { method: 'POST' })
      const data = await res.json()
      localStorage.setItem('gameId', data.game_id)
      localStorage.setItem('gameState', JSON.stringify(data.state))
      navigate('/loading')
    } catch (err) {
      alert('创建游戏失败，请检查网络')
    }
  }

  const handleContinue = () => {
    navigate('/loading')
  }

  return (
    <div className="home-container">
      <div className="home-card">
        <h1 className="home-title">大学生期末求生模拟器</h1>
        <p className="home-subtitle">Final Survival Simulator</p>
        <div className="home-buttons">
          <button className="btn btn-primary" onClick={handleNewGame}>
            新游戏
          </button>
          {hasSave && (
            <button className="btn btn-secondary" onClick={handleContinue}>
              继续游戏
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default HomePage
