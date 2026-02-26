/**
 * Auth context: current user and login/logout.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { getMe, login as apiLogin, TokenResponse } from '../services/api'
import type { User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  initialized: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const TOKEN_KEY = 'token'
const USER_KEY = 'user'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem(TOKEN_KEY),
    loading: false,
    initialized: false,
  })

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setState((s) => ({ ...s, user: null, initialized: true }))
      return
    }
    try {
      const { data } = await getMe()
      setState((s) => ({ ...s, user: data, initialized: true }))
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      setState((s) => ({ ...s, user: null, token: null, initialized: true }))
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = useCallback(async (email: string, password: string) => {
    setState((s) => ({ ...s, loading: true }))
    try {
      const { data } = await apiLogin({ email, password })
      localStorage.setItem(TOKEN_KEY, data.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(data.user))
      setState({
        user: data.user,
        token: data.access_token,
        loading: false,
        initialized: true,
      })
    } finally {
      setState((s) => ({ ...s, loading: false }))
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setState({ user: null, token: null, loading: false, initialized: true })
  }, [])

  const setUser = useCallback((user: User | null) => {
    setState((s) => ({ ...s, user }))
  }, [])

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
    setUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (ctx === undefined) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
