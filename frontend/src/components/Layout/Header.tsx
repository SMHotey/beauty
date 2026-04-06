import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import {
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline'
import { RootState, useAppDispatch } from '../../store'
import { logout } from '../../store/authSlice'

const navLinks = [
  { to: '/', label: 'Главная' },
  { to: '/services', label: 'Услуги' },
  { to: '/masters', label: 'Мастера' },
  { to: '/promotions', label: 'Акции' },
  { to: '/contacts', label: 'Контакты' },
]

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleLogout = async () => {
    await dispatch(logout())
    navigate('/')
  }

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-xl shadow-soft border-b border-gray-100/50'
          : 'bg-white/80 backdrop-blur-md border-b border-gray-100/30'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-18">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-rose-500 flex items-center justify-center shadow-lg shadow-primary-500/20 group-hover:shadow-primary-500/30 transition-shadow">
              <span className="text-white font-bold text-sm">B</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-500 to-rose-500 bg-clip-text text-transparent">
              Beauty
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="px-4 py-2 text-gray-600 hover:text-primary-600 font-medium transition-colors text-sm rounded-xl hover:bg-primary-50/50"
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* Desktop Auth */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="flex items-center gap-2 text-gray-700 hover:text-primary-600 transition-colors text-sm font-medium px-3 py-2 rounded-xl hover:bg-primary-50/50"
                >
                  <UserCircleIcon className="w-5 h-5" />
                  <span>{user?.first_name || 'Профиль'}</span>
                </Link>
                {user?.is_staff && (
                  <Link
                    to="/admin"
                    className="text-sm font-medium text-primary-500 hover:text-primary-600 transition-colors px-3 py-2 rounded-xl hover:bg-primary-50/50"
                  >
                    Админ
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-gray-400 hover:text-red-500 transition-colors text-sm px-3 py-2 rounded-xl hover:bg-red-50/50"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5" />
                  <span>Выйти</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-primary-600 px-4 py-2.5 transition-colors">
                  Войти
                </Link>
                <Link to="/register" className="btn-primary text-sm px-6 py-2.5">
                  Регистрация
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50/50 rounded-xl transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? (
              <XMarkIcon className="w-6 h-6" />
            ) : (
              <Bars3Icon className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-100/50 bg-white/95 backdrop-blur-xl animate-fade-in-down">
          <div className="px-4 py-4 space-y-1">
            {navLinks.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className="block text-gray-700 hover:text-primary-600 hover:bg-primary-50/50 font-medium py-3 px-4 rounded-xl transition-colors text-base"
              >
                {label}
              </Link>
            ))}
            <div className="pt-4 mt-2 border-t border-gray-100/50 space-y-2">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/profile"
                    onClick={() => setMobileOpen(false)}
                    className="flex items-center gap-2 justify-center btn-secondary text-sm"
                  >
                    <UserCircleIcon className="w-5 h-5" />
                    Профиль
                  </Link>
                  {user?.is_staff && (
                    <Link
                      to="/admin"
                      onClick={() => setMobileOpen(false)}
                      className="block text-center text-sm font-medium text-primary-500 py-3"
                    >
                      Админ-панель
                    </Link>
                  )}
                  <button
                    onClick={() => {
                      handleLogout()
                      setMobileOpen(false)
                    }}
                    className="block w-full text-center text-sm text-red-500 py-3 hover:bg-red-50/50 rounded-xl transition-colors"
                  >
                    Выйти
                  </button>
                </>
              ) : (
                <div className="flex gap-3">
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="flex-1 text-center btn-secondary text-sm"
                  >
                    Войти
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileOpen(false)}
                    className="flex-1 text-center btn-primary text-sm"
                  >
                    Регистрация
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
