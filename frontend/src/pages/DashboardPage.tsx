/**
 * Dashboard: stats cards and ticket table with filters.
 */
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { getTickets, getDashboardStats } from '../services/api'
import type { TicketListItem, DashboardStats as Stats, TicketFilters } from '../types'
import { StatsCard } from '../components/StatsCard'
import { TicketTable } from '../components/TicketTable'
import { TicketFilters as TicketFiltersComponent } from '../components/TicketFilters'

const defaultFilters: TicketFilters = {
  status: '',
  priority: '',
  category: '',
  search: '',
}

export function DashboardPage() {
  const [tickets, setTickets] = useState<TicketListItem[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [filters, setFilters] = useState<TicketFilters>(defaultFilters)
  const [loadingTickets, setLoadingTickets] = useState(true)
  const [loadingStats, setLoadingStats] = useState(true)

  const loadStats = async () => {
    try {
      const { data } = await getDashboardStats()
      setStats(data)
    } catch {
      toast.error('Failed to load dashboard stats')
    } finally {
      setLoadingStats(false)
    }
  }

  const loadTickets = async () => {
    setLoadingTickets(true)
    try {
      const params: Record<string, string | number> = { skip: 0, limit: 50 }
      if (filters.status) params.status = filters.status
      if (filters.priority) params.priority = filters.priority
      if (filters.category) params.category = filters.category
      if (filters.search) params.search = filters.search
      const { data } = await getTickets(params)
      setTickets(data)
    } catch {
      toast.error('Failed to load tickets')
    } finally {
      setLoadingTickets(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  useEffect(() => {
    loadTickets()
  }, [filters])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {loadingStats ? (
          <>
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-24 bg-slate-200 rounded-xl animate-pulse" />
            ))}
          </>
        ) : stats ? (
          <>
            <StatsCard title="Total tickets" value={stats.total_tickets} accent="blue" />
            <StatsCard title="Open" value={stats.open_tickets} accent="yellow" />
            <StatsCard title="In progress" value={stats.in_progress} accent="blue" />
            <StatsCard title="Resolved" value={stats.resolved} accent="green" />
            <StatsCard title="High priority" value={stats.high_priority} accent="red" />
          </>
        ) : null}
      </div>

      {/* Filters + Table */}
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">Tickets</h2>
        <TicketFiltersComponent filters={filters} onFiltersChange={setFilters} />
        <TicketTable tickets={tickets} loading={loadingTickets} />
      </div>
    </div>
  )
}
