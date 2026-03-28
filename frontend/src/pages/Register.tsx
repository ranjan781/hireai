import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuthStore } from '../store/authStore'

export default function Register() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const [form, setForm] = useState({
    email: '', full_name: '', password: '',
    role: 'applicant' as 'hr' | 'applicant', company: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = {
        ...form,
        company: form.role === 'hr' ? form.company : undefined
      }
      const res = await api.post('/auth/register', payload)
      setAuth(res.data.user, res.data.access_token)
      navigate(res.data.user.role === 'hr' ? '/hr' : '/applicant')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-hr-accent to-ap-accent bg-clip-text text-transparent">
            HireAI
          </h1>
          <p className="text-muted mt-2">Create your account</p>
        </div>

        <div className="bg-card border border-border rounded-2xl p-8">
          <h2 className="text-xl font-semibold mb-6">Register</h2>

          {error && (
            <div className="bg-red-900/20 border border-red-500/30 text-red-400 rounded-lg p-3 mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            {/* Role Toggle */}
            <div className="flex bg-surface rounded-lg p-1 border border-border">
              {(['applicant', 'hr'] as const).map(r => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setForm({...form, role: r})}
                  className={`flex-1 py-2 rounded-md text-sm font-bold transition ${
                    form.role === r
                      ? r === 'hr'
                        ? 'bg-hr-accent text-black'
                        : 'bg-ap-accent text-black'
                      : 'text-muted'
                  }`}
                >
                  {r === 'hr' ? 'I am HR' : 'I am Applicant'}
                </button>
              ))}
            </div>

            <input
              type="text"
              placeholder="Full Name"
              value={form.full_name}
              onChange={e => setForm({...form, full_name: e.target.value})}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-hr-accent"
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={e => setForm({...form, email: e.target.value})}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-hr-accent"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={e => setForm({...form, password: e.target.value})}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-hr-accent"
              required
            />
            {form.role === 'hr' && (
              <input
                type="text"
                placeholder="Company Name"
                value={form.company}
                onChange={e => setForm({...form, company: e.target.value})}
                className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-hr-accent"
              />
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-hr-accent text-black font-bold py-3 rounded-lg hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-muted text-sm mt-4">
            Already have account?{' '}
            <span
              onClick={() => navigate('/login')}
              className="text-hr-accent cursor-pointer hover:underline"
            >
              Login
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}