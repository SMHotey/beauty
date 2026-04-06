import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getService } from '../api/services'
import { handleApiError } from '../utils/apiErrors'
import { serviceImages, categoryImages } from '../utils/images'

interface ServiceDetail {
  id: number
  name: string
  slug: string
  base_price: number
  base_duration_minutes: number
  description: string
  category: { name: string }
  category_name: string
  masters: { id: number; full_name: string; is_active: boolean }[]
}

export default function ServiceDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const [service, setService] = useState<ServiceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    setError(null)
    getService(slug)
      .then((res) => setService(res.data))
      .catch((e) => {
        handleApiError(e, 'Ошибка загрузки услуги')
        setError('Не удалось загрузить информацию об услуге')
      })
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-neutral-bg to-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-80 bg-gray-200 rounded-2xl mb-8" />
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4" />
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-8" />
            <div className="h-4 bg-gray-200 rounded w-full mb-3" />
            <div className="h-4 bg-gray-200 rounded w-5/6" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !service) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-neutral-bg to-white flex items-center justify-center">
        <div className="text-center py-16">
          <div className="text-6xl mb-4">😔</div>
          <p className="text-gray-500 text-lg mb-4">{error || 'Услуга не найдена'}</p>
          <Link to="/services" className="btn-primary">
            Вернуться к услугам
          </Link>
        </div>
      </div>
    )
  }

  const activeMasters = service.masters?.filter((m) => m.is_active) || []
  const imageUrl = serviceImages[service.slug] || categoryImages[service.category_name?.toLowerCase() || ''] || categoryImages[service.category?.name?.toLowerCase() || '']

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-bg to-white">
      {/* Hero Image */}
      <div className="relative h-72 sm:h-96 overflow-hidden">
        <img
          src={imageUrl}
          alt={service.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white text-sm mb-4 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Назад к услугам
          </Link>
          <h1 className="text-3xl sm:text-4xl font-bold text-white text-balance">
            {service.name}
          </h1>
          <p className="text-white/80 mt-2">{service.category_name || service.category?.name}</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10 pb-16">
        {/* Info Card */}
        <div className="card-flat bg-white rounded-2xl shadow-card border border-gray-100/50 p-6 sm:p-8 mb-8">
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="text-center p-4 bg-primary-50 rounded-xl">
              <div className="text-3xl font-bold text-primary-600">
                {Number(service.base_price).toLocaleString('ru-RU')} ₽
              </div>
              <div className="text-sm text-gray-500 mt-1">Стоимость</div>
            </div>
            <div className="text-center p-4 bg-rose-50 rounded-xl">
              <div className="text-3xl font-bold text-rose-600">
                {service.base_duration_minutes}
              </div>
              <div className="text-sm text-gray-500 mt-1">Минут</div>
            </div>
          </div>

          {service.description && (
            <div className="mb-8">
              <h3 className="font-semibold text-gray-900 mb-3">Описание</h3>
              <p className="text-gray-600 leading-relaxed">{service.description}</p>
            </div>
          )}

          {activeMasters.length > 0 && (
            <div className="mb-8">
              <h3 className="font-semibold text-gray-900 mb-3">Мастера</h3>
              <div className="flex flex-wrap gap-3">
                {activeMasters.map((master) => (
                  <Link
                    key={master.id}
                    to={`/masters/${master.id}`}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-xl hover:bg-primary-50 hover:text-primary-600 transition-colors text-sm font-medium text-gray-700"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-200 to-rose-200 flex items-center justify-center text-white text-xs font-bold">
                      {master.full_name[0]}
                    </div>
                    {master.full_name}
                  </Link>
                ))}
              </div>
            </div>
          )}

          <Link
            to={`/booking?service=${service.id}`}
            className="btn-primary w-full text-center text-lg py-4 block"
          >
            Записаться на услугу
          </Link>
        </div>
      </div>
    </div>
  )
}
