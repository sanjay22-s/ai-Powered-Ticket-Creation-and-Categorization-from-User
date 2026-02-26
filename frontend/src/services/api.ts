/**
 * Axios API client with JWT and error handling.
 */
import axios, { AxiosError } from 'axios'

const API_BASE = '/api'

function getToken(): string | null {
  return localStorage.getItem('token')
}

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally (e.g. redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// --- Auth ---
export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    name: string
    email: string
    role: string
    created_at?: string
  }
}

export function login(data: LoginRequest) {
  return api.post<TokenResponse>('/auth/login', data)
}

export function getMe() {
  return api.get<TokenResponse['user']>('/auth/me')
}

// --- Dashboard ---
export function getDashboardStats() {
  return api.get<import('../types').DashboardStats>('/dashboard/stats')
}

// --- Tickets ---
export interface TicketListParams {
  skip?: number
  limit?: number
  status?: string
  priority?: string
  category?: string
  search?: string
}

export function getTickets(params?: TicketListParams) {
  return api.get<import('../types').TicketListItem[]>('/tickets', { params })
}

export function getTicket(id: number) {
  return api.get<import('../types').TicketDetail>(`/tickets/${id}`)
}

export function updateTicket(id: number, data: import('../types').TicketUpdatePayload) {
  return api.put<import('../types').TicketDetail>(`/tickets/${id}`, data)
}

export function addTicketNote(id: number, note: string) {
  return api.post<import('../types').TicketNote>(`/tickets/${id}/notes`, { note })
}

export function assignTicket(id: number, assignedTo: number | null) {
  return api.put<import('../types').TicketDetail>(`/tickets/${id}/assign`, { assigned_to: assignedTo })
}
