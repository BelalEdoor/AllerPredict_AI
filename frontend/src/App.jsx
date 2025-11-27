import React, { useState, useRef, useEffect } from 'react'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  const logoUrl = "https://upload.wikimedia.org/wikipedia/commons/5/53/Logo_placeholder.png"

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { type: 'user', text: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/analyze_product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product: input })
      })
      if (!res.ok) throw new Error('Network response was not ok')
      const data = await res.json()
      const botMessage = { type: 'bot', data }
      setMessages(prev => [...prev, botMessage])
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', data: { detected_allergens: [], risk_level: 'Error', ethical_score: 0, recommendations: [err.message] } }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-app">
      <header className="chat-header">
        <img src={logoUrl} alt="Logo" className="logo"/>
        <h1>AllerPredict</h1>
      </header>

      <div className="chat-window">
        {messages.map((msg, i) => (
          msg.type === 'user' ? (
            <div key={i} className="chat-bubble user">{msg.text}</div>
          ) : (
            <div key={i} className="chat-bubble bot">
              <strong>Analysis Result:</strong>
              <div><strong>Detected Allergens:</strong> {msg.data.detected_allergens.join(', ') || 'None'}</div>
              <div><strong>Risk Level:</strong> {msg.data.risk_level}</div>
              <div><strong>Ethical Score:</strong> {msg.data.ethical_score}</div>
              <div><strong>Recommendations:</strong>
                <ul>
                  {msg.data.recommendations.map((r, idx) => <li key={idx}>{r}</li>)}
                </ul>
              </div>
            </div>
          )
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter product name or ingredients..."
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? 'Analyzing...' : 'Send'}
        </button>
      </form>
    </div>
  )
}
