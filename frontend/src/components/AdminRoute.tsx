import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { RootState } from '../store'

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)
  if (!isAuthenticated || (!user?.is_staff && !user?.is_superuser)) {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}
