import { useState } from 'react'
import { getSalesReport } from '../../api/services'
import { format, subDays } from 'date-fns'
import toast from 'react-hot-toast'

export default function AdminReportsPage() {
  const [dateFrom, setDateFrom] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [dateTo, setDateTo] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [loading, setLoading] = useState(false)

  const handleDownload = async () => {
    setLoading(true)
    try {
      const res = await getSalesReport({ date_from: dateFrom, date_to: dateTo, format: 'xlsx' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `sales_report_${dateFrom}_${dateTo}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Отчёт скачан')
    } catch {
      toast.error('Ошибка при скачивании отчёта')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Отчёты</h1>
        <p className="text-sm text-gray-500 mt-1">Экспорт данных о продажах</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-lg">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Отчёт по продажам</h2>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата с</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Дата по</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          <button
            onClick={handleDownload}
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Загрузка...</span>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Скачать Excel
              </>
            )}
          </button>
          <p className="text-xs text-gray-400 text-center">
            Отчёт включает: дату, выручку, количество записей и средний чек
          </p>
        </div>
      </div>
    </div>
  )
}
