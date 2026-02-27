import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getStats } from '../services/api'
import { fadeInUp, staggerContainer, listItem } from '../utils/motion'

const FRIENDLY_NAMES = {
  num_items: '# of Items',
  has_electronics: 'Has Electronics',
  state_reorder_score: 'State Pattern',
  total_normalized: 'Order Total',
  electronics_x_spend: 'Electronics × Spend',
  avg_item_price: 'Avg Item Price',
}

function stateBarColor(rate) {
  if (rate >= 60) return 'bg-success'
  if (rate >= 45) return 'bg-accent'
  return 'bg-warning'
}

export default function StatsPanel() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center px-6">
        <div className="card text-center">
          <p className="text-sm text-error">{error}</p>
          <p className="text-xs text-text-tertiary mt-1">Make sure the backend is running.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto px-4 py-4 space-y-4">
      {/* 1. Model Overview */}
      <motion.div variants={fadeInUp} initial="hidden" animate="visible" className="card">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-text-primary">Reorder Prediction Model</span>
          <span className="badge badge-success">{stats.accuracy}% accuracy</span>
        </div>
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-surface-hover rounded-lg p-2.5">
            <span className="text-text-tertiary">Training samples</span>
            <p className="font-mono font-medium text-text-primary mt-0.5">{stats.training_samples}</p>
          </div>
          <div className="bg-surface-hover rounded-lg p-2.5">
            <span className="text-text-tertiary">Test samples</span>
            <p className="font-mono font-medium text-text-primary mt-0.5">{stats.test_samples}</p>
          </div>
        </div>
      </motion.div>

      {/* 2. Reorder by State */}
      {stats.state_reorder_rates && (
        <motion.div variants={fadeInUp} initial="hidden" animate="visible" className="card">
          <span className="text-sm font-semibold text-text-primary block mb-3">Reorder Rate by State</span>
          <motion.div variants={staggerContainer(0.03)} initial="hidden" animate="visible" className="space-y-2">
            {Object.entries(stats.state_reorder_rates)
              .sort(([, a], [, b]) => b - a)
              .map(([state, rate]) => (
                <motion.div key={state} variants={listItem}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-text-secondary font-mono font-medium">{state}</span>
                    <span className="text-text-tertiary">{rate}%</span>
                  </div>
                  <div className="h-2 bg-surface-hover rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${stateBarColor(rate)}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${rate}%` }}
                      transition={{ duration: 0.6, delay: 0.1 }}
                    />
                  </div>
                </motion.div>
              ))}
          </motion.div>
          <div className="flex items-center gap-3 mt-3 text-[10px] text-text-tertiary">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-success" />60%+</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-accent" />45-59%</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-warning" />&lt;45%</span>
          </div>
        </motion.div>
      )}

      {/* 3. Feature Importance */}
      <motion.div variants={fadeInUp} initial="hidden" animate="visible" className="card">
        <span className="text-sm font-semibold text-text-primary block mb-3">Feature Importance</span>
        <motion.div variants={staggerContainer(0.05)} initial="hidden" animate="visible" className="space-y-2.5">
          {Object.entries(stats.feature_importance)
            .sort(([, a], [, b]) => b - a)
            .map(([name, value]) => (
              <motion.div key={name} variants={listItem}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-text-secondary font-mono">{FRIENDLY_NAMES[name] || name}</span>
                  <span className="text-text-tertiary">{value}%</span>
                </div>
                <div className="h-2 bg-surface-hover rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-accent rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                  />
                </div>
              </motion.div>
            ))}
        </motion.div>
      </motion.div>

    </div>
  )
}
