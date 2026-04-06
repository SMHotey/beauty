import { useEffect, useState } from 'react'
import { getBlacklist, addToBlacklist, removeFromBlacklist } from '../../api/services'
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import Modal from '../../components/UI/Modal'
import toast from 'react-hot-toast'
import { handleApiError } from '../../utils/apiErrors'

interface BlacklistEntry {
  id: number
  client_phone: string
  reason: string
  created_at: string
}

export default function AdminBlacklistPage() {
  const [entries, setEntries] = useState<BlacklistEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ client_phone: '', reason: '' })

  useEffect(() => {
    fetchBlacklist()
  }, [])

  const fetchBlacklist = () => {
    getBlacklist()
      .then((res) => setEntries(res.data.results || res.data || []))
      .catch((e) => handleApiError(e, 'Ошибка загрузки черного списка'))
      .finally(() => setLoading(false))
  }

  const handleAdd = async () => {
    if (!form.client_phone.trim()) {
      toast.error('Введите номер телефона')
      return
    }
    try {
      await addToBlacklist({ phone: form.client_phone, reason: form.reason })
      toast.success('Добавлено в чёрный список')
      setModalOpen(false)
      setForm({ client_phone: '', reason: '' })
      fetchBlacklist()
    } catch {
      toast.error('Ошибка')
    }
  }

  const handleRemove = async (id: number) => {
    if (!confirm('Удалить из чёрного списка?')) return
    try {
      await removeFromBlacklist(id)
      toast.success('Удалено из чёрного списка')
      fetchBlacklist()
    } catch {
      toast.error('Ошибка')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Чёрный список</h1>
          <p className="text-sm text-gray-500 mt-1">Заблокированные клиенты</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-5 h-5" />
          <span>Добавить</span>
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-16" />
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-16 text-center">
          <p className="text-gray-500">Чёрный список пуст</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Телефон</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Причина</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Дата</th>
                <th className="text-right py-3 px-4 font-medium text-gray-500">Действия</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="py-3 px-4 font-medium text-gray-900">{entry.client_phone}</td>
                  <td className="py-3 px-4 text-gray-600 max-w-xs">{entry.reason || '—'}</td>
                  <td className="py-3 px-4 text-gray-500 text-xs">
                    {new Date(entry.created_at).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleRemove(entry.id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Добавить в чёрный список"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
            <input
              type="tel"
              value={form.client_phone}
              onChange={(e) => setForm({ ...form, client_phone: e.target.value })}
              placeholder="+7 (___) ___-__-__"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Причина</label>
            <textarea
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
              placeholder="Причина блокировки..."
              className="input-field resize-none"
              rows={3}
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button onClick={() => setModalOpen(false)} className="btn-secondary">
              Отмена
            </button>
            <button onClick={handleAdd} className="btn-primary">
              Добавить
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
