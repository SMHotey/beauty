import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAdminMasters, createAdminMaster, updateAdminMaster, deleteAdminMaster } from '../../api/services'
import { PlusIcon, PencilIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'

interface Master {
  id: number
  full_name: string
  first_name: string
  last_name: string
  bio: string
  phone: string
  is_active: boolean
}

export default function AdminMastersPage() {
  const [masters, setMasters] = useState<Master[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingMaster, setEditingMaster] = useState<Master | null>(null)
  const [form, setForm] = useState({ first_name: '', last_name: '', bio: '', phone: '', password: '' })

  useEffect(() => { fetchMasters() }, [])

  const fetchMasters = () => {
    getAdminMasters()
      .then((res) => {
        const list = res.data.results || res.data || []
        setMasters(list.map((m: Master) => ({
          ...m,
          first_name: m.first_name || m.full_name?.split(' ')[0] || '',
          last_name: m.last_name || m.full_name?.split(' ').slice(1).join(' ') || '',
        })))
      })
      .catch((e) => handleApiError(e, 'Ошибка загрузки мастеров'))
      .finally(() => setLoading(false))
  }

  const openCreate = () => {
    setEditingMaster(null)
    setForm({ first_name: '', last_name: '', bio: '', phone: '', password: '' })
    setModalOpen(true)
  }

  const openEdit = (master: Master) => {
    setEditingMaster(master)
    setForm({ first_name: master.first_name, last_name: master.last_name, bio: master.bio, phone: master.phone, password: '' })
    setModalOpen(true)
  }

  const handleSave = async () => {
    try {
      if (editingMaster) {
        await updateAdminMaster(editingMaster.id, { first_name: form.first_name, last_name: form.last_name, bio: form.bio, phone: form.phone })
        toast.success('Мастер обновлён')
      } else {
        await createAdminMaster(form)
        toast.success('Мастер создан')
      }
      setModalOpen(false)
      fetchMasters()
    } catch {
      toast.error('Ошибка при сохранении')
    }
  }

  const handleToggleActive = async (master: Master) => {
    try {
      await updateAdminMaster(master.id, { is_active: !master.is_active })
      toast.success(master.is_active ? 'Мастер уволен' : 'Мастер принят')
      fetchMasters()
    } catch {
      toast.error('Ошибка')
    }
  }

  if (loading) return <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-16" />)}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Мастера</h1>
          <p className="text-sm text-gray-500 mt-1">Управление мастерами салона</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-5 h-5" />
          <span>Добавить</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left py-3 px-4 font-medium text-gray-500">Имя</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">О себе</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Телефон</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Статус</th>
              <th className="text-right py-3 px-4 font-medium text-gray-500">Действия</th>
            </tr>
          </thead>
          <tbody>
            {masters.map((m) => (
              <tr key={m.id} className={`border-b border-gray-50 hover:bg-gray-50 transition-colors ${!m.is_active ? 'opacity-50' : ''}`}>
                <td className="py-3 px-4">
                  <Link to={`/admin/masters/${m.id}`} className="font-medium text-primary-500 hover:underline">
                    {m.first_name} {m.last_name}
                  </Link>
                </td>
                <td className="py-3 px-4 text-gray-600 max-w-xs truncate">{m.bio || '—'}</td>
                <td className="py-3 px-4 text-gray-600">{m.phone}</td>
                <td className="py-3 px-4">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${m.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {m.is_active ? 'Активен' : 'Уволен'}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Link to={`/admin/masters/${m.id}`} className="p-1.5 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors" title="Профиль">
                      <UserCircleIcon className="w-4 h-4" />
                    </Link>
                    <button onClick={() => openEdit(m)} className="p-1.5 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors" title="Редактировать">
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleToggleActive(m)}
                      className={`p-1.5 rounded-lg transition-colors ${m.is_active ? 'text-gray-400 hover:text-red-500 hover:bg-red-50' : 'text-gray-400 hover:text-green-500 hover:bg-green-50'}`}
                      title={m.is_active ? 'Уволить' : 'Принять'}
                    >
                      {m.is_active ? (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                      ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      )}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingMaster ? 'Редактировать мастера' : 'Новый мастер'}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
              <input type="text" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
              <input type="text" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="input-field" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">О себе</label>
            <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} className="input-field resize-none" rows={2} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
            <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="input-field" />
          </div>
          {!editingMaster && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
              <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input-field" />
            </div>
          )}
          <div className="flex gap-3 justify-end pt-2">
            <button onClick={() => setModalOpen(false)} className="btn-secondary">Отмена</button>
            <button onClick={handleSave} className="btn-primary">{editingMaster ? 'Сохранить' : 'Создать'}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
