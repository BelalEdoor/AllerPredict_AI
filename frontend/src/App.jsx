import React, { useState, useRef, useEffect } from 'react'
import './styles.css'
import logoUrl from './assest/logo.png'

export default function App() {
  const [messages, setMessages] = useState([])
  const [products, setProducts] = useState([])
  const [filteredProducts, setFilteredProducts] = useState([])
  const [input, setInput] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => { scrollToBottom() }, [messages])

  // Fetch products from backend
  useEffect(() => {
    fetch("http://localhost:8000/products")
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        setFilteredProducts(data)
      })
      .catch(err => console.error("Error loading products", err))
  }, [])

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Filter products on search
  useEffect(() => {
    const filtered = products.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase())
    )
    setFilteredProducts(filtered)
  }, [search, products])

  // Analyze product (click or send)
  async function analyzeProduct(productName) {
    const userMessage = { type: 'user', text: productName }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/analyze_product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName })
      })

      const data = await res.json()
      const botMessage = { type: 'bot', data }
      setMessages(prev => [...prev, botMessage])

    } catch (err) {
      setMessages(prev => [...prev, {
        type: 'bot',
        data: {
          detected_allergens: [],
          risk_level: 'Error',
          ethical_score: 0,
          recommendations: [err.message]
        }
      }])
    } finally {
      setLoading(false)
    }
  }

  // Sending text manually
  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim()) return
    analyzeProduct(input)
    setInput('')
  }

  return (
    <div className="layout">
      <div className='mt-20'></div>
         <aside className="products-panel fixed left-0 top-0 w-80 h-screen bg-white p-4 flex flex-col shadow-lg z-10">
{/* Title */}
  <div className="mb-2">
    <h2 className="text-xl font-bold">Products</h2>
  </div>

  {/* Search */}
  <div className="mb-3">
    <input
      type="text"
      placeholder="Search products..."
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      className="
        w-full 
        px-4 py-2 
        rounded-lg 
        border border-gray-300 
        focus:outline-none focus:ring-2 focus:ring-blue-500 
        focus:border-blue-500
        shadow-sm
        placeholder-gray-400
        transition
        duration-200
      "
    />
  </div>

  {/* Scrollable Products List */}
  <div className="flex-1 overflow-y-auto">
    {filteredProducts.length === 0 && <p className="text-gray-500">No products found.</p>}

    {filteredProducts.map((p, i) => (
      <div
        key={i}
        className="product-card cursor-pointer p-3 mb-2 bg-gray-50 rounded-lg hover:bg-blue-50 transition"
        onClick={() => analyzeProduct(p.name)}
      >
        <p className="font-medium">{p.name}</p>
      </div>
    ))}
  </div>
</aside>


      {/* Right: Chat */}
      <div className="chat-app">
        <header className="chat-header">
          <img src={logoUrl} alt="Logo" className="logo" />
          <h1>AllerPredict</h1>
        </header>

        <div className="chat-window">
          {messages.map((msg, i) =>
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
          )}
          <div ref={chatEndRef}></div>
        </div>

        <form className="chat-input" onSubmit={handleSend}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter product name..."
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Analyzing...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}
