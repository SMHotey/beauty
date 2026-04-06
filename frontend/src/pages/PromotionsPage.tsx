import { useEffect, useState } from 'react'
import { getPromotions } from '../api/services'
import { SkeletonCard } from '../components/UI/Skeleton'
import { handleApiError } from '../utils/apiErrors'

interface Promotion {
  id: number
  title: string
  description: string
  discount_percent: number
  valid_from: string
  valid_until: string
  image: string
  services: { name: string }[]
}

export default function PromotionsPage() {
  const [promotions, setPromotions] = useState<Promotion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPromotions()
      .then((res) => setPromotions(res.data.results || res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки акций'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Акции и скидки</h1>

      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : promotions.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">Акций пока нет</p>
          <p className="text-gray-400 text-sm mt-1">Загляните позже — мы регулярно обновляем предложения</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {promotions.map((promo) => (
            <div key={promo.id} className="card border-l-4 border-l-primary-500">
              {promo.image && (
                <img src={promo.image} alt={promo.title} className="w-full h-40 object-cover rounded-lg mb-4" />
              )}
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{promo.title}</h3>
                <span className="bg-primary-500 text-white text-xs font-bold px-2 py-1 rounded-full flex-shrink-0 ml-2">
                  -{promo.discount_percent}%
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{promo.description}</p>
              {promo.services && promo.services.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {promo.services.map((svc, i) => (
                    <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                      {svc.name}
                    </span>
                  ))}
                </div>
              )}
              <p className="text-xs text-gray-400">
                {new Date(promo.valid_from).toLocaleDateString('ru-RU')} — {new Date(promo.valid_until).toLocaleDateString('ru-RU')}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
