import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowUp } from 'lucide-react'
import Message from './Message'
import { queryAgent } from '../services/api'
import { staggerContainer, listItem, fadeInUp, buttonHover, buttonTap } from '../utils/motion'

const SUGGESTIONS = [
  'Show me all orders from Ohio over $500',
  'Who ordered laptops or gaming PCs?',
  'Orders under $100',
]

export default function ChatPanel({ messages, setMessages, onResult, isLoading, setIsLoading }) {
  const [input, setInput] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
  }, [input])

  const handleSubmit = async (query) => {
    const q = query || input.trim()
    if (!q || isLoading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setIsLoading(true)

    try {
      const result = await queryAgent(q)
      const summary = result.success
        ? `Found ${result.total_matched} of ${result.total_parsed} orders.${
            Object.keys(result.filters_applied || {}).length > 0
              ? ` Filters: ${Object.entries(result.filters_applied).map(([k, v]) => `${k}=${v}`).join(', ')}`
              : ''
          }`
        : `Error: ${result.error}`

      setMessages(prev => [...prev, { role: 'assistant', content: summary, result }])
      onResult(result)
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}. Make sure the backend is running (python main.py).`,
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-lg font-semibold text-text-primary mb-8">Ask about customer orders</h2>
            <motion.div
              variants={staggerContainer(0.06, 0.2)}
              initial="hidden"
              animate="visible"
              className="flex flex-wrap justify-center gap-2"
            >
              {SUGGESTIONS.map((s) => (
                <motion.button
                  key={s}
                  variants={listItem}
                  whileHover={buttonHover}
                  whileTap={buttonTap}
                  onClick={() => handleSubmit(s)}
                  className="px-3.5 py-2 rounded-full text-xs font-medium bg-surface border border-border text-text-secondary hover:text-text-primary hover:border-border-hover transition-all duration-150"
                >
                  {s}
                </motion.button>
              ))}
            </motion.div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, i) => (
            <Message key={i} {...msg} />
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            className="flex gap-3"
          >
            <div className="message-assistant">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 px-6 pb-6">
        <motion.div
          className="flex items-end bg-surface rounded-3xl border border-border"
          animate={{
            boxShadow: isFocused
              ? '0 0 0 3px rgba(59, 130, 246, 0.1)'
              : '0 0 0 0px rgba(59, 130, 246, 0)',
          }}
          transition={{ duration: 0.2 }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask about orders..."
            rows={1}
            className="flex-1 bg-transparent px-6 py-5 text-base text-text-primary placeholder:text-text-tertiary resize-none focus:outline-none min-h-[64px] max-h-[200px]"
          />
          <motion.button
            whileHover={buttonHover}
            whileTap={buttonTap}
            onClick={() => handleSubmit()}
            disabled={!input.trim() || isLoading}
            className="shrink-0 p-3 m-2 rounded-full bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            <ArrowUp size={18} className="text-white" />
          </motion.button>
        </motion.div>
      </div>
    </div>
  )
}
