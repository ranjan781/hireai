import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Register from './pages/Register'
import HRDashboard from './pages/HRDashboard'
import ApplicantDashboard from './pages/ApplicantDashboard'

function ProtectedRoute({ children, role }: { children: React.ReactNode, role: string }) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== role) return <Navigate to={user.role === 'hr' ? '/hr' : '/applicant'} replace />
  return <>{children}</>
}

export default function App() {
  const { user } = useAuthStore()
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={
          user
            ? <Navigate to={user.role === 'hr' ? '/hr' : '/applicant'} replace />
            : <Navigate to="/login" replace />
        }/>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/hr/*" element={
          <ProtectedRoute role="hr">
            <HRDashboard />
          </ProtectedRoute>
        }/>
        <Route path="/applicant/*" element={
          <ProtectedRoute role="applicant">
            <ApplicantDashboard />
          </ProtectedRoute>
        }/>
      </Routes>
    </BrowserRouter>
  )
}