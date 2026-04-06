import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getServices, getCategories, createService, updateService, deleteService, getAdminMasters } from '../../api/services'
import api from '../../api/client'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ChartBarIcon,
  UserIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'
import { format, subDays } from 'date-fns'

const CATEGORY_ICONS: Record<string, string> = {
  hair: '✂️',
  nails: '💅',
  cosmetology: '🧴',
  makeup: '💄',
  massage: '💆',
}

const CATEGORY_GRADIENTS: Record<string, string> = {
  hair: 'from-pink-500 to-rose-500',
  nails: 'from-purple-500 to-violet-500',
  cosmetology: 'from-blue-500 to-cyan-500',
  makeup: 'from-amber-500 to-orange-500',
  massage: 'from-emerald-500 to-teal-500',
}

interface Category {
  id: number
  name: string
  slug: string
  icon: string
}

interface ServiceMaster {
  id: number
  full_name: string
  is_active: boolean
}

interface Service {
  id: number
  name: string
  slug: string
  description: string
  base_price: string
  base_duration_minutes: number
  category: { id: number; name: string } | number
  is_active: boolean
  gender_target: string
  category_name: string
  masters: ServiceMaster[]
}

interface Master {
  id: number
  full_name: string
  is_active: boolean
}

interface ServiceStat {
  master_id: number
  master_name: string
  services: {
    service_id: number
    service_name: string
    count: number
    revenue: string
  }[]
  total_count: number
  total_revenue: string
}

function getCatId(cat: { id: number; name: string } | number | undefined): number | undefined {
  if (cat === undefined || cat === null) return undefined
  if (typeof cat === 'number') return cat
  if (typeof cat === 'object' && cat.id) return cat.id
  return undefined
}

