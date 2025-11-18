import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/upload', label: 'File Upload' },
  { to: '/tracking-script', label: 'Tracking Script' },
]

const Layout = () => {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/60">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-rose-400">UserInsight AI</p>
            <h1 className="text-lg font-semibold">Behaviour Analytics</h1>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-300">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `transition-colors hover:text-white ${isActive ? 'text-rose-300' : ''}`
                }
              >
                {link.label}
              </NavLink>
            ))}
            <div className="hidden flex-col text-right text-xs text-slate-500 sm:flex">
              <span className="text-sm text-slate-200">{user?.name}</span>
              <span>{user?.email}</span>
            </div>
            <button
              onClick={logout}
              className="rounded-lg border border-slate-700 px-3 py-1 text-sm hover:border-rose-500 hover:text-rose-300"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

