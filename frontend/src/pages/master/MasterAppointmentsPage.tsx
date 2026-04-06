import { useEffect, useState } from 'react'
import api from '../../api/client'
import { handleApiError } from '../../utils/apiErrors'
import toast from 'react-hot-toast'

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  completed: 'Завершена',
  cancelled_by_client: 'Отменена',
  cancelled_by_admin: 'Отменена',
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

interface Appointment {
  id: number
  client_name: string
  client_phone: string
  datetime_start: string
  datetime_end: string
  status: string
  payment_method: string
  total_price: string
  services: string[]
  comment: string
}

export default function MasterAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    const params: Record<string, string> = {}
    if (filter) params.status = filter
    api.get('/staff/master/appointments/', { params })
      .then((res) => setAppointments(res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [filter])

  const handleStatus = async (id: number, status: string) => {
    try {
      await api.patch('/staff/master/appointments/', { appointment_id: id, status })
      setAppointments((prev) => prev.map((a) => (a.id === id ? { ...a, status } : a)))
      toast.success('Статус обновлён')
    } catch {
      toast.error('Ошибка')
    }
  }

  if (loading) return <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-16" />)}</div>

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Мои записи</h1>
          <p className="text-sm text-gray-500 mt-1">Расписание и управление статусами</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={() => setFilter('')} className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${!filter ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>Все</button>
          {['pending', 'confirmed', 'completed'].map((s) => (
            <button key={s} onClick={() => setFilter(s)} className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === s ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>{statusLabels[s]}</button>
          ))}
        </div>
      </div>

      {appointments.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-16 text-center">
          <p className="text-gray-500">Записей не найдено</p>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map((apt) => (
            <div key={apt.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-3">
                <div>
                  <p className="font-semibold text-gray-900">{apt.client_name}</p>
                  <p className="text-sm text-gray-500">{apt.client_phone}</p>
                </div>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[apt.status] || 'bg-gray-100 text-gray-700'}`}>
                  {statusLabels[apt.status] || apt.status}
                </span>
              </div>
              <div className="grid sm:grid-cols-3 gap-4 text-sm mb-3">
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Дата и время</p>
                  <p className="font-medium text-gray-900">
                    {new Date(apt.datetime_start).toLocaleDateString('ru-RU')} {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Услуги</p>
                  <p className="font-medium text-gray-900">{apt.services.join(', ') || '—'}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-0.5">Сумма</p>
                  <p className="font-bold text-primary-500">{Number(apt.total_price).toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
              <div className="flex gap-2 pt-3 border-t border-gray-100 flex-wrap">
                {(['pending', 'confirmed', 'completed', 'cancelled_by_client'] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleStatus(apt.id, s)}
                    disabled={apt.status === s}
                    className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                      apt.status === s ? 'bg-gray-100 text-gray-400 cursor-default' : 'bg-white border border-gray-200 text-gray-600 hover:border-primary-300 hover:text-primary-500'
                    }`}
                  >
                    {statusLabels[s]}
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
