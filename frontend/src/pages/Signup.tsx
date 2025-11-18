import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { signup as signupService } from '../services/auth'
import { useAuth } from '../hooks/useAuth'

const Signup = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
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
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-8 text-slate-100 shadow-2xl"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-rose-400">UserInsight AI</p>
          <h1 className="text-2xl font-semibold">Create an account</h1>
        </div>
        <label className="block text-sm">
          Name
          <input
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            value={form.name}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            required
          />
        </label>
        <label className="block text-sm">
          Email
          <input
            type="email"
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            value={form.email}
            onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
        </label>
        <label className="block text-sm">
          Password
          <input
            type="password"
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            value={form.password}
            onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
            required
          />
        </label>
        {mutation.isError && (
          <p className="text-sm text-rose-400">Unable to sign up. Try again.</p>
        )}
        <button
          type="submit"
          className="w-full rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white transition hover:bg-rose-400 disabled:opacity-50"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Creating account...' : 'Sign up'}
        </button>
        <p className="text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link className="text-rose-300" to="/login">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  )
}

export default Signup

