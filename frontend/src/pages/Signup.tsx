import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { signup as signupService } from '../services/auth'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../contexts/ThemeContext'
import { Sun, Moon } from 'lucide-react'

const Signup = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const mutation = useMutation({
    mutationFn: signupService,
    onSuccess: (data) => {
      login(data)
      navigate('/')
    },
  })

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    mutation.mutate(form)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 transition-colors duration-200">
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 rounded-lg border border-slate-300 dark:border-slate-700 p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors bg-white dark:bg-slate-900 shadow-md"
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-yellow-400" />
        ) : (
          <Moon className="w-5 h-5 text-slate-700" />
        )}
      </button>
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/70 p-8 text-slate-900 dark:text-slate-100 shadow-2xl"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-rose-400">UserInsight AI</p>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Create an account</h1>
        </div>
        <label className="block text-sm text-slate-700 dark:text-slate-300">
          Name
          <input
            className="mt-1 w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-colors"
            value={form.name}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            required
          />
        </label>
        <label className="block text-sm text-slate-700 dark:text-slate-300">
          Email
          <input
            type="email"
            className="mt-1 w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-colors"
            value={form.email}
            onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
        </label>
        <label className="block text-sm text-slate-700 dark:text-slate-300">
          Password
          <input
            type="password"
            className="mt-1 w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-colors"
            value={form.password}
            onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
            required
          />
        </label>
        {mutation.isError && (
          <p className="text-sm text-rose-600 dark:text-rose-400">Unable to sign up. Try again.</p>
        )}
        <button
          type="submit"
          className="w-full rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white transition-all hover:bg-rose-400 disabled:opacity-50 shadow-md hover:shadow-lg"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Creating account...' : 'Sign up'}
        </button>
        <p className="text-center text-sm text-slate-600 dark:text-slate-400">
          Already have an account?{' '}
          <Link className="text-rose-600 dark:text-rose-300 hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  )
}

export default Signup

