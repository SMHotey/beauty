import { useEffect, useState } from 'react'
import api from '../../api/client'
import {
  CalendarDaysIcon,
  CurrencyDollarIcon,
  StarIcon,
  ChatBubbleLeftIcon,
} from '@heroicons/react/24/outline'
import { handleApiError } from '../../utils/apiErrors'

interface DashboardData {
  today_appointments: number
  week_appointments: number
  month_appointments: number
  today_revenue: string
  week_revenue: string
  month_revenue: string
  avg_rating: number | null
  review_count: number
}

export default function MasterDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/staff/master/dashboard/')
      .then((res) => setData(res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">{Array.from({ length: 4 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-28" />)}</div>
  if (!data) return <div className="text-center py-16 text-gray-500">Нет данных</div>

  const cards = [
    { label: 'Записей сегодня', value: data.today_appointments, icon: CalendarDaysIcon, color: 'text-blue-500', bg: 'bg-blue-50' },
    { label: 'Записей за неделю', value: data.week_appointments, icon: CalendarDaysIcon, color: 'text-purple-500', bg: 'bg-purple-50' },
    { label: 'Выручка сегодня', value: `${Number(data.today_revenue).toLocaleString('ru-RU')} ₽`, icon: CurrencyDollarIcon, color: 'text-green-500', bg: 'bg-green-50' },
    { label: 'Рейтинг', value: data.avg_rating ? `${data.avg_rating} ★` : '—', icon: StarIcon, color: 'text-amber-500', bg: 'bg-amber-50' },
  ]

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
        <p className="text-sm text-gray-500 mt-1">Ваша статистика</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${bg}`}><Icon className={`w-6 h-6 ${color}`} /></div>
              <div>
                <p className="text-xl font-bold text-gray-900">{value}</p>
                <p className="text-xs text-gray-500 mt-0.5">{label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Записей за месяц</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{data.month_appointments}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Выручка за месяц</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{Number(data.month_revenue).toLocaleString('ru-RU')} ₽</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Отзывов</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{data.review_count}</p>
        </div>
      </div>
    </div>
  )
}
