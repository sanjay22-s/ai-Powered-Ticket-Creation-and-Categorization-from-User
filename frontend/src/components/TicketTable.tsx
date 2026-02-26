/**
 * Ticket list table: ID, Title, Category, Priority, Status, Assigned, Actions.
 */
import { Link } from 'react-router-dom'
import type { TicketListItem } from '../types'
import { PriorityBadge } from './PriorityBadge'

interface TicketTableProps {
  tickets: TicketListItem[]
  loading?: boolean
}

export function TicketTable({ tickets, loading }: TicketTableProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="p-8 flex justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-500 border-t-transparent" />
        </div>
      </div>
    )
  }

  if (tickets.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500">
        No tickets match your filters.
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">ID</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Title</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Category</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Priority</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Assigned</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {tickets.map((t) => (
              <tr key={t.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm text-slate-600">{t.id}</td>
                <td className="px-4 py-3">
                  <Link
                    to={`/tickets/${t.id}`}
                    className="text-sm font-medium text-primary-600 hover:underline"
                  >
                    {t.title}
                  </Link>
                </td>
                <td className="px-4 py-3 text-sm text-slate-600">{t.category || '—'}</td>
                <td className="px-4 py-3">
                  <PriorityBadge priority={t.priority} />
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-slate-700">{t.status}</span>
                </td>
                <td className="px-4 py-3 text-sm text-slate-600">{t.assignee_name || '—'}</td>
                <td className="px-4 py-3 text-right">
                  <Link
                    to={`/tickets/${t.id}`}
                    className="text-sm font-medium text-primary-600 hover:underline"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
