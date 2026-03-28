import { useState, useEffect, useRef } from 'react'
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

interface NavbarProps {
  role: 'hr' | 'applicant'
}

interface Notification {
  id: string
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export default function Navbar({ role }: NavbarProps) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [showNotifs, setShowNotifs] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const dropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchUnreadCount()
    const interval = setInterval(fetchUnreadCount, 30000) // 30s poll
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) {
        setShowNotifs(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const fetchUnreadCount = async () => {
    try {
      const r = await api.get('/notifications/unread-count')
      setUnreadCount(r.data.count)
    } catch {}
  }

  const fetchNotifications = async () => {
    try {
      const r = await api.get('/notifications')
      setNotifications(r.data)
    } catch {}
  }

  const toggleNotifs = async () => {
    if (!showNotifs) {
      await fetchNotifications()
      if (unreadCount > 0) {
        await api.patch('/notifications/read-all')
        setUnreadCount(0)
      }
    }
    setShowNotifs(!showNotifs)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const typeColors: Record<string, string> = {
    success: 'border-l-green-400 bg-green-400/5',
    info: 'border-l-blue-400 bg-blue-400/5',
    warning: 'border-l-yellow-400 bg-yellow-400/5',
    error: 'border-l-red-400 bg-red-400/5',
  }

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return 'Just now'
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return `${Math.floor(hrs / 24)}d ago`
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-surface/90 backdrop-blur-md">
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold bg-gradient-to-r from-hr-accent to-ap-accent bg-clip-text text-transparent">
            HireAI
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            role === 'hr'
              ? 'bg-green-400/10 text-green-400 border border-green-400/20'
              : 'bg-blue-400/10 text-blue-400 border border-blue-400/20'
          }`}>
            {role === 'hr' ? 'HR Portal' : 'Applicant Portal'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Notification Bell */}
          <div className="relative" ref={dropRef}>
            <button
              onClick={toggleNotifs}
              className="relative w-9 h-9 rounded-xl hover:bg-card flex items-center justify-center transition text-muted hover:text-white"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-danger text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Dropdown */}
            {showNotifs && (
              <div className="absolute right-0 top-11 w-80 bg-card border border-border rounded-2xl shadow-xl overflow-hidden">
                <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                  <p className="font-semibold text-sm">Notifications</p>
                  <button onClick={() => setShowNotifs(false)} className="text-muted hover:text-white text-lg leading-none">×</button>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="py-8 text-center text-muted text-sm">No notifications yet</div>
                  ) : (
                    notifications.map(n => (
                      <div key={n.id} className={`px-4 py-3 border-b border-border/50 border-l-2 ${typeColors[n.type] || typeColors.info} last:border-b-0`}>
                        <p className="text-sm font-medium">{n.title}</p>
                        <p className="text-xs text-muted mt-0.5 leading-relaxed">{n.message}</p>
                        <p className="text-xs text-muted/60 mt-1">{timeAgo(n.created_at)}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Avatar + Name */}
          <div className="flex items-center gap-2 pl-1">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
              role === 'hr' ? 'bg-green-400/20 text-green-400' : 'bg-blue-400/20 text-blue-400'
            }`}>
              {user?.full_name?.[0]?.toUpperCase()}
            </div>
            <span className="text-sm text-muted hidden sm:block">{user?.full_name}</span>
          </div>

          <button
            onClick={handleLogout}
            className="text-sm text-muted hover:text-white transition px-3 py-1.5 rounded-lg hover:bg-card"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}