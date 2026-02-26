/**
 * Top navbar with user menu and logout.
 */
import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div className="text-slate-600 font-medium">Support Agent Portal</div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">
          {user?.name} <span className="text-slate-400">({user?.role})</span>
        </span>
        <button
          type="button"
          onClick={handleLogout}
          className="text-sm text-slate-600 hover:text-red-600 font-medium"
        >
          Logout
        </button>
      </div>
    </header>
  )
}
