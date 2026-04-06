import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { RootState, useAppDispatch } from '../store'
import {
  CalendarDaysIcon,
  HeartIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline'
import { logout } from '../store/authSlice'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user } = useSelector((state: RootState) => state.auth)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleLogout = () => {
    dispatch(logout())
    toast.success('Вы вышли из аккаунта')
    navigate('/')
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Профиль</h1>

      <div className="card mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center text-primary-500 text-2xl font-bold">
            {user?.first_name?.[0] || '?'}
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.first_name} {user?.last_name}
            </h2>
            <p className="text-gray-500">{user?.phone}</p>
          </div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4 mb-6">
        <Link to="/profile/appointments" className="card flex items-center gap-4 hover:border-primary-200 group cursor-pointer">
          <CalendarDaysIcon className="w-8 h-8 text-primary-500" />
          <div>
            <p className="font-medium text-gray-900 group-hover:text-primary-500 transition-colors">Мои записи</p>
            <p className="text-sm text-gray-500">История и предстоящие визиты</p>
          </div>
        </Link>
        <Link to="/profile/favorites" className="card flex items-center gap-4 hover:border-primary-200 group cursor-pointer">
          <HeartIcon className="w-8 h-8 text-primary-500" />
          <div>
            <p className="font-medium text-gray-900 group-hover:text-primary-500 transition-colors">Избранное</p>
            <p className="text-sm text-gray-500">Любимые мастера</p>
          </div>
        </Link>
      </div>

      {user?.is_staff && (
        <Link to="/admin" className="card mb-6 flex items-center gap-4 hover:border-primary-200 group cursor-pointer border-primary-200 bg-primary-50">
          <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">
            A
          </div>
          <div>
            <p className="font-medium text-gray-900">Админ-панель</p>
            <p className="text-sm text-gray-500">Управление салоном</p>
          </div>
        </Link>
      )}

      <button
        onClick={handleLogout}
        className="flex items-center gap-2 text-red-500 hover:text-red-600 font-medium"
      >
        <ArrowRightOnRectangleIcon className="w-5 h-5" />
        <span>Выйти из аккаунта</span>
      </button>
    </div>
  )
}
