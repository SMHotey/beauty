import { useEffect, useState } from 'react'
import { getPromotions, getServices } from '../../api/services'
import api from '../../api/client'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'

interface Promotion {
  id: number
  name: string
  description: string
  discount_percent: number
  start_date: string
  end_date: string
  promo_code: string | null
  is_active: boolean
  applicable_services: number[]
}

interface Service {
  id: number
  name: string
}

export default function AdminPromotionsPage() {
  const [promotions, setPromotions] = useState<Promotion[]>([])
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingPromo, setEditingPromo] = useState<Promotion | null>(null)
  const [form, setForm] = useState({
    name: '', description: '', discount_percent: '', start_date: '', end_date: '',
    promo_code: '', is_active: true, service_ids: [] as number[],
  })

  useEffect(() => {
    Promise.all([
      getPromotions().catch((e) => { handleApiError(e); return null }),
      getServices({}).catch((e) => { handleApiError(e); return null }),
    ])
      .then(([promoRes, svcRes]) => {
        if (promoRes) setPromotions(promoRes.data.results || promoRes.data || [])
        if (svcRes) setServices(svcRes.data.results || svcRes.data || [])
      })
      .finally(() => setLoading(false))
  }, [])

  const openCreate = () => {
    setEditingPromo(null)
    setForm({ name: '', description: '', discount_percent: '', start_date: '', end_date: '', promo_code: '', is_active: true, service_ids: [] })
    setModalOpen(true)
  }

  const openEdit = (promo: Promotion) => {
    setEditingPromo(promo)
    setForm({
      name: promo.name,
      description: promo.description,
      discount_percent: String(promo.discount_percent),
      start_date: promo.start_date?.split('T')[0] || '',
      end_date: promo.end_date?.split('T')[0] || '',
      promo_code: promo.promo_code || '',
      is_active: promo.is_active,
      service_ids: promo.applicable_services || [],
    })
    setModalOpen(true)
  }

  const handleSave = async () => {
    try {
      const data: any = {
        name: form.name,
        description: form.description,
        discount_percent: Number(form.discount_percent),
        start_date: form.start_date,
        end_date: form.end_date,
        promo_code: form.promo_code || null,
        is_active: form.is_active,
      }
      if (editingPromo) {
        await api.patch(`/promotions/promotions/${editingPromo.id}/`, data)
        toast.success('Акция обновлена')
      } else {
        await api.post('/promotions/promotions/', data)
        toast.success('Акция создана')
      }
      setModalOpen(false)
      const res = await getPromotions()
      setPromotions(res.data.results || res.data || [])
    } catch (err: any) {
      const msg = err?.response?.data ? JSON.stringify(err.response.data) : 'Ошибка'
      toast.error(msg)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить акцию?')) return
    try {
      await api.delete(`/promotions/promotions/${id}/`)
      toast.success('Акция удалена')
      const res = await getPromotions()
      setPromotions(res.data.results || res.data || [])
    } catch {
      toast.error('Ошибка')
    }
  }

  if (loading) return <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-16" />)}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Акции</h1>
          <p className="text-sm text-gray-500 mt-1">Управление акциями и спецпредложениями</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-5 h-5" />
          <span>Добавить</span>
        </button>
      </div>

      {promotions.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-16 text-center">
          <p className="text-gray-500 mb-4">Акций пока нет</p>
          <button onClick={openCreate} className="btn-primary">Создать первую акцию</button>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Название</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Скидка</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Промокод</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Период</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Статус</th>
                <th className="text-right py-3 px-4 font-medium text-gray-500">Действия</th>
              </tr>
            </thead>
            <tbody>
              {promotions.map((promo) => (
                <tr key={promo.id} className={`border-b border-gray-50 hover:bg-gray-50 transition-colors ${!promo.is_active ? 'opacity-50' : ''}`}>
                  <td className="py-3 px-4">
                    <p className="font-medium text-gray-900">{promo.name}</p>
                    <p className="text-xs text-gray-500 truncate max-w-xs">{promo.description}</p>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-primary-500 font-bold">-{promo.discount_percent}%</span>
                  </td>
                  <td className="py-3 px-4">
                    {promo.promo_code ? (
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">{promo.promo_code}</code>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-gray-600 text-xs">
                    {new Date(promo.start_date).toLocaleDateString('ru-RU')} — {new Date(promo.end_date).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${promo.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {promo.is_active ? 'Активна' : 'Неактивна'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => openEdit(promo)} className="p-1.5 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(promo.id)} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingPromo ? 'Редактировать акцию' : 'Новая акция'}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field resize-none" rows={2} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Скидка (%)</label>
              <input type="number" value={form.discount_percent} onChange={(e) => setForm({ ...form, discount_percent: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Промокод</label>
              <input type="text" value={form.promo_code} onChange={(e) => setForm({ ...form, promo_code: e.target.value })} className="input-field" placeholder="Необязательно" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата начала</label>
              <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата окончания</label>
              <input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} className="input-field" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Применяется к услугам</label>
            <div className="space-y-1 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {services.map((s) => (
                <label key={s.id} className="flex items-center gap-2 py-1 px-2 rounded hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.service_ids.includes(s.id)}
                    onChange={(e) => {
                      const ids = e.target.checked ? [...form.service_ids, s.id] : form.service_ids.filter((id) => id !== s.id)
                      setForm({ ...form, service_ids: ids })
                    }}
                    className="rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">{s.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="promo_active" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="rounded border-gray-300 text-primary-500 focus:ring-primary-500" />
            <label htmlFor="promo_active" className="text-sm text-gray-700">Активна</label>
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button onClick={() => setModalOpen(false)} className="btn-secondary">Отмена</button>
            <button onClick={handleSave} className="btn-primary">{editingPromo ? 'Сохранить' : 'Создать'}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
