import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoadingPage from './pages/LoadingPage'
import GamePage from './pages/GamePage'
import EndingPage from './pages/EndingPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/loading" element={<LoadingPage />} />
        <Route path="/game" element={<GamePage />} />
        <Route path="/ending" element={<EndingPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
