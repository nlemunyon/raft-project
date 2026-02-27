import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Table, Code, AlertTriangle, TrendingUp } from 'lucide-react'
import { fadeInUp, staggerContainer, listItem } from '../utils/motion'

export default function ResultsPanel({ result }) {
  const [tab, setTab] = useState('table')

  if (!result) {
    return (
      <div className="h-full flex items-center justify-center text-center px-6">
        <div>
          <div className="w-12 h-12 rounded-xl bg-surface border border-border flex items-center justify-center mx-auto mb-3">
            <Table size={20} className="text-text-tertiary" />
          </div>
          <p className="text-sm text-text-tertiary">Results will appear here after you submit a query.</p>
        </div>
      </div>
    )
  }

  if (!result.success) {
    return (
      <div className="h-full flex items-center justify-center px-6">
        <div className="card text-center max-w-sm">
          <AlertTriangle size={24} className="text-error mx-auto mb-2" />
          <p className="text-sm text-error">{result.error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Tab bar + summary */}
      <div className="shrink-0 px-4 pt-4 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setTab('table')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              tab === 'table' ? 'bg-accent-muted text-accent' : 'text-text-tertiary hover:text-text-secondary'
            }`}
          >
            <Table size={13} className="inline mr-1.5 -mt-0.5" />
            Results
          </button>
          <button
            onClick={() => setTab('raw')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              tab === 'raw' ? 'bg-accent-muted text-accent' : 'text-text-tertiary hover:text-text-secondary'
            }`}
          >
            <Code size={13} className="inline mr-1.5 -mt-0.5" />
            Raw JSON
          </button>
        </div>
        <span className="badge badge-accent">
          {result.total_matched} of {result.total_parsed} matched
        </span>
      </div>

      {/* Filters applied */}
      {Object.keys(result.filters_applied || {}).length > 0 && (
        <div className="px-4 pb-2 flex flex-wrap gap-1.5">
          {Object.entries(result.filters_applied).map(([k, v]) => (
            <span key={k} className="badge badge-accent text-[10px]">
              {k}: {String(v)}
            </span>
          ))}
        </div>
      )}

      {/* Validation warnings */}
      {result.validation_warnings?.length > 0 && (
        <div className="px-4 pb-2">
          <div className="p-2.5 rounded-xl bg-warning-muted border border-warning/20">
            <div className="flex items-center gap-1.5 mb-1">
              <AlertTriangle size={12} className="text-warning" />
              <span className="text-[11px] font-medium text-warning">Validation Warnings</span>
            </div>
            {result.validation_warnings.map((w, i) => (
              <p key={i} className="text-[11px] text-warning/80">{w}</p>
            ))}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto px-4 pb-4">
        <AnimatePresence mode="wait">
          {tab === 'table' ? (
            <motion.div
              key="table"
              variants={staggerContainer(0.03)}
              initial="hidden"
              animate="visible"
            >
              {result.orders.length === 0 ? (
                <p className="text-sm text-text-tertiary text-center py-8">No orders matched your filters.</p>
              ) : (
                <div className="space-y-2">
                  {[...result.orders].sort((a, b) => a.order_id - b.order_id).map((order) => {
                    const pred = result.ml_predictions?.find(p => p.order_id === order.order_id)
                    return (
                      <motion.div key={order.order_id} variants={listItem} className="card !p-3 border-l-2 border-l-accent">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm font-bold text-accent">#{order.order_id}</span>
                            <span className="text-sm text-text-primary font-bold">{order.buyer}</span>
                          </div>
                          <span className="font-mono text-sm font-bold text-text-primary">${order.total.toFixed(2)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-text-tertiary font-semibold">{order.city}, {order.state}</span>
                            <span className="text-xs text-text-tertiary">|</span>
                            <span className="text-xs text-text-secondary font-semibold">{order.items.join(', ')}</span>
                          </div>
                          {pred && (
                            <div className="flex items-center gap-1">
                              <TrendingUp size={11} className={pred.prediction === 'likely_reorder' ? 'text-success' : 'text-text-tertiary'} />
                              <span className={`text-[10px] font-medium ${
                                pred.prediction === 'likely_reorder' ? 'text-success' : 'text-text-tertiary'
                              }`}>
                                {(pred.reorder_probability * 100).toFixed(0)}% reorder
                              </span>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div key="raw" variants={fadeInUp} initial="hidden" animate="visible">
              <pre className="text-xs text-text-secondary font-mono bg-surface rounded-xl p-4 overflow-auto border border-border whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
