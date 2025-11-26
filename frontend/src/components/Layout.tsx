import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../contexts/ThemeContext'
import { Sun, Moon } from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/upload', label: 'File Upload' },
  { to: '/tracking-script', label: 'Tracking Script' },
]

const Layout = () => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200">
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-rose-400">UserInsight AI</p>
            <h1 className="text-lg font-semibold">Behaviour Analytics</h1>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-600 dark:text-slate-300">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `transition-colors hover:text-rose-600 dark:hover:text-white ${
                    isActive ? 'text-rose-500 dark:text-rose-300 font-medium' : ''
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
            <button
              onClick={toggleTheme}
              className="rounded-lg border border-slate-300 dark:border-slate-700 p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-yellow-400" />
              ) : (
                <Moon className="w-4 h-4 text-slate-700" />
              )}
            </button>
            <div className="hidden flex-col text-right text-xs text-slate-500 dark:text-slate-500 sm:flex">
              <span className="text-sm text-slate-700 dark:text-slate-200">{user?.name}</span>
              <span>{user?.email}</span>
            </div>
            <button
              onClick={logout}
              className="rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-1 text-sm hover:border-rose-500 hover:text-rose-500 dark:hover:text-rose-300 transition-colors"
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

