import React, { useEffect, useRef, useState } from 'react'
import './App.css'
import OrbVisualizer from './components/OrbVisualizer'
import VoiceInterface from './components/VoiceInterface'
import Dashboard from './components/Dashboard'
import TaskSubmitter from './components/TaskSubmitter'

function App() {
  const [connected, setConnected] = useState(false)
  const [orbState, setOrbState] = useState({
    position: [0, 0, 0],
    scale: 1.0,
    rotation: [0, 0, 0],
    color: '#0099FF',
    intensity: 0.5
  })
  const [listening, setListening] = useState(false)
  const [tasks, setTasks] = useState([])
  const ws = useRef(null)

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws.current = new WebSocket(`${protocol}//${window.location.hostname}:8000/ws/voice`)
    
    ws.current.onopen = () => {
      console.log('✅ Connected to JARVIS')
      setConnected(true)
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'response') {
        // Update orb state
        if (data.orb) {
          setOrbState(data.orb)
        }
        
        // Log response
        console.log('🤖 JARVIS:', data.text)
        
        // Play audio response if available
        if (data.audio) {
          playAudio(data.audio)
        }
      }
    }

    ws.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
      setConnected(false)
    }

    ws.current.onclose = () => {
      console.log('🔌 Disconnected from JARVIS')
      setConnected(false)
    }

    return () => {
      if (ws.current) ws.current.close()
    }
  }, [])

  const handleVoiceInput = (audioData, intensity) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return

    // Send audio to backend
    ws.current.send(JSON.stringify({
      type: 'audio',
      audio: audioData,
      intensity
    }))

    // Update visual feedback
    setListening(true)
  }

  const handleVoiceEnd = () => {
    setListening(false)
  }

  const handleTaskSubmit = async (taskType, content, context) => {
    try {
      const response = await fetch('/api/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_type: taskType,
          content,
          context
        })
      })

      const data = await response.json()
      setTasks([...tasks, data])
      console.log('✅ Task submitted:', data)
    } catch (error) {
      console.error('❌ Task submission error:', error)
    }
  }

  const playAudio = (audioBase64) => {
    try {
      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`)
      audio.play()
    } catch (error) {
      console.error('Audio playback error:', error)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🤖 JARVIS Chief of Staff</h1>
        <div className="status">
          <span className={`indicator ${connected ? 'connected' : 'disconnected'}`}></span>
          {connected ? 'Connected' : 'Offline'}
        </div>
      </header>

      <main className="main">
        {/* Left: Orb Visualization */}
        <section className="orb-section">
          <OrbVisualizer orbState={orbState} listening={listening} />
        </section>

        {/* Right: Controls & Dashboard */}
        <section className="control-section">
          {/* Voice Interface */}
          <VoiceInterface
            onInput={handleVoiceInput}
            onEnd={handleVoiceEnd}
            listening={listening}
          />

          {/* Task Submitter */}
          <TaskSubmitter onSubmit={handleTaskSubmit} />

          {/* Dashboard */}
          <Dashboard tasks={tasks} />
        </section>
      </main>

      <footer className="footer">
        <p>🧠 Neural engine active • 💰 Cost-optimized routing • 📊 Real-time monitoring</p>
      </footer>
    </div>
  )
}

export default App
