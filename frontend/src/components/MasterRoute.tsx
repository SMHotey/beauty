import { useEffect } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { RootState, useAppDispatch } from '../store'
import { fetchProfile } from '../store/authSlice'

export default function MasterRoute({ children }: { children?: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth)
  const dispatch = useAppDispatch()

  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchProfile())
    }
  }, [isAuthenticated, user, dispatch])

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" /></div>
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  if (user.is_staff || user.is_superuser) {
    return <Navigate to="/admin" replace />
  }

  if (children) return <>{children}</>
  return <Outlet />
}
