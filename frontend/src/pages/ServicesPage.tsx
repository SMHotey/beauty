import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getCategories, getServices } from '../api/services'
import type { Category, Service } from '../types'
import { handleApiError } from '../utils/apiErrors'
import { categoryImages, categoryIcons, serviceImages } from '../utils/images'

export default function ServicesPage() {
  const [searchParams] = useSearchParams()
  const [categories, setCategories] = useState<Category[]>([])
  const [allServices, setAllServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState<string>(searchParams.get('category') || '')

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([getCategories(), getServices({ limit: '100' })])
      .then(([catsRes, svcRes]) => {
        const cats = catsRes.data.results || catsRes.data
        const svcs = svcRes.data.results || svcRes.data
        setCategories(Array.isArray(cats) ? cats : [])
        setAllServices(Array.isArray(svcs) ? svcs : [])
      })
      .catch((e) => {
        handleApiError(e, 'Ошибка загрузки данных')
        setCategories([])
        setAllServices([])
        setError('Не удалось загрузить данные. Попробуйте позже.')
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredServices = activeCategory
    ? allServices.filter((s) => Number(s.category) === (categories.find(c => c.slug === activeCategory)?.id ?? 0))
    : allServices

  const handleCategoryClick = (slug: string) => {
    setActiveCategory(slug === activeCategory ? '' : slug)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-bg to-white">
      {/* Header Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary-500 via-primary-600 to-rose-500 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.4%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')] opacity-50" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <h1 className="text-4xl sm:text-5xl font-bold text-center mb-4 animate-fade-in-down">
            {activeCategory ? categories.find(c => c.slug === activeCategory)?.name || 'Наши услуги' : 'Наши услуги'}
          </h1>
          <p className="text-lg sm:text-xl text-white/90 text-center max-w-2xl mx-auto animate-fade-in-up">
            Широкий спектр beauty-услуг для вашей красоты и уверенности
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Category Filters */}
        {loading ? (
          <div className="flex flex-wrap gap-3 mb-10 animate-pulse">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-12 w-28 bg-gray-200 rounded-2xl" />
            ))}
          </div>
        ) : categories.length > 0 && (
          <div className="flex flex-wrap gap-3 mb-10 animate-fade-in">
            <button
              onClick={() => setActiveCategory('')}
              className={`px-5 py-3 rounded-2xl text-sm font-semibold transition-all duration-300 ${
                !activeCategory
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                  : 'bg-white text-gray-600 border-2 border-gray-100 hover:border-primary-200 hover:text-primary-600 hover:shadow-sm'
              }`}
            >
              Все услуги
            </button>
            {categories.map((cat, idx) => (
              <button
                key={cat.id}
                onClick={() => handleCategoryClick(cat.slug)}
                className={`px-5 py-3 rounded-2xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 ${
                  activeCategory === cat.slug
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                    : 'bg-white text-gray-600 border-2 border-gray-100 hover:border-primary-200 hover:text-primary-600 hover:shadow-sm'
                }`}
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <span>{categoryIcons[cat.slug] || '💫'}</span>
                {cat.name}
              </button>
            ))}
          </div>
        )}

        {/* Services Grid */}
        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-48 bg-gray-200 rounded-xl mb-4" />
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">😔</div>
            <p className="text-gray-500 text-lg mb-4">{error}</p>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Попробовать снова
            </button>
          </div>
        ) : filteredServices.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">✨</div>
            <p className="text-gray-500 text-lg">
              {activeCategory ? 'В этой категории пока нет услуг' : 'Услуги скоро появятся'}
            </p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredServices.map((service, idx) => (
              <Link
                key={service.id}
                to={`/services/${service.slug}`}
                className="group bg-white rounded-2xl shadow-soft border border-gray-100/50 overflow-hidden transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1 hover:border-primary-100"
                style={{ animationDelay: `${idx * 75}ms` }}
              >
                {/* Image */}
                <div className="relative h-48 overflow-hidden bg-gradient-to-br from-primary-100 to-rose-100">
                    <img
                    src={serviceImages[service.slug] || categoryImages[service.category_name?.toLowerCase() || ''] || 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&h=400&fit=crop'}
                    alt={service.name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                  <div className="absolute top-3 right-3">
                    <span className="bg-white/90 backdrop-blur-sm text-primary-600 font-bold px-3 py-1.5 rounded-full text-sm shadow-sm">
                      {Number(service.base_price).toLocaleString('ru-RU')} ₽
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="font-semibold text-gray-900 text-lg mb-2 group-hover:text-primary-600 transition-colors">
                    {service.name}
                  </h3>
                  {service.description && (
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2 leading-relaxed">
                      {service.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <span className="flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                      {service.category_name}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {service.base_duration_minutes} мин
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
