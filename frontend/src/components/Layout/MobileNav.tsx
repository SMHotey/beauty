import { Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  ScissorsIcon,
  UserIcon,
  PhoneIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import {
  HomeIcon as HomeSolid,
  ScissorsIcon as ScissorsSolid,
  UserIcon as UserSolid,
  PhoneIcon as PhoneSolid,
  SparklesIcon as SparklesSolid,
} from '@heroicons/react/24/solid'

const navItems = [
  { path: '/', label: 'Главная', icon: HomeIcon, activeIcon: HomeSolid },
  { path: '/services', label: 'Услуги', icon: ScissorsIcon, activeIcon: ScissorsSolid },
  { path: '/promotions', label: 'Акции', icon: SparklesIcon, activeIcon: SparklesSolid },
  { path: '/contacts', label: 'Контакты', icon: PhoneIcon, activeIcon: PhoneSolid },
  { path: '/profile', label: 'Профиль', icon: UserIcon, activeIcon: UserSolid },
]

export default function MobileNav() {
  const location = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-gray-100/50 md:hidden safe-area-bottom">
      <div className="flex items-center justify-around h-16 pb-1">
        {navItems.map(({ path, label, icon: Icon, activeIcon: ActiveIcon }) => {
          const isActive = path === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(path)
          return (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center justify-center flex-1 h-full gap-0.5 transition-colors ${
                isActive ? 'text-primary-500' : 'text-gray-400 hover:text-gray-500'
              }`}
            >
              {isActive ? (
                <ActiveIcon className="w-6 h-6" />
              ) : (
                <Icon className="w-6 h-6" />
              )}
              <span className="text-xs font-medium">{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
