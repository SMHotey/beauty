import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAdminAppointments, updateAppointmentStatus } from '../../api/services'
import { SkeletonCard } from '../../components/UI/Skeleton'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'

interface Appointment {
  id: number
  client_id: number | null
  client_name: string
  client_phone: string
  master_id: number
  master_name: string
  service_names: string[]
  datetime_start: string
  datetime_end: string
  status: string
  total_price: string
  comment: string
}

const statusOptions = [
  { value: 'pending', label: 'Ожидает' },
  { value: 'confirmed', label: 'Подтверждена' },
  { value: 'completed', label: 'Завершена' },
  { value: 'cancelled_by_client', label: 'Отменена' },
]

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled_by_client: 'bg-red-100 text-red-700',
  cancelled_by_admin: 'bg-red-100 text-red-700',
  no_show: 'bg-gray-100 text-gray-700',
}

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  completed: 'Завершена',
  cancelled_by_client: 'Отменена',
  cancelled_by_admin: 'Отменена',
  no_show: 'Не явился',
}

export default function AdminAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    const params: Record<string, string> = {}
    if (filter) params.status = filter
    getAdminAppointments(params)
      .then((res) => setAppointments(res.data.results || res.data || []))
      .catch((e) => handleApiError(e, 'Ошибка загрузки записей'))
      .finally(() => setLoading(false))
  }, [filter])

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await updateAppointmentStatus(id, status)
      setAppointments((prev) => prev.map((a) => (a.id === id ? { ...a, status } : a)))
      toast.success('Статус обновлён')
    } catch {
      toast.error('Ошибка')
    }
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Записи</h1>
          <p className="text-sm text-gray-500 mt-1">Управление записями клиентов</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilter('')}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              !filter ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            Все
          </button>
          {statusOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                filter === opt.value ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : appointments.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-16 text-center">
          <p className="text-gray-500">Записей не найдено</p>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((apt) => (
            <div key={apt.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-4">
                <div>
                  {apt.client_id ? (
                    <Link to={`/admin/clients/${apt.client_id}`} className="font-semibold text-primary-500 hover:underline">
                      {apt.client_name}
                    </Link>
                  ) : (
                    <p className="font-semibold text-gray-900">{apt.client_name}</p>
                  )}
                  <p className="text-sm text-gray-500">{apt.client_phone}</p>
                </div>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[apt.status] || 'bg-gray-100 text-gray-700'}`}>
                  {statusLabels[apt.status] || apt.status}
                </span>
              </div>
              <div className="grid sm:grid-cols-3 gap-4 text-sm mb-3">
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Мастер</p>
                  <Link to={`/admin/masters/${apt.master_id}`} className="font-medium text-gray-900 hover:text-primary-500 hover:underline">
                    {apt.master_name}
                  </Link>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Дата и время</p>
                  <p className="font-medium text-gray-900">
                    {new Date(apt.datetime_start).toLocaleDateString('ru-RU')} {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Сумма</p>
                  <p className="font-bold text-primary-500">{Number(apt.total_price).toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
              {apt.service_names && apt.service_names.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {apt.service_names.map((svc, i) => (
                    <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md">
                      {svc}
                    </span>
                  ))}
                </div>
              )}
              {apt.comment && <p className="text-sm text-gray-500 mb-3 bg-gray-50 rounded-lg p-2">Комментарий: {apt.comment}</p>}
              <div className="flex gap-2 pt-3 border-t border-gray-100 flex-wrap">
                {statusOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => handleStatusChange(apt.id, opt.value)}
                    disabled={apt.status === opt.value}
                    className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                      apt.status === opt.value
                        ? 'bg-gray-100 text-gray-400 cursor-default'
                        : 'bg-white border border-gray-200 text-gray-600 hover:border-primary-300 hover:text-primary-500'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
