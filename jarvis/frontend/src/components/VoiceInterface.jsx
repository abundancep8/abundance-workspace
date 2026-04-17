import React, { useEffect, useRef, useState } from 'react'

const VoiceInterface = ({ onInput, onEnd, listening }) => {
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef(null)

  useEffect(() => {
    // Check for Web Speech API support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (SpeechRecognition) {
      setIsSupported(true)
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.language = 'en-US'

      recognition.onstart = () => {
        console.log('🎤 Voice recognition started')
      }

      recognition.onresult = (event) => {
        let interim = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          
          if (event.results[i].isFinal) {
            setTranscript((prev) => prev + transcript + ' ')
            onInput(transcript, 0.8)
          } else {
            interim += transcript
          }
        }
        setInterimTranscript(interim)
      }

      recognition.onerror = (event) => {
        console.error('🔴 Speech recognition error:', event.error)
      }

      recognition.onend = () => {
        console.log('🎤 Voice recognition ended')
        onEnd()
      }

      recognitionRef.current = recognition
    }
  }, [onInput, onEnd])

  const startListening = () => {
    if (recognitionRef.current) {
      setTranscript('')
      setInterimTranscript('')
      recognitionRef.current.start()
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }

  const clearTranscript = () => {
    setTranscript('')
    setInterimTranscript('')
  }

  if (!isSupported) {
    return (
      <div className="voice-interface">
        <p>⚠️ Web Speech API not supported in your browser</p>
      </div>
    )
  }

  return (
    <div className="voice-interface">
      <h3>🎙️ Voice Control</h3>
      
      <div className="transcript-display">
        <div className="transcript-final">{transcript}</div>
        {interimTranscript && (
          <div className="transcript-interim">{interimTranscript}</div>
        )}
      </div>

      <div className="voice-controls">
        <button
          className={`voice-btn ${listening ? 'listening' : ''}`}
          onClick={listening ? stopListening : startListening}
        >
          {listening ? '🔴 Stop' : '🎤 Listen'}
        </button>
        <button className="clear-btn" onClick={clearTranscript}>
          Clear
        </button>
      </div>

      <div className="voice-hints">
        <p>Try: "Generate leads", "Show pipeline", "Schedule meeting"</p>
      </div>
    </div>
  )
}

export default VoiceInterface
