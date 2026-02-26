/**
 * Login page: email/password, store JWT, redirect after login.
 */
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim() || !password) {
      toast.error('Please enter email and password')
      return
    }
    try {
      await login(email.trim(), password)
      toast.success('Logged in successfully')
      navigate(from, { replace: true })
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string | Array<{ msg?: string }> }; status?: number } }
      const detail = ax.response?.data?.detail
      let msg = 'Login failed'
      if (typeof detail === 'string') msg = detail
      else if (Array.isArray(detail) && detail[0]?.msg) msg = detail.map((d) => d.msg).join(', ')
      else if (ax.response?.status === 500) msg = 'Server error. Is the database running?'
      else if (ax.response?.status === 403) msg = 'Access denied'
      toast.error(msg)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <h1 className="text-2xl font-bold text-slate-800 text-center">Agent Dashboard</h1>
          <p className="text-slate-500 text-center mt-1 text-sm">Sign in to manage tickets</p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="agent@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
            <p className="text-center text-xs text-slate-500 mt-4">
              Demo: agent@example.com / agent123 (run seed script first)
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
