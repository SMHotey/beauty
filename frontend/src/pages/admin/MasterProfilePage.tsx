import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAdminMasters, updateAdminMaster } from '../../api/services'
import api from '../../api/client'
import {
  ArrowLeftIcon,
  UserIcon,
  ClockIcon,
  CurrencyDollarIcon,
  StarIcon,
  ChatBubbleLeftIcon,
  CalendarIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'
import { format, subDays } from 'date-fns'

interface ServiceStat {
  service_id: number
  service_name: string
  count: number
  revenue: string
}

interface Review {
  id: number
  client_name: string
  rating: number
  comment: string
  created_at: string
}

interface MasterStats {
  master_id: number
  master_name: string
  bio: string
  phone: string
  is_active: boolean
  total_revenue: string
  total_appointments: number
  total_hours: number
  avg_rating: number | null
  service_stats: ServiceStat[]
  recent_reviews: Review[]
}

interface MasterDetail {
  id: number
  first_name: string
  last_name: string
  full_name: string
  bio: string
  phone: string
  is_active: boolean
  working_hours: Record<string, { start: string; end: string }>
  break_slots: { start: string; end: string; weekday?: number }[]
  vacations: any[]
  services?: { service: { id: number; name: string } }[]
}

interface MasterServiceStat {
  master_id: number
  master_name: string
  service_id: number
  service_name: string
  total_count: number
  total_revenue: string
  date_from: string
  date_to: string
}

const WEEKDAYS = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
const WEEKDAY_KEYS = ['0', '1', '2', '3', '4', '5', '6']
const WEEKDAY_LABELS = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

const PRESETS = [
  { label: '10:00–19:00', start: '10:00', end: '19:00' },
  { label: '09:00–18:00', start: '09:00', end: '18:00' },
  { label: '09:00–20:00', start: '09:00', end: '20:00' },
  { label: '10:00–20:00', start: '10:00', end: '20:00' },
  { label: '11:00–20:00', start: '11:00', end: '20:00' },
  { label: 'Выходной', start: '', end: '' },
]

export default function MasterProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [stats, setStats] = useState<MasterStats | null>(null)
  const [master, setMaster] = useState<MasterDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState<'30' | '90' | '365' | 'all'>('30')
  const [editingHours, setEditingHours] = useState(false)
  const [hoursForm, setHoursForm] = useState<Record<string, { start: string; end: string }>>({})
  const [editBio, setEditBio] = useState(false)
  const [bioForm, setBioForm] = useState('')

  const [serviceStatsModal, setServiceStatsModal] = useState(false)
  const [selectedService, setSelectedService] = useState<{ id: number; name: string } | null>(null)
  const [svcDateFrom, setSvcDateFrom] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [svcDateTo, setSvcDateTo] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [svcStatData, setSvcStatData] = useState<MasterServiceStat | null>(null)
  const [svcStatLoading, setSvcStatLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    const params: Record<string, string> = {}
    if (period !== 'all') {
      const now = new Date()
      const from = new Date(now)
      from.setDate(from.getDate() - Number(period))
      params.date_from = from.toISOString().split('T')[0]
      params.date_to = now.toISOString().split('T')[0]
    }
    Promise.all([
      api.get(`/admin-panel/masters/${id}/stats/`, { params }).then((r) => r.data).catch(() => null),
      getAdminMasters().then((r) => {
        const list = r.data.results || r.data || []
        return list.find((m: MasterDetail) => m.id === Number(id)) || null
      }).catch(() => null),
    ])
      .then(([statsData, masterData]) => {
        setStats(statsData)
        setMaster(masterData)
        if (masterData?.working_hours) {
          setHoursForm(masterData.working_hours)
        }
        if (masterData?.bio) {
          setBioForm(masterData.bio)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id, period])

  const saveHours = async () => {
    if (!master) return
    try {
      await updateAdminMaster(master.id, { working_hours: hoursForm })
      toast.success('График сохранён')
      setEditingHours(false)
      const res = await getAdminMasters()
      const list = res.data.results || res.data || []
      const updated = list.find((m: MasterDetail) => m.id === master.id)
      if (updated) setMaster(updated)
    } catch {
      toast.error('Ошибка')
    }
  }

  const saveBio = async () => {
    if (!master) return
    try {
      await updateAdminMaster(master.id, { bio: bioForm })
      toast.success('Описание сохранено')
      setEditBio(false)
      if (stats) setStats({ ...stats, bio: bioForm })
    } catch {
      toast.error('Ошибка')
    }
  }

  const applyPreset = (preset: typeof PRESETS[0]) => {
    const newHours: Record<string, { start: string; end: string }> = {}
    for (const key of WEEKDAY_KEYS) {
      if (preset.start) {
        newHours[key] = { start: preset.start, end: preset.end }
      }
    }
    setHoursForm(newHours)
  }

  const openServiceStats = (svcId: number, svcName: string) => {
    setSelectedService({ id: svcId, name: svcName })
    setSvcDateFrom(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
    setSvcDateTo(format(new Date(), 'yyyy-MM-dd'))
    setSvcStatData(null)
    setServiceStatsModal(true)
  }

  const fetchServiceStats = async () => {
    if (!selectedService || !id) return
    setSvcStatLoading(true)
    try {
      const res = await api.get(`/admin-panel/masters/${id}/services/${selectedService.id}/stats/`, {
        params: { date_from: svcDateFrom, date_to: svcDateTo },
      })
      setSvcStatData(res.data)
    } catch {
      toast.error('Ошибка загрузки статистики')
    } finally {
      setSvcStatLoading(false)
    }
  }

  if (loading) return <div className="space-y-6"><div className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-48" /></div>
  if (!master) return <div className="text-center py-16 text-gray-500">Мастер не найден</div>

  const name = stats?.master_name || master.full_name || `${master.first_name || ''} ${master.last_name || ''}`.trim()

  const cards = [
    { label: 'Записей', value: stats?.total_appointments ?? '—', icon: UserIcon, color: 'text-blue-500', bg: 'bg-blue-50' },
    { label: 'Выручка', value: stats?.total_revenue ? `${Number(stats.total_revenue).toLocaleString('ru-RU')} ₽` : '—', icon: CurrencyDollarIcon, color: 'text-green-500', bg: 'bg-green-50' },
    { label: 'Часов работы', value: stats?.total_hours?.toFixed(1) ?? '—', icon: ClockIcon, color: 'text-purple-500', bg: 'bg-purple-50' },
    { label: 'Средний рейтинг', value: stats?.avg_rating ? stats.avg_rating.toFixed(1) : '—', icon: StarIcon, color: 'text-amber-500', bg: 'bg-amber-50' },
  ]

  const masterServices = master.services || []

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{name}</h1>
          <p className="text-sm text-gray-500">{stats?.phone || master.phone}</p>
        </div>
        <span className={`ml-auto text-xs font-medium px-2.5 py-1 rounded-full ${(stats?.is_active ?? master.is_active) ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {(stats?.is_active ?? master.is_active) ? 'Активен' : 'Неактивен'}
        </span>
      </div>

      <div className="flex gap-2 mb-6">
        {([['30', '30 дней'], ['90', '90 дней'], ['365', 'Год'], ['all', 'Всё время']] as const).map(([val, label]) => (
          <button
            key={val}
            onClick={() => setPeriod(val)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              period === val ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {label}
          </button>
        ))}
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
          {masterServices.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Услуги мастера</h2>
              </div>
              <div className="p-3 space-y-2">
                {masterServices.map((ms) => (
                  <button
                    key={ms.service.id}
                    onClick={() => openServiceStats(ms.service.id, ms.service.name)}
                    className="w-full flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-primary-50 hover:text-primary-600 transition-colors text-left"
                  >
                    <span className="text-sm font-medium text-gray-900">{ms.service.name}</span>
                    <ChartBarIcon className="w-4 h-4 text-gray-400" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {stats?.service_stats && stats.service_stats.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Статистика по услугам</h2>
              </div>
              <div className="p-5">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-2 font-medium text-gray-500">Услуга</th>
                      <th className="text-right py-2 font-medium text-gray-500">Кол-во</th>
                      <th className="text-right py-2 font-medium text-gray-500">Выручка</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats?.service_stats?.map((s) => (
                      <tr key={s.service_id} className="border-b border-gray-50">
                        <td className="py-2 text-gray-900">{s.service_name}</td>
                        <td className="py-2 text-right text-gray-600">{s.count}</td>
                        <td className="py-2 text-right font-medium">{Number(s.revenue).toLocaleString('ru-RU')} ₽</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-5 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">О себе</h2>
              <button onClick={() => { setEditBio(true); setBioForm(stats?.bio || master.bio || '') }} className="p-1 text-gray-400 hover:text-primary-500">
                <PencilIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="p-5">
              {editBio ? (
                <div className="space-y-3">
                  <textarea value={bioForm} onChange={(e) => setBioForm(e.target.value)} className="input-field resize-none" rows={3} />
                  <div className="flex gap-2">
                    <button onClick={saveBio} className="btn-primary text-sm py-1.5 px-3 flex items-center gap-1"><CheckIcon className="w-4 h-4" /> Сохранить</button>
                    <button onClick={() => setEditBio(false)} className="btn-secondary text-sm py-1.5 px-3 flex items-center gap-1"><XMarkIcon className="w-4 h-4" /> Отмена</button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-600">{stats?.bio || master.bio || 'Нет описания'}</p>
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-5 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CalendarIcon className="w-5 h-5 text-gray-400" />
                <h2 className="text-lg font-semibold text-gray-900">График работы</h2>
              </div>
              {!editingHours && (
                <button onClick={() => setEditingHours(true)} className="p-1 text-gray-400 hover:text-primary-500">
                  <PencilIcon className="w-4 h-4" />
                </button>
              )}
            </div>
            <div className="p-5">
              {editingHours && (
                <div className="mb-4 flex flex-wrap gap-2">
                  <span className="text-xs text-gray-500 self-center">Шаблоны:</span>
                  {PRESETS.map((p) => (
                    <button
                      key={p.label}
                      onClick={() => applyPreset(p)}
                      className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              )}
              <div className="space-y-2">
                {WEEKDAY_KEYS.map((key, i) => {
                  const day = hoursForm[key]
                  const isOff = !day?.start
                  return (
                    <div key={key} className="flex items-center gap-3">
                      <span className="w-8 text-sm font-medium text-gray-700">{WEEKDAY_LABELS[i]}</span>
                      {editingHours ? (
                        <div className="flex items-center gap-2">
                          <input
                            type="time"
                            value={day?.start || ''}
                            onChange={(e) => setHoursForm({ ...hoursForm, [key]: { ...day, start: e.target.value } })}
                            className="input-field py-1 px-2 text-sm w-28"
                          />
                          <span className="text-gray-400">—</span>
                          <input
                            type="time"
                            value={day?.end || ''}
                            onChange={(e) => setHoursForm({ ...hoursForm, [key]: { ...day, end: e.target.value } })}
                            className="input-field py-1 px-2 text-sm w-28"
                          />
                        </div>
                      ) : (
                        <span className={`text-sm ${isOff ? 'text-gray-400' : 'text-gray-900'}`}>
                          {isOff ? 'Выходной' : `${day.start} — ${day.end}`}
                        </span>
                      )}
                    </div>
                  )
                })}
              </div>
              {editingHours && (
                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
                  <button onClick={saveHours} className="btn-primary text-sm py-1.5 px-3 flex items-center gap-1"><CheckIcon className="w-4 h-4" /> Сохранить</button>
                  <button onClick={() => { setEditingHours(false); setHoursForm(master.working_hours || {}) }} className="btn-secondary text-sm py-1.5 px-3 flex items-center gap-1"><XMarkIcon className="w-4 h-4" /> Отмена</button>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-5 border-b border-gray-100 flex items-center gap-2">
              <ChatBubbleLeftIcon className="w-5 h-5 text-gray-400" />
              <h2 className="text-lg font-semibold text-gray-900">Отзывы</h2>
            </div>
            {stats?.recent_reviews?.length === 0 ? (
              <p className="text-gray-500 text-center py-10">Отзывов пока нет</p>
            ) : (
              <div className="p-5 space-y-4">
                {stats?.recent_reviews?.map((r) => (
                  <div key={r.id} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{r.client_name}</span>
                      <span className="text-xs text-gray-400">{new Date(r.created_at).toLocaleDateString('ru-RU')}</span>
                    </div>
                    <div className="flex items-center gap-1 mb-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <StarIcon key={i} className={`w-4 h-4 ${i < r.rating ? 'text-amber-400' : 'text-gray-200'}`} />
                      ))}
                    </div>
                    <p className="text-sm text-gray-600">{r.comment}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <Modal isOpen={serviceStatsModal} onClose={() => setServiceStatsModal(false)} title={selectedService ? `Статистика: ${selectedService.name}` : 'Статистика'}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата с</label>
              <input type="date" value={svcDateFrom} onChange={(e) => setSvcDateFrom(e.target.value)} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата по</label>
              <input type="date" value={svcDateTo} onChange={(e) => setSvcDateTo(e.target.value)} className="input-field" />
            </div>
          </div>
          <button onClick={fetchServiceStats} disabled={svcStatLoading} className="btn-primary w-full flex items-center justify-center gap-2">
            {svcStatLoading ? 'Загрузка...' : 'Отобразить'}
          </button>

          {svcStatData ? (
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Мастер</span>
                <span className="font-medium text-gray-900">{svcStatData.master_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Услуга</span>
                <span className="font-medium text-gray-900">{svcStatData.service_name}</span>
              </div>
              <div className="border-t border-gray-200 pt-3 grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{svcStatData.total_count}</p>
                  <p className="text-xs text-gray-500 mt-1">Заказов</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{Number(svcStatData.total_revenue).toLocaleString('ru-RU')} ₽</p>
                  <p className="text-xs text-gray-500 mt-1">Заработано</p>
                </div>
              </div>
              {svcStatData.total_count === 0 && (
                <p className="text-center text-sm text-gray-500 bg-white rounded-lg p-3 border border-gray-200">
                  У мастера не было завершённых заказов по данной услуге за выбранный период
                </p>
              )}
            </div>
          ) : (
            <p className="text-center text-gray-400 py-8">Выберите период и нажмите «Отобразить»</p>
          )}
        </div>
      </Modal>
    </div>
  )
}
