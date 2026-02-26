/**
 * Filters for ticket list: status, priority, search.
 */
import type { TicketFilters as Filters } from '../types'

const STATUS_OPTIONS = ['', 'Open', 'In Progress', 'Resolved']
const PRIORITY_OPTIONS = ['', 'Low', 'Medium', 'High', 'Critical']

interface TicketFiltersProps {
  filters: Filters
  onFiltersChange: (f: Filters) => void
}

export function TicketFilters({ filters, onFiltersChange }: TicketFiltersProps) {
  const update = (key: keyof Filters, value: string) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  return (
    <div className="flex flex-wrap items-center gap-4 mb-4">
      <input
        type="text"
        placeholder="Search by title..."
        value={filters.search}
        onChange={(e) => update('search', e.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm w-56 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
      <select
        value={filters.status}
        onChange={(e) => update('status', e.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
      >
        {STATUS_OPTIONS.map((s) => (
          <option key={s || 'all'} value={s}>
            {s || 'All statuses'}
          </option>
        ))}
      </select>
      <select
        value={filters.priority}
        onChange={(e) => update('priority', e.target.value)}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
      >
        {PRIORITY_OPTIONS.map((p) => (
          <option key={p || 'all'} value={p}>
            {p || 'All priorities'}
          </option>
        ))}
      </select>
    </div>
  )
}
