import { useEffect, useState } from 'react'
import api from '../../api/client'
import { handleApiError } from '../../utils/apiErrors'
import toast from 'react-hot-toast'
import { format, addDays, startOfWeek, isSameDay } from 'date-fns'
import { ru } from 'date-fns/locale'
import { ChevronLeftIcon, ChevronRightIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

const WEEKDAY_LABELS = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

interface ScheduleEntry {
  id: number
  date: string
  start_time: string
  end_time: string
  is_working: boolean
  breaks: { start: string; end: string }[]
}

export default function MasterSchedulePage() {
  const [schedule, setSchedule] = useState<ScheduleEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [weekStart, setWeekStart] = useState(startOfWeek(new Date(), { weekStartsOn: 1 }))
  const [canEdit, setCanEdit] = useState(false)
  const [editing, setEditing] = useState<number | null>(null)
  const [editForm, setEditForm] = useState({ start_time: '10:00', end_time: '19:00', is_working: true })

  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i))

  useEffect(() => {
    const from = format(weekStart, 'yyyy-MM-dd')
    const to = format(addDays(weekStart, 6), 'yyyy-MM-dd')
    Promise.all([
      api.get('/staff/master/schedule/', { params: { date_from: from, date_to: to } }).then((r) => r.data),
      api.get('/staff/master/profile/').then((r) => r.data),
    ])
      .then(([data, profile]) => {
        setSchedule(data)
        setCanEdit(profile.permissions?.can_edit_schedule || false)
      })
      .catch((e) => handleApiError(e, 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [weekStart])

  const getEntry = (date: Date) => {
    const key = format(date, 'yyyy-MM-dd')
    return schedule.find((s) => s.date === key)
  }

  const saveEntry = async (date: Date) => {
    const entry = getEntry(date)
    try {
      const res = await api.post('/staff/master/schedule/', {
        date: format(date, 'yyyy-MM-dd'),
        ...editForm,
      })
      if (entry) {
        setSchedule((prev) => prev.map((s) => (s.id === entry.id ? res.data : s)))
      } else {
        setSchedule((prev) => [...prev, res.data])
      }
      setEditing(null)
      toast.success('Сохранено')
    } catch {
      toast.error('Ошибка')
    }
  }

  const prevWeek = () => setWeekStart((d) => addDays(d, -7))
  const nextWeek = () => setWeekStart((d) => addDays(d, 7))

  if (loading) return <div className="space-y-4">{Array.from({ length: 7 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-20" />)}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">График работы</h1>
          <p className="text-sm text-gray-500 mt-1">
            {format(weekStart, 'd MMMM', { locale: ru })} — {format(addDays(weekStart, 6), 'd MMMM yyyy', { locale: ru })}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={prevWeek} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ChevronLeftIcon className="w-5 h-5" /></button>
          <button onClick={() => setWeekStart(startOfWeek(new Date(), { weekStartsOn: 1 }))} className="btn-secondary text-sm">Сегодня</button>
          <button onClick={nextWeek} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ChevronRightIcon className="w-5 h-5" /></button>
        </div>
      </div>

      <div className="space-y-3">
        {weekDays.map((day) => {
          const entry = getEntry(day)
          const isEditing = editing === day.getTime()
          const isToday = isSameDay(day, new Date())

          return (
            <div key={day.getTime()} className={`bg-white rounded-xl shadow-sm border transition-colors ${isToday ? 'border-primary-300 bg-primary-50/30' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between p-4">
                <div className="flex items-center gap-4">
                  <div className="text-center min-w-[60px]">
                    <p className={`text-sm font-bold ${isToday ? 'text-primary-600' : 'text-gray-900'}`}>{WEEKDAY_LABELS[day.getDay()]}</p>
                    <p className={`text-lg font-bold ${isToday ? 'text-primary-600' : 'text-gray-700'}`}>{format(day, 'd')}</p>
                  </div>

                  {isEditing ? (
                    <div className="flex items-center gap-3">
                      <input type="time" value={editForm.start_time} onChange={(e) => setEditForm({ ...editForm, start_time: e.target.value })} className="input-field py-1 px-2 text-sm w-24" />
                      <span className="text-gray-400">—</span>
                      <input type="time" value={editForm.end_time} onChange={(e) => setEditForm({ ...editForm, end_time: e.target.value })} className="input-field py-1 px-2 text-sm w-24" />
                      <label className="flex items-center gap-1 text-sm text-gray-600">
                        <input type="checkbox" checked={editForm.is_working} onChange={(e) => setEditForm({ ...editForm, is_working: e.target.checked })} className="rounded border-gray-300 text-primary-500" />
                        Рабочий
                      </label>
                      <button onClick={() => saveEntry(day)} className="p-1.5 text-green-500 hover:bg-green-50 rounded-lg"><CheckIcon className="w-5 h-5" /></button>
                      <button onClick={() => setEditing(null)} className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg"><XMarkIcon className="w-5 h-5" /></button>
                    </div>
                  ) : (
                    <div>
                      {entry ? (
                        <div>
                          {entry.is_working ? (
                            <p className="font-medium text-gray-900">{entry.start_time} — {entry.end_time}</p>
                          ) : (
                            <p className="text-gray-400">Выходной</p>
                          )}
                        </div>
                      ) : (
                        <p className="text-gray-400 text-sm">Не задан</p>
                      )}
                    </div>
                  )}
                </div>

                {canEdit && !isEditing && (
                  <button
                    onClick={() => {
                      const e = getEntry(day)
                      setEditForm({
                        start_time: e?.start_time || '10:00',
                        end_time: e?.end_time || '19:00',
                        is_working: e?.is_working ?? true,
                      })
                      setEditing(day.getTime())
                    }}
                    className="text-sm text-primary-500 hover:underline"
                  >
                    {entry ? 'Изменить' : 'Задать'}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {!canEdit && (
        <p className="text-center text-sm text-gray-400 mt-4">Редактирование графика недоступно — обратитесь к администратору</p>
      )}
    </div>
  )
}
