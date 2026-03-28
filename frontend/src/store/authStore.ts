import { create } from 'zustand'

interface User {
  id: string
  email: string
  full_name: string
  role: 'hr' | 'applicant'
  company?: string
}

interface AuthState {
  user: User | null
  token: string | null
  setAuth: (user: User, token: string) => void
  logout: () => void
  isHR: () => boolean
  isApplicant: () => boolean
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token'),

  setAuth: (user, token) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({ user, token })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  isHR: () => get().user?.role === 'hr',
  isApplicant: () => get().user?.role === 'applicant',
}))