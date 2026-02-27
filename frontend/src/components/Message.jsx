import { motion } from 'framer-motion'
import { userMessage, assistantMessage } from '../utils/motion'

export default function Message({ role, content, result }) {
  const isUser = role === 'user'

  return (
    <motion.div
      variants={isUser ? userMessage : assistantMessage}
      initial="hidden"
      animate="visible"
      className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[85%] ${isUser ? 'message-user' : 'message-assistant'}`}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>

        {result && result.success && result.orders.length > 0 && (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-1.5 px-2 font-medium text-white/70">ID</th>
                  <th className="text-left py-1.5 px-2 font-medium text-white/70">Buyer</th>
                  <th className="text-left py-1.5 px-2 font-medium text-white/70">State</th>
                  <th className="text-right py-1.5 px-2 font-medium text-white/70">Total</th>
                  <th className="text-left py-1.5 px-2 font-medium text-white/70">Items</th>
                </tr>
              </thead>
              <tbody>
                {[...result.orders].sort((a, b) => a.order_id - b.order_id).map((order) => (
                  <tr key={order.order_id} className="border-b border-white/5">
                    <td className="py-1.5 px-2 font-mono font-semibold text-accent">{order.order_id}</td>
                    <td className="py-1.5 px-2 font-semibold text-white">{order.buyer}</td>
                    <td className="py-1.5 px-2 font-semibold text-white">{order.state}</td>
                    <td className="py-1.5 px-2 text-right font-mono font-semibold text-white">${order.total.toFixed(2)}</td>
                    <td className="py-1.5 px-2 font-semibold text-white/80">{order.items.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {result && result.validation_warnings?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {result.validation_warnings.map((w, i) => (
              <span key={i} className="badge badge-warning text-[10px]">{w}</span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
