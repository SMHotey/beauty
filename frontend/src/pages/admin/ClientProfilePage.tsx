import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../../api/client'
import {
  ArrowLeftIcon,
  UserIcon,
  CurrencyDollarIcon,
  CalendarDaysIcon,
  PhoneIcon,
  EnvelopeIcon,
  GiftIcon,
  TicketIcon,
} from '@heroicons/react/24/outline'
import { handleApiError } from '../../utils/apiErrors'

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  completed: 'Завершена',
  cancelled_by_client: 'Отменена',
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

interface ServiceStat {
  service_id: number
  service_name: string
  count: number
  spent: string
}

interface Appointment {
  id: number
  master_name: string
  datetime_start: string
  status: string
  total_price: string
  services: { name: string; price: string }[]
}

interface ClientStats {
  client_id: number
  client_name: string
  phone: string
  email: string
  bonus_balance: number
  referral_code: string
  referred_by: string | null
  total_visits: number
  total_spent: string
  completed_visits: number
  service_stats: ServiceStat[]
  recent_appointments: Appointment[]
}

export default function ClientProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [stats, setStats] = useState<ClientStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    api.get(`/admin-panel/clients/${id}/stats/`)
      .then((res) => setStats(res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки профиля'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="space-y-6"><div className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-48" /></div>
  if (!stats) return <div className="text-center py-16 text-gray-500">Клиент не найден или нет доступа</div>

  const cards = [
    { label: 'Визитов', value: stats.total_visits, icon: CalendarDaysIcon, color: 'text-blue-500', bg: 'bg-blue-50' },
    { label: 'Потрачено', value: `${Number(stats.total_spent).toLocaleString('ru-RU')} ₽`, icon: CurrencyDollarIcon, color: 'text-green-500', bg: 'bg-green-50' },
    { label: 'Завершённых', value: stats.completed_visits, icon: UserIcon, color: 'text-purple-500', bg: 'bg-purple-50' },
    { label: 'Бонусы', value: `${stats.bonus_balance}`, icon: GiftIcon, color: 'text-amber-500', bg: 'bg-amber-50' },
  ]

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{stats.client_name}</h1>
          <p className="text-sm text-gray-500">{stats.phone}</p>
        </div>
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

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Данные</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <PhoneIcon className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Телефон</p>
                  <p className="text-sm font-medium text-gray-900">{stats.phone}</p>
                </div>
              </div>
              {stats.email && (
                <div className="flex items-center gap-3">
                  <EnvelopeIcon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="text-sm font-medium text-gray-900">{stats.email}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3">
                <TicketIcon className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Реферальный код</p>
                  <p className="text-sm font-mono font-medium text-gray-900">{stats.referral_code}</p>
                </div>
              </div>
              {stats.referred_by && (
                <div className="flex items-center gap-3">
                  <GiftIcon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Приглашён</p>
                    <p className="text-sm font-medium text-gray-900">{stats.referred_by}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {stats?.service_stats?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Услуги</h2>
              </div>
              <div className="p-5">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-2 font-medium text-gray-500">Услуга</th>
                      <th className="text-right py-2 font-medium text-gray-500">Кол-во</th>
                      <th className="text-right py-2 font-medium text-gray-500">Сумма</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.service_stats.map((s) => (
                      <tr key={s.service_id} className="border-b border-gray-50">
                        <td className="py-2 text-gray-900">{s.service_name}</td>
                        <td className="py-2 text-right text-gray-600">{s.count}</td>
                        <td className="py-2 text-right font-medium">{Number(s.spent).toLocaleString('ru-RU')} ₽</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-5 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">История записей</h2>
          </div>
          {stats.recent_appointments.length === 0 ? (
            <p className="text-gray-500 text-center py-10">Записей пока нет</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Дата</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Мастер</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Услуги</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-500">Сумма</th>
                    <th className="text-center py-3 px-4 font-medium text-gray-500">Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_appointments.map((apt) => (
                    <tr key={apt.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 text-gray-600 text-xs">
                        {new Date(apt.datetime_start).toLocaleDateString('ru-RU')}
                        <br />
                        <span className="text-gray-400">
                          {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-900">{apt.master_name}</td>
                      <td className="py-3 px-4 text-gray-600 max-w-xs">
                        {apt.services.map((s, i) => (
                          <span key={i} className="block text-xs">{s.name} — {Number(s.price).toLocaleString('ru-RU')} ₽</span>
                        ))}
                      </td>
                      <td className="py-3 px-4 text-right font-medium">{Number(apt.total_price).toLocaleString('ru-RU')} ₽</td>
                      <td className="py-3 px-4 text-center">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusColors[apt.status] || 'bg-gray-100 text-gray-700'}`}>
                          {statusLabels[apt.status] || apt.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
