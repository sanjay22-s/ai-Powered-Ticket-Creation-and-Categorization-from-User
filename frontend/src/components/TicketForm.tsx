/**
 * Editable ticket fields for the ticket details page: status, priority, category.
 */
import type { TicketDetail, TicketUpdatePayload } from '../types'

const STATUS_OPTIONS = ['Open', 'In Progress', 'Resolved']
const PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']

interface TicketFormProps {
  ticket: TicketDetail
  onUpdate: (data: TicketUpdatePayload) => void
  saving?: boolean
}

export function TicketForm({ ticket, onUpdate, saving }: TicketFormProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
        <select
          value={ticket.status}
          onChange={(e) => onUpdate({ status: e.target.value })}
          disabled={saving}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm w-full max-w-xs focus:ring-2 focus:ring-primary-500"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
        <select
          value={ticket.priority}
          onChange={(e) => onUpdate({ priority: e.target.value })}
          disabled={saving}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm w-full max-w-xs focus:ring-2 focus:ring-primary-500"
        >
          {PRIORITY_OPTIONS.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
        <input
          type="text"
          value={ticket.category ?? ''}
          onChange={(e) => onUpdate({ category: e.target.value || undefined })}
          disabled={saving}
          placeholder="e.g. Billing, Technical"
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm w-full max-w-xs focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>
  )
}
