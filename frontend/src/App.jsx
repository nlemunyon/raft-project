import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BarChart3 } from 'lucide-react'
import ChatPanel from './components/ChatPanel'
import ResultsPanel from './components/ResultsPanel'
import StatsPanel from './components/StatsPanel'
import { fadeIn } from './utils/motion'

export default function App() {
  const [messages, setMessages] = useState([])
  const [latestResult, setLatestResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [rightTab, setRightTab] = useState('results')

  const handleResult = useCallback((result) => {
    setLatestResult(result)
    setRightTab('results')
  }, [])

  return (
    <div className="h-screen flex flex-col bg-primary overflow-hidden">
      {/* Header */}
      <header className="shrink-0 border-b border-border h-16 px-6 flex items-center justify-between">
        <div>
          <h1 className="text-sm font-semibold text-text-primary">Noah LeMunyon Raft Project</h1>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setRightTab('results')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
              rightTab === 'results'
                ? 'bg-accent-muted text-accent'
                : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-hover'
            }`}
          >
            Results
          </button>
          <button
            onClick={() => setRightTab('stats')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 flex items-center gap-1.5 ${
              rightTab === 'stats'
                ? 'bg-accent-muted text-accent'
                : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-hover'
            }`}
          >
            <BarChart3 size={13} />
            ML Stats
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex min-h-0">
        {/* Left: Chat */}
        <div className="w-[70%] border-r border-border flex flex-col">
          <ChatPanel
            messages={messages}
            setMessages={setMessages}
            onResult={handleResult}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        </div>

        {/* Right: Results or Stats */}
        <div className="w-[30%] flex flex-col min-h-0">
          <AnimatePresence mode="wait">
            {rightTab === 'results' ? (
              <motion.div
                key="results"
                variants={fadeIn}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="flex-1 min-h-0"
              >
                <ResultsPanel result={latestResult} />
              </motion.div>
            ) : (
              <motion.div
                key="stats"
                variants={fadeIn}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="flex-1 min-h-0"
              >
                <StatsPanel />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
