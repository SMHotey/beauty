import { useEffect, useState } from 'react'
import { getMyAppointments, cancelAppointment } from '../api/services'
import { SkeletonCard } from '../components/UI/Skeleton'
import toast from 'react-hot-toast'
import Modal from '../components/UI/Modal'
import { handleApiError } from '../utils/apiErrors'

interface Appointment {
  id: number
  master_name: string
  services: { service_name: string; price_at_booking: number }[]
  datetime_start: string
  datetime_end: string
  status: string
  total_price: number
  comment: string
}

const statusLabels: Record<string, { label: string; color: string }> = {
  pending: { label: 'Ожидает', color: 'bg-yellow-100 text-yellow-700' },
  confirmed: { label: 'Подтверждена', color: 'bg-green-100 text-green-700' },
  completed: { label: 'Завершена', color: 'bg-blue-100 text-blue-700' },
  cancelled: { label: 'Отменена', color: 'bg-red-100 text-red-700' },
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [cancelModal, setCancelModal] = useState<number | null>(null)

  useEffect(() => {
    getMyAppointments()
      .then((res) => setAppointments(res.data.results || res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки записей'))
      .finally(() => setLoading(false))
  }, [])

  const handleCancel = async (id: number) => {
    try {
      await cancelAppointment(id)
      toast.success('Запись отменена')
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'cancelled' } : a))
      )
    } catch {
      toast.error('Ошибка при отмене')
    } finally {
      setCancelModal(null)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Мои записи</h1>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : appointments.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">У вас пока нет записей</p>
        </div>
      ) : (
        <div className="space-y-4">
          {appointments.map((apt) => {
            const status = statusLabels[apt.status] || { label: apt.status, color: 'bg-gray-100 text-gray-700' }
            return (
              <div key={apt.id} className="card">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-gray-900">
                      {apt.master_name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(apt.datetime_start).toLocaleDateString('ru-RU')} в {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${status.color}`}>
                    {status.label}
                  </span>
                </div>
                <div className="space-y-1 mb-3">
                  {apt.services.map((svc, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-gray-600">{svc.service_name}</span>
                      <span className="text-gray-900 font-medium">{svc.price_at_booking} ₽</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <span className="font-bold text-gray-900">{apt.total_price} ₽</span>
                  {(apt.status === 'pending' || apt.status === 'confirmed') && (
                    <button
                      onClick={() => setCancelModal(apt.id)}
                      className="text-sm text-red-500 hover:text-red-600 font-medium"
                    >
                      Отменить
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <Modal
        isOpen={cancelModal !== null}
        onClose={() => setCancelModal(null)}
        title="Отмена записи"
      >
        <p className="text-gray-600 mb-4">Вы уверены, что хотите отменить эту запись?</p>
        <div className="flex gap-3 justify-end">
          <button onClick={() => setCancelModal(null)} className="btn-secondary">
            Нет
          </button>
          {cancelModal !== null && (
            <button onClick={() => handleCancel(cancelModal)} className="btn-danger">
              Да, отменить
            </button>
          )}
        </div>
      </Modal>
    </div>
  )
}
