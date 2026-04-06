import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getAdminCalendar, getAdminAppointments, createAdminAppointment, updateAppointmentStatus } from '../../api/services'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, addDays, addMonths, subMonths, isSameDay } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
  XMarkIcon,
  UserIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'

interface Appointment {
  id: number
  client_id: number | null
  client_name: string
  client_phone: string
  datetime_start: string
  datetime_end: string
  status: string
  total_price: string
  services: string[]
  comment: string
  master_id?: number
}

interface MasterCalendarData {
  master_id: number
  master_name: string
  date: string
  appointments: Appointment[]
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  confirmed: 'bg-green-100 text-green-700 border-green-200',
  completed: 'bg-blue-100 text-blue-700 border-blue-200',
  cancelled_by_client: 'bg-red-100 text-red-700 border-red-200',
  cancelled_by_admin: 'bg-red-100 text-red-700 border-red-200',
  no_show: 'bg-gray-100 text-gray-700 border-gray-200',
}

const statusLabels: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  completed: 'Завершена',
  cancelled_by_client: 'Отменена',
  cancelled_by_admin: 'Отменена',
  no_show: 'Не явился',
}

const HOURS = Array.from({ length: 21 }, (_, i) => 10 + i)

export default function AdminCalendarPage() {
  const [view, setView] = useState<'month' | 'day'>('day')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [mastersData, setMastersData] = useState<MasterCalendarData[]>([])
  const [allAppointments, setAllAppointments] = useState<Appointment[]>([])
  const [selectedMaster, setSelectedMaster] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [createModal, setCreateModal] = useState(false)
  const [clientModal, setClientModal] = useState<Appointment | null>(null)
  const [createForm, setCreateForm] = useState({
    master_id: '',
    service_ids: [] as number[],
    datetime_start: '',
    datetime_end: '',
    client_phone: '',
    comment: '',
  })
  const [availableServices, setAvailableServices] = useState<any[]>([])

  const dayStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate(), 10, 0)
  const dayEnd = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate(), 20, 0)

  const fetchDayData = useCallback(() => {
    setLoading(true)
    const dateStr = format(currentDate, 'yyyy-MM-dd')
    Promise.all([
      getAdminCalendar({ month: String(currentDate.getMonth() + 1), year: String(currentDate.getFullYear()), ...(selectedMaster ? { master_id: String(selectedMaster) } : {}) }).catch(() => null),
      getAdminAppointments({ date_from: dateStr, date_to: dateStr }).catch(() => null),
    ])
      .then(([calRes, aptRes]) => {
        if (calRes) setMastersData(calRes.data || [])
        if (aptRes) {
          const results = aptRes.data.results || aptRes.data || []
          setAllAppointments(results)
        }
      })
      .finally(() => setLoading(false))
  }, [currentDate, selectedMaster])

  useEffect(() => {
    fetchDayData()
  }, [fetchDayData])

  const prevDay = () => setCurrentDate((d) => addDays(d, -1))
  const nextDay = () => setCurrentDate((d) => addDays(d, 1))
  const prevMonth = () => setCurrentDate((d) => subMonths(d, 1))
  const nextMonth = () => setCurrentDate((d) => addMonths(d, 1))

  const masters = [...new Map(mastersData.map((m) => [m.master_id, { id: m.master_id, name: m.master_name }])).values()]

  const getAppointmentsForMasterAndHour = (masterId: number, hour: number) => {
    const hourStart = new Date(currentDate)
    hourStart.setHours(hour, 0, 0, 0)
    const hourEnd = new Date(hourStart)
    hourEnd.setMinutes(30)

    return allAppointments.filter((apt) => {
      if (selectedMaster && apt.master_id !== masterId) return false
      const start = new Date(apt.datetime_start)
      return start >= hourStart && start < hourEnd
    })
  }

  const getAppointmentRows = (masterId: number, hour: number) => {
    const hourStart = new Date(currentDate)
    hourStart.setHours(hour, 0, 0, 0)

    return allAppointments.filter((apt) => {
      const start = new Date(apt.datetime_start)
      return start.getHours() === hour && (selectedMaster ? apt.master_id === masterId : true)
    })
  }

  const openCreate = (masterId?: number, hour?: number) => {
    const dateStr = format(currentDate, 'yyyy-MM-dd')
    const timeStr = hour !== undefined ? `${String(hour).padStart(2, '0')}:00` : '10:00'
    setCreateForm({
      master_id: String(masterId || masters[0]?.id || ''),
      service_ids: [],
      datetime_start: `${dateStr}T${timeStr}`,
      datetime_end: `${dateStr}T${timeStr}`,
      client_phone: '',
      comment: '',
    })
    setCreateModal(true)
  }

  const handleCreate = async () => {
    try {
      const start = new Date(createForm.datetime_start)
      const end = new Date(createForm.datetime_end)
      if (end <= start) {
        toast.error('Время окончания должно быть позже начала')
        return
      }
      await createAdminAppointment({
        master_id: Number(createForm.master_id),
        service_ids: createForm.service_ids,
        datetime_start: createForm.datetime_start,
        datetime_end: createForm.datetime_end,
        client_phone: createForm.client_phone || undefined,
        comment: createForm.comment,
      })
      toast.success('Запись создана')
      setCreateModal(false)
      fetchDayData()
    } catch {
      toast.error('Ошибка при создании записи')
    }
  }

  if (loading) return <div className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-96" />

  if (view === 'month') {
    const days = eachDayOfInterval({ start: startOfMonth(currentDate), end: endOfMonth(currentDate) })
    const weeks: (Date | null)[][] = []
    let currentWeek: (Date | null)[] = []
    const firstDay = startOfMonth(currentDate).getDay()
    const offset = firstDay === 0 ? 6 : firstDay - 1
    for (let i = 0; i < offset; i++) currentWeek.push(null)
    for (const day of days) {
      currentWeek.push(day)
      if (currentWeek.length === 7) { weeks.push(currentWeek); currentWeek = [] }
    }
    if (currentWeek.length > 0) { while (currentWeek.length < 7) currentWeek.push(null); weeks.push(currentWeek) }

    return (
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Календарь</h1>
            <p className="text-sm text-gray-500 mt-1">Расписание мастеров</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setView('day')} className="btn-secondary text-sm">День</button>
            <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-lg"><ChevronLeftIcon className="w-5 h-5" /></button>
            <span className="font-medium text-gray-700 min-w-[140px] text-center">{format(currentDate, 'LLLL yyyy', { locale: ru })}</span>
            <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-lg"><ChevronRightIcon className="w-5 h-5" /></button>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="grid grid-cols-7 border-b border-gray-200">
            {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((d) => (
              <div key={d} className="py-2 text-center text-xs font-medium text-gray-500 uppercase">{d}</div>
            ))}
          </div>
          <div className="divide-y divide-gray-200">
            {weeks.map((week, wi) => (
              <div key={wi} className="grid grid-cols-7">
                {week.map((day, di) => {
                  if (!day) return <div key={di} className="min-h-24 bg-gray-50/50" />
                  const key = format(day, 'yyyy-MM-dd')
                  const dayApts = allAppointments.filter((a) => a.datetime_start.startsWith(key))
                  const isToday = key === format(new Date(), 'yyyy-MM-dd')
                  return (
                    <div
                      key={key}
                      onClick={() => { setCurrentDate(day); setView('day') }}
                      className={`min-h-24 p-1.5 border-l border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${isToday ? 'bg-primary-50/30' : ''}`}
                    >
                      <p className={`text-xs font-medium mb-1 ${isToday ? 'text-primary-500' : 'text-gray-500'}`}>{format(day, 'd')}</p>
                      <div className="space-y-0.5">
                        {dayApts.slice(0, 3).map((apt) => (
                          <div key={apt.id} className={`text-[10px] rounded px-1 py-0.5 truncate ${statusColors[apt.status] || 'bg-gray-100 text-gray-600'}`}>
                            {new Date(apt.datetime_start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}{' '}
                            {apt.client_id ? (
                              <Link to={`/admin/clients/${apt.client_id}`} className="hover:underline" onClick={(e) => e.stopPropagation()}>
                                {apt.client_name}
                              </Link>
                            ) : apt.client_name}
                          </div>
                        ))}
                        {dayApts.length > 3 && <p className="text-[10px] text-gray-400 text-center">+{dayApts.length - 3}</p>}
                      </div>
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Расписание на день</h1>
          <p className="text-sm text-gray-500 mt-1">{format(currentDate, 'd MMMM yyyy', { locale: ru })}</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => setView('month')} className="btn-secondary text-sm">Месяц</button>
          <button onClick={prevDay} className="p-2 hover:bg-gray-100 rounded-lg"><ChevronLeftIcon className="w-5 h-5" /></button>
          <span className="font-medium text-gray-700 min-w-[140px] text-center">{format(currentDate, 'd MMM', { locale: ru })}</span>
          <button onClick={nextDay} className="p-2 hover:bg-gray-100 rounded-lg"><ChevronRightIcon className="w-5 h-5" /></button>
          <button onClick={() => setCurrentDate(new Date())} className="btn-secondary text-sm">Сегодня</button>
          <button onClick={() => openCreate()} className="btn-primary flex items-center gap-1"><PlusIcon className="w-4 h-4" /> Запись</button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
        <div className="min-w-[600px]" style={{ minWidth: `${200 + masters.length * 200}px` }}>
          <div className="grid border-b border-gray-200 bg-gray-50" style={{ gridTemplateColumns: `80px repeat(${masters.length}, 1fr)` }}>
            <div className="p-3 text-xs font-medium text-gray-500 uppercase text-center">Время</div>
            {masters.map((m) => (
              <div key={m.id} className="p-3 text-center">
                <Link to={`/admin/masters/${m.id}`} className="text-sm font-semibold text-primary-500 hover:underline">
                  {m.name}
                </Link>
              </div>
            ))}
          </div>

          {HOURS.map((hour) => (
            <div key={hour} className="grid border-b border-gray-100" style={{ gridTemplateColumns: `80px repeat(${masters.length}, 1fr)` }}>
              <div className="p-2 text-xs text-gray-400 text-center border-r border-gray-100 flex items-start justify-center pt-1">
                {String(hour).padStart(2, '0')}:00
              </div>
              {masters.map((m) => {
                const apts = getAppointmentRows(m.id, hour)
                return (
                  <div
                    key={m.id}
                    className="p-1 border-r border-gray-100 min-h-[60px] hover:bg-gray-50 cursor-pointer transition-colors relative"
                    onClick={() => openCreate(m.id, hour)}
                  >
                    {apts.map((apt) => {
                      const start = new Date(apt.datetime_start)
                      const end = new Date(apt.datetime_end)
                      const durationMin = (end.getTime() - start.getTime()) / 60000
                      const rows = Math.max(1, Math.ceil(durationMin / 30))
                      return (
                        <div
                          key={apt.id}
                          className={`rounded-lg border p-2 mb-1 cursor-pointer transition-shadow hover:shadow-md ${statusColors[apt.status] || 'bg-gray-100 text-gray-600 border-gray-200'}`}
                          style={{ minHeight: `${rows * 56}px` }}
                          onClick={(e) => { e.stopPropagation(); setClientModal(apt) }}
                        >
                          {apt.client_id ? (
                            <Link
                              to={`/admin/clients/${apt.client_id}`}
                              className="text-xs font-semibold truncate hover:underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {apt.client_name}
                            </Link>
                          ) : (
                            <p className="text-xs font-semibold truncate">{apt.client_name}</p>
                          )}
                          <p className="text-[10px] opacity-75 truncate">
                            {apt.services?.join(', ') || 'Услуга'}
                          </p>
                          <p className="text-[10px] opacity-60">
                            {start.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })} — {end.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      <Modal isOpen={createModal} onClose={() => setCreateModal(false)} title="Новая запись">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Мастер</label>
            <select value={createForm.master_id} onChange={(e) => setCreateForm({ ...createForm, master_id: e.target.value })} className="input-field">
              {masters.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Дата и время начала</label>
            <input type="datetime-local" value={createForm.datetime_start} onChange={(e) => setCreateForm({ ...createForm, datetime_start: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Дата и время окончания</label>
            <input type="datetime-local" value={createForm.datetime_end} onChange={(e) => setCreateForm({ ...createForm, datetime_end: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Телефон клиента</label>
            <input type="tel" value={createForm.client_phone} onChange={(e) => setCreateForm({ ...createForm, client_phone: e.target.value })} className="input-field" placeholder="+7..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Комментарий</label>
            <textarea value={createForm.comment} onChange={(e) => setCreateForm({ ...createForm, comment: e.target.value })} className="input-field resize-none" rows={2} />
          </div>
          <div className="flex gap-3 justify-end">
            <button onClick={() => setCreateModal(false)} className="btn-secondary">Отмена</button>
            <button onClick={handleCreate} className="btn-primary">Создать</button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={!!clientModal} onClose={() => setClientModal(null)} title="Информация о записи">
        {clientModal && (
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Клиент</p>
              <p className="font-semibold text-gray-900">{clientModal.client_name}</p>
              <p className="text-sm text-gray-500">{clientModal.client_phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Услуги</p>
              <p className="text-gray-900">{clientModal.services?.join(', ') || '—'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Время</p>
              <p className="text-gray-900">
                {new Date(clientModal.datetime_start).toLocaleString('ru-RU')} — {new Date(clientModal.datetime_end).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Сумма</p>
              <p className="font-bold text-primary-500">{Number(clientModal.total_price).toLocaleString('ru-RU')} ₽</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Статус</p>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[clientModal.status] || 'bg-gray-100 text-gray-700'}`}>
                {statusLabels[clientModal.status] || clientModal.status}
              </span>
            </div>
            {clientModal.comment && (
              <div>
                <p className="text-sm text-gray-500">Комментарий</p>
                <p className="text-gray-600 text-sm bg-gray-50 rounded-lg p-2">{clientModal.comment}</p>
              </div>
            )}
            <div className="flex gap-2 flex-wrap pt-2">
              {(['pending', 'confirmed', 'completed', 'cancelled_by_client'] as const).map((s) => (
                <button
                  key={s}
                  onClick={async () => {
                    try {
                      await updateAppointmentStatus(clientModal.id, s)
                      toast.success('Статус обновлён')
                      setClientModal(null)
                      fetchDayData()
                    } catch { toast.error('Ошибка') }
                  }}
                  className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                    clientModal.status === s ? 'bg-gray-100 text-gray-400 cursor-default' : 'bg-white border border-gray-200 text-gray-600 hover:border-primary-300 hover:text-primary-500'
                  }`}
                >
                  {statusLabels[s]}
                </button>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