export default function AdminServicesPage() {
  const [services, setServices] = useState<Service[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [masters, setMasters] = useState<Master[]>([])
  const [loading, setLoading] = useState(true)
  const [openCategories, setOpenCategories] = useState<Set<number>>(new Set())
  const [modalOpen, setModalOpen] = useState(false)
  const [editingService, setEditingService] = useState<Service | null>(null)
  const [form, setForm] = useState({ name: '', description: '', base_price: '', base_duration_minutes: '', category: '', gender_target: 'unisex', is_active: true, master_ids: [] as number[] })

  const [statsModal, setStatsModal] = useState(false)
  const [statsService, setStatsService] = useState<Service | null>(null)
  const [statsDateFrom, setStatsDateFrom] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [statsDateTo, setStatsDateTo] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [statsData, setStatsData] = useState<ServiceStat[]>([])
  const [statsLoading, setStatsLoading] = useState(false)

  const refreshServices = async () => {
    try {
      const res = await getServices({})
      const data = res.data.results || res.data || []
      console.log('refreshServices:', data.length, 'items', data.map((s: Service) => ({ id: s.id, name: s.name, cat: s.category })))
      setServices(data)
    } catch (e) {
      handleApiError(e, 'Ошибка загрузки услуг')
    }
  }

  useEffect(() => {
    Promise.all([
      refreshServices(),
      getCategories().catch((e) => { handleApiError(e); return null }),
      getAdminMasters().catch(() => null),
    ])
      .then(([_, catRes, masterRes]) => {
        if (catRes) setCategories(catRes.data.results || catRes.data || [])
        if (masterRes) setMasters(masterRes.data.results || masterRes.data || [])
      })
      .finally(() => setLoading(false))
  }, [])

  const toggleCategory = (catId: number) => {
    setOpenCategories((prev) => {
      const next = new Set(prev)
      if (next.has(catId)) next.delete(catId)
      else next.add(catId)
      return next
    })
  }

  const openCreate = (categoryId?: number) => {
    if (categories.length === 0) {
      toast.error('Категории не загружены')
      return
    }
    const catId = categoryId || categories[0]?.id
    setEditingService(null)
    setForm({ name: '', description: '', base_price: '', base_duration_minutes: '', category: String(catId), gender_target: 'unisex', is_active: true, master_ids: [] })
    setModalOpen(true)
    if (categoryId) {
      setOpenCategories((prev) => {
        const next = new Set(prev)
        next.add(categoryId)
        return next
      })
    }
  }

  const openEdit = (svc: Service) => {
    setEditingService(svc)
    const catId = getCatId(svc.category)
    setForm({
      name: svc.name,
      description: svc.description || '',
      base_price: String(svc.base_price),
      base_duration_minutes: String(svc.base_duration_minutes),
      category: String(catId || ''),
      gender_target: svc.gender_target,
      is_active: svc.is_active,
      master_ids: svc.masters?.map((m) => m.id) || [],
    })
    setModalOpen(true)
    if (catId) {
      setOpenCategories((prev) => {
        const next = new Set(prev)
        next.add(catId)
        return next
      })
    }
  }

  const openStats = (svc: Service) => {
    setStatsService(svc)
    setStatsData([])
    setStatsDateFrom(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
    setStatsDateTo(format(new Date(), 'yyyy-MM-dd'))
    setStatsModal(true)
  }

  const fetchStats = async () => {
    if (!statsService) return
    setStatsLoading(true)
    try {
      const res = await api.get(`/admin-panel/services/${statsService.id}/stats/`, {
        params: { date_from: statsDateFrom, date_to: statsDateTo },
      })
      setStatsData(res.data)
    } catch {
      toast.error('Ошибка загрузки статистики')
    } finally {
      setStatsLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const data: any = {
        name: form.name,
        description: form.description,
        base_price: Number(form.base_price),
        base_duration_minutes: Number(form.base_duration_minutes),
        category: Number(form.category),
        gender_target: form.gender_target,
        is_active: form.is_active,
      }
      if (editingService) {
        await updateService(editingService.id, data)
        if (editingService.masters) {
          const currentIds = editingService.masters.map((m) => m.id)
          const toRemove = currentIds.filter((id) => !form.master_ids.includes(id))
          const toAdd = form.master_ids.filter((id) => !currentIds.includes(id))
          const token = localStorage.getItem('access_token')
          for (const mid of toRemove) {
            try { await fetch(`/api/v1/admin-panel/masters/${mid}/services/`, { method: 'DELETE', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ service_id: editingService.id }) }) } catch {}
          }
          for (const mid of toAdd) {
            try { await fetch(`/api/v1/admin-panel/masters/${mid}/services/`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ service_id: editingService.id }) }) } catch {}
          }
        }
        toast.success('Услуга обновлена')
      } else {
        await createService(data)
        toast.success('Услуга создана')
      }
    } catch (err: any) {
      const msg = err?.response?.data ? JSON.stringify(err.response.data) : 'Ошибка при сохранении'
      toast.error(msg)
      return
    }

    setModalOpen(false)
    await refreshServices()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Скрыть услугу?')) return
    try {
      await deleteService(id)
      toast.success('Услуга скрыта')
      await refreshServices()
    } catch {
      toast.error('Ошибка при удалении')
    }
  }

  if (loading) return <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-16" />)}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Услуги</h1>
          <p className="text-sm text-gray-500 mt-1">Управление категориями и услугами</p>
        </div>
        <button onClick={() => openCreate()} className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-5 h-5" />
          <span>Добавить</span>
        </button>
      </div>

      <div className="space-y-3">
        {categories.map((cat) => {
          const catServices = services.filter((s) => getCatId(s.category) === cat.id)
          const gradient = CATEGORY_GRADIENTS[cat.slug] || 'from-gray-500 to-gray-600'
          const emoji = CATEGORY_ICONS[cat.slug] || '🔧'
          const isOpen = openCategories.has(cat.id)
          return (
            <div key={cat.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <button
                onClick={() => toggleCategory(cat.id)}
                className={`w-full bg-gradient-to-r ${gradient} px-4 py-3 flex items-center justify-between`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{emoji}</span>
                  <div className="text-left">
                    <h2 className="text-base font-bold text-white">{cat.name}</h2>
                    <p className="text-white/70 text-xs">{catServices.length} {catServices.length === 1 ? 'услуга' : catServices.length < 5 ? 'услуги' : 'услуг'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span onClick={(e) => e.stopPropagation()} className="bg-white/20 hover:bg-white/30 text-white px-2.5 py-1 rounded-md text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer">
                    <PlusIcon className="w-3 h-3" />
                    Добавить
                  </span>
                  {isOpen ? <ChevronUpIcon className="w-5 h-5 text-white" /> : <ChevronDownIcon className="w-5 h-5 text-white" />}
                </div>
              </button>

              {isOpen && (
                <div className="divide-y divide-gray-100">
                  {catServices.length === 0 ? (
                    <div className="p-8 text-center">
                      <p className="text-gray-500 mb-3">В этой категории пока нет услуг</p>
                      <button onClick={() => openCreate(cat.id)} className="btn-primary text-sm">Добавить первую услугу</button>
                    </div>
                  ) : (
                    catServices.map((svc) => (
                      <div key={svc.id} className={`p-4 flex items-start gap-4 ${!svc.is_active ? 'opacity-50' : ''}`}>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900">{svc.name}</h3>
                            {!svc.is_active && <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">Скрыта</span>}
                          </div>
                          {svc.description && <p className="text-sm text-gray-500 mb-2 line-clamp-2">{svc.description}</p>}
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span className="font-medium text-gray-900">{Number(svc.base_price).toLocaleString('ru-RU')} ₽</span>
                            <span>{svc.base_duration_minutes} мин</span>
                          </div>
                          {svc.masters && svc.masters.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {svc.masters.slice(0, 5).map((m) => (
                                <Link
                                  key={m.id}
                                  to={`/admin/masters/${m.id}`}
                                  className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full hover:bg-primary-50 hover:text-primary-500 transition-colors"
                                >
                                  {m.full_name}
                                </Link>
                              ))}
                              {svc.masters.length > 5 && (
                                <span className="text-xs text-gray-400">+{svc.masters.length - 5}</span>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          <button onClick={() => openStats(svc)} className="p-2 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors" title="Статистика">
                            <ChartBarIcon className="w-4 h-4" />
                          </button>
                          <button onClick={() => openEdit(svc)} className="p-2 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors" title="Редактировать">
                            <PencilIcon className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDelete(svc.id)} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Удалить">
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingService ? 'Редактировать услугу' : 'Новая услуга'}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field resize-none" rows={3} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Категория</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="input-field">
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Цена (₽)</label>
              <input type="number" value={form.base_price} onChange={(e) => setForm({ ...form, base_price: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Длительность (мин)</label>
              <input type="number" value={form.base_duration_minutes} onChange={(e) => setForm({ ...form, base_duration_minutes: e.target.value })} className="input-field" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Пол</label>
            <select value={form.gender_target} onChange={(e) => setForm({ ...form, gender_target: e.target.value })} className="input-field">
              <option value="unisex">Унисекс</option>
              <option value="female">Женская</option>
              <option value="male">Мужская</option>
              <option value="children">Детская</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Мастера</label>
            <div className="space-y-1 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {masters.map((m) => {
                const checked = form.master_ids.includes(m.id)
                return (
                  <label key={m.id} className="flex items-center gap-2 py-1 px-2 rounded hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={(e) => {
                        const ids = e.target.checked ? [...form.master_ids, m.id] : form.master_ids.filter((id) => id !== m.id)
                        setForm({ ...form, master_ids: ids })
                      }}
                      className="rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                    />
                    <UserIcon className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-700">{m.full_name}</span>
                    {!m.is_active && <span className="text-xs text-gray-400">(неактивен)</span>}
                  </label>
                )
              })}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_active2" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="rounded border-gray-300 text-primary-500 focus:ring-primary-500" />
            <label htmlFor="is_active2" className="text-sm text-gray-700">Активна</label>
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button onClick={() => setModalOpen(false)} className="btn-secondary">Отмена</button>
            <button onClick={handleSave} className="btn-primary">{editingService ? 'Сохранить' : 'Создать'}</button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={statsModal} onClose={() => setStatsModal(false)} title={statsService ? `Статистика: ${statsService.name}` : 'Статистика'}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата с</label>
              <input type="date" value={statsDateFrom} onChange={(e) => setStatsDateFrom(e.target.value)} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата по</label>
              <input type="date" value={statsDateTo} onChange={(e) => setStatsDateTo(e.target.value)} className="input-field" />
            </div>
          </div>
          <button onClick={fetchStats} disabled={statsLoading} className="btn-primary w-full flex items-center justify-center gap-2">
            {statsLoading ? 'Загрузка...' : 'Отобразить'}
          </button>

          {statsData.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-medium text-gray-500 sticky left-0 bg-white z-10">Мастер</th>
                    {statsData[0]?.services.map((s) => (
                      <th key={s.service_id} className="text-center py-2 px-2 font-medium text-gray-500 min-w-[80px]">
                        {s.service_name}
                      </th>
                    ))}
                    <th className="text-center py-2 px-2 font-medium text-gray-500 min-w-[80px] bg-gray-50">Итого</th>
                  </tr>
                </thead>
                <tbody>
                  {statsData.map((row) => (
                    <tr key={row.master_id} className="border-b border-gray-100">
                      <td className="py-2 px-2 sticky left-0 bg-white z-10">
                        <Link to={`/admin/masters/${row.master_id}`} className="font-medium text-primary-500 hover:underline">
                          {row.master_name}
                        </Link>
                      </td>
                      {row.services.map((s) => (
                        <td key={s.service_id} className="py-2 px-2 text-center">
                          <div className="font-medium text-gray-900">{s.count}</div>
                          <div className="text-gray-400">{Number(s.revenue).toLocaleString('ru-RU')} ₽</div>
                        </td>
                      ))}
                      <td className="py-2 px-2 text-center bg-gray-50">
                        <div className="font-bold text-gray-900">{row.total_count}</div>
                        <div className="text-gray-500">{Number(row.total_revenue).toLocaleString('ru-RU')} ₽</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Modal>
    </div>
  )
}
