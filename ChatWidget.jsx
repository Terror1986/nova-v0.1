import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])      // { role: 'user'|'assistant', text }
  const [input, setInput] = useState('')
  const [building, setBuilding] = useState(false)
  const [previewLink, setPreviewLink] = useState(null)
  const bottomRef = useRef()

  // On mount, load saved sessionId
  useEffect(() => {
    const saved = localStorage.getItem('nova_session')
    if (saved) setSessionId(saved)
  }, [])

  // Scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim()) return
    // 1) append user message
    setMessages(m => [...m, { role: 'user', text }])
    setInput('')

    // 2) call /api/chat
    const resp = await axios.post('/api/chat', {
      session_id: sessionId,
      message: text
    })
    const { reply, session_id } = resp.data

    // 3) persist session
    if (session_id !== sessionId) {
      setSessionId(session_id)
      localStorage.setItem('nova_session', session_id)
    }

    // 4) append assistant reply
    setMessages(m => [...m, { role: 'assistant', text: reply }])
  }

  const buildSite = async () => {
    setBuilding(true)
    setPreviewLink(null)
    const resp = await axios.post('/api/build', { prompt: input || 'Build me a site' })
    if (resp.data.success) {
      setPreviewLink(resp.data.preview)
    }
    setBuilding(false)
  }

  return (
    <div style={{
      border: '1px solid #ccc',
      borderRadius: 4,
      width: 320,
      display: 'flex',
      flexDirection: 'column',
      height: 480,
      overflow: 'hidden'
    }}>
      {/* Chat history */}
      <div style={{ flex: 1, padding: 8, overflowY: 'auto' }}>
        {messages.map((m,i) => (
          <div key={i}
               style={{ textAlign: m.role === 'user' ? 'right' : 'left', margin: '4px 0' }}>
            <span style={{
              display: 'inline-block',
              padding: '6px 12px',
              borderRadius: 12,
              background: m.role === 'user' ? '#007bff' : '#f1f1f1',
              color: m.role === 'user' ? 'white'   : 'black',
              maxWidth: '80%'
            }}>
              {m.text}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input & buttons */}
      <div style={{ padding: 8, borderTop: '1px solid #ddd' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' ? sendMessage(input) : null}
          placeholder="Type a message…"
          style={{ width: '100%', boxSizing: 'border-box', padding: 6 }}
        />

        <div style={{ marginTop: 6, display: 'flex', gap: 6 }}>
          <button
            onClick={() => sendMessage(input)}
            style={{ flex: 1, padding: '6px 0' }}
          >
            Send
          </button>

          <button
            onClick={buildSite}
            disabled={building}
            style={{ padding: '6px 12px' }}
          >
            { building ? 'Building…' : 'Build Site' }
          </button>
        </div>

        {previewLink && (
          <div style={{ marginTop: 6 }}>
            <a href={previewLink} target="_blank" rel="noopener">
              Open Preview
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
