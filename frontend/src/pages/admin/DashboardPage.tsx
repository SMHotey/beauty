import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboardStats, getAdminAppointments } from '../../api/services'
import {
  CalendarDaysIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  UserIcon,
} from '@heroicons/react/24/outline'
import { handleApiError } from '../../utils/apiErrors'

interface DashboardStats {
  revenue: string
  appointments_count: number
  masters_count: number
  clients_count: number
  avg_check: string | null
  top_services: { name: string; count: number; revenue: string }[]
  master_load: { master_id: number; master_name: string; appointments_count: number; revenue: string }[]
}

interface RecentAppointment {
  id: number
  client_id: number | null
  client_name: string
  client_phone: string
  master_id: number
  master_name: string
  datetime_start: string
  status: string
  total_price: string
}

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  completed: 'Завершена',
  cancelled_by_client: 'Отменена клиентом',
  cancelled_by_admin: 'Отменена админом',
  no_show: 'Не явился',
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled_by_client: 'bg-red-100 text-red-700',
  cancelled_by_admin: 'bg-red-100 text-red-700',
  no_show: 'bg-gray-100 text-gray-700',
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentAppointments, setRecentAppointments] = useState<RecentAppointment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getDashboardStats().catch((e) => { handleApiError(e, 'Ошибка загрузки статистики'); return null }),
      getAdminAppointments({}).catch((e) => { handleApiError(e, 'Ошибка загрузки записей'); return null }),
    ])
      .then(([statsRes, apptsRes]) => {
        if (statsRes) setStats(statsRes.data)
        if (apptsRes) {
          const results = apptsRes.data.results || apptsRes.data || []
          setRecentAppointments(results.slice(0, 8))
        }
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse h-28" />
          ))}
        </div>
      </div>
    )
  }

  const cards = [
    { label: 'Записей за период', value: stats?.appointments_count || 0, icon: CalendarDaysIcon, color: 'text-blue-500', bg: 'bg-blue-50' },
    { label: 'Клиентов', value: stats?.clients_count || 0, icon: UserGroupIcon, color: 'text-purple-500', bg: 'bg-purple-50' },
    { label: 'Выручка', value: `${Number(stats?.revenue || 0).toLocaleString('ru-RU')} ₽`, icon: CurrencyDollarIcon, color: 'text-green-500', bg: 'bg-green-50' },
    { label: 'Средний чек', value: stats?.avg_check ? `${Number(stats.avg_check).toLocaleString('ru-RU')} ₽` : '—', icon: ChartBarIcon, color: 'text-amber-500', bg: 'bg-amber-50' },
  ]

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Панель управления</h1>
        <p className="text-sm text-gray-500 mt-1">Обзор основных показателей салона</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${bg}`}>
                <Icon className={`w-6 h-6 ${color}`} />
              </div>
              <div>
                <p className="text-xl font-bold text-gray-900">{value}</p>
                <p className="text-xs text-gray-500 mt-0.5">{label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between p-5 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">Последние записи</h2>
            <Link to="/admin/appointments" className="text-sm text-primary-500 hover:underline font-medium">
              Все записи →
            </Link>
          </div>
          {recentAppointments.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Клиент</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Мастер</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Дата</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Сумма</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAppointments.map((apt) => (
                    <tr key={apt.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        {apt.client_id ? (
                          <Link to={`/admin/clients/${apt.client_id}`} className="font-medium text-primary-500 hover:underline">
                            {apt.client_name}
                          </Link>
                        ) : (
                          <div>
                            <p className="font-medium text-gray-900">{apt.client_name}</p>
                            <p className="text-xs text-gray-400">{apt.client_phone}</p>
                          </div>
                        )}
                        {apt.client_id && <p className="text-xs text-gray-400">{apt.client_phone}</p>}
                      </td>
                      <td className="py-3 px-4">
                        <Link to={`/admin/masters/${apt.master_id}`} className="text-gray-600 hover:text-primary-500 hover:underline">
                          {apt.master_name}
                        </Link>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {new Date(apt.datetime_start).toLocaleDateString('ru-RU')}
                        <br />
                        <span className="text-xs text-gray-400">
                          {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-medium">{Number(apt.total_price).toLocaleString('ru-RU')} ₽</td>
                      <td className="py-3 px-4">
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[apt.status] || 'bg-gray-100 text-gray-700'}`}>
                          {statusLabels[apt.status] || apt.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-10">Записей пока нет</p>
          )}
        </div>

        <div className="space-y-6">
          {stats?.top_services && stats.top_services.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Популярные услуги</h2>
              </div>
              <div className="p-5 space-y-3">
                {stats.top_services.slice(0, 5).map((svc, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-primary-50 text-primary-500 text-xs font-bold flex items-center justify-center">
                        {i + 1}
                      </span>
                      <span className="text-sm text-gray-700">{svc.name}</span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{svc.count}</p>
                      <p className="text-xs text-gray-400">{Number(svc.revenue).toLocaleString('ru-RU')} ₽</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {stats?.master_load && stats.master_load.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Загрузка мастеров</h2>
              </div>
              <div className="p-5 space-y-3">
                {stats.master_load.map((m) => (
                  <div key={m.master_id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                        <UserIcon className="w-4 h-4 text-gray-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{m.master_name}</p>
                        <p className="text-xs text-gray-400">{m.appointments_count} записей</p>
                      </div>
                    </div>
                    <span className="text-sm font-medium text-gray-700">{Number(m.revenue).toLocaleString('ru-RU')} ₽</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
