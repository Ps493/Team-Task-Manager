import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/', label: '📊 Dashboard' },
    { to: '/projects', label: '📁 Projects' },
    { to: '/tasks', label: '📋 Tasks' },
  ]

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
        <div className="p-5 border-b border-gray-800">
          <div className="text-lg font-bold text-white">TaskFlow</div>
          <div className="text-xs text-gray-500 mt-0.5">Team Task Manager</div>
        </div>

        <nav className="flex-1 p-3 flex flex-col gap-1">
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="text-xs text-gray-400 truncate mb-1">{user?.name}</div>
          <div className="flex items-center justify-between">
            <span className={`text-[10px] px-1.5 py-0.5 rounded ${isAdmin ? 'bg-amber-900/50 text-amber-300' : 'bg-gray-800 text-gray-400'}`}>
              {user?.role}
            </span>
            <button onClick={handleLogout} className="text-xs text-gray-500 hover:text-red-400 transition-colors">
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}
