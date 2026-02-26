/**
 * Shared TypeScript types for the Agent Dashboard.
 */

export interface User {
  id: number
  name: string
  email: string
  role: string
  created_at?: string
}

export type TicketStatus = 'Open' | 'In Progress' | 'Resolved'
export type TicketPriority = 'Low' | 'Medium' | 'High' | 'Critical'

export interface TicketListItem {
  id: number
  title: string
  category: string | null
  priority: string
  status: string
  created_at: string
  assigned_to: number | null
  assignee_name: string | null
}

export interface TicketNote {
  id: number
  ticket_id: number
  agent_id: number
  note: string
  created_at: string
  agent_name: string | null
}

export interface TicketDetail {
  id: number
  title: string
  description: string | null
  category: string | null
  priority: string
  status: string
  created_by: number | null
  assigned_to: number | null
  created_at: string
  updated_at: string | null
  creator_name: string | null
  assignee_name: string | null
  notes: TicketNote[]
}

export interface DashboardStats {
  total_tickets: number
  open_tickets: number
  in_progress: number
  resolved: number
  high_priority: number
}

export interface TicketFilters {
  status: string
  priority: string
  category: string
  search: string
}

export interface TicketUpdatePayload {
  title?: string
  description?: string
  category?: string
  priority?: string
  status?: string
}
