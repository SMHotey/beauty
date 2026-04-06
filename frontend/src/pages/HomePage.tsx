import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCategories, getServices, getMasters, getPromotions } from '../api/services'
import type { Category, Service, Master, Promotion } from '../types'
import { handleApiError } from '../utils/apiErrors'
import { categoryImages, categoryIcons, heroImages, serviceImages } from '../utils/images'

export default function HomePage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [allServices, setAllServices] = useState<Service[]>([])
  const [masters, setMasters] = useState<Master[]>([])
  const [promotions, setPromotions] = useState<Promotion[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCategory, setActiveCategory] = useState<string>('')

  useEffect(() => {
    Promise.all([
      getCategories(),
      getServices({ limit: '100' }),
      getMasters({ limit: '4' }),
      getPromotions(),
    ])
      .then(([catsRes, svcRes, mastRes, promoRes]) => {
        setCategories(catsRes.data.results || catsRes.data)
        setAllServices(svcRes.data.results || svcRes.data)
        setMasters(mastRes.data.results || mastRes.data)
        setPromotions(promoRes.data.results || promoRes.data)
      })
      .catch((e) => handleApiError(e, 'Ошибка загрузки данных'))
      .finally(() => setLoading(false))
  }, [])

  const activeCategoryId = activeCategory && categories.length > 0
    ? categories.find(c => c.slug === activeCategory)?.id ?? null
    : null

  const filteredServices = activeCategoryId
    ? allServices.filter((s) => Number(s.category) === activeCategoryId)
    : allServices

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-500 via-primary-600 to-rose-500 text-white">
        <div className="absolute inset-0">
          <img
            src={heroImages[0]}
            alt=""
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-primary-600/90 via-primary-700/85 to-rose-600/90" />
        </div>
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.4%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')]" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 lg:py-40">
          <div className="text-center animate-fade-in">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 text-balance leading-tight">
              Салон красоты
              <br />
              <span className="text-cream-200">Beauty</span>
            </h1>
            <p className="text-lg sm:text-xl text-white/90 mb-10 max-w-2xl mx-auto text-balance">
              Запишитесь онлайн к лучшим мастерам. Качество и комфорт — наш приоритет.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/booking" className="btn-primary bg-white text-primary-600 hover:bg-cream-100 shadow-xl shadow-black/20 text-lg px-10 py-4">
                Записаться онлайн
              </Link>
              <Link to="/services" className="btn-primary bg-white text-primary-600 hover:bg-cream-100 shadow-xl shadow-black/20 text-lg px-10 py-4">
                Каталог услуг
              </Link>
              <Link to="/services" className="btn-primary bg-white text-primary-600 hover:bg-cream-100 shadow-xl shadow-black/20 text-lg px-10 py-4">
                Каталог услуг
              </Link>
            </div>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-neutral-bg to-transparent" />
      </section>

      {/* Categories Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div className="text-center mb-12">
          <h2 className="section-title">Наши услуги</h2>
          <p className="section-subtitle mx-auto">Выберите категорию и найдите идеальную процедуру для себя</p>
        </div>
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="card text-center animate-pulse">
                <div className="h-24 bg-gray-200 rounded-xl mb-3" />
                <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6">
            <button
              onClick={() => setActiveCategory('')}
              className={`group relative overflow-hidden rounded-2xl shadow-soft border transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1 ${
                !activeCategory
                  ? 'ring-2 ring-primary-500 border-primary-200'
                  : 'border-gray-100/50'
              }`}
            >
              <div className="aspect-square overflow-hidden bg-gradient-to-br from-primary-100 to-rose-100 flex items-center justify-center">
                <span className="text-4xl">💫</span>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                <h3 className="font-semibold text-sm sm:text-base">Все услуги</h3>
              </div>
            </button>
            {categories.map((cat, idx) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(activeCategory === cat.slug ? '' : cat.slug)}
                className={`group relative overflow-hidden rounded-2xl shadow-soft border transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1 ${
                  activeCategory === cat.slug
                    ? 'ring-2 ring-primary-500 border-primary-200'
                    : 'border-gray-100/50'
                }`}
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="aspect-square overflow-hidden bg-gradient-to-br from-primary-50 to-rose-50">
                  <img
                    src={categoryImages[cat.slug] || heroImages[0]}
                    alt={cat.name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    loading="lazy"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                  <div className="text-2xl mb-1">{categoryIcons[cat.slug] || '✨'}</div>
                  <h3 className="font-semibold text-sm sm:text-base">{cat.name}</h3>
                </div>
              </button>
            ))}
          </div>
        )}
        {!loading && activeCategory && (
          <div className="text-center mt-6">
            <button
              onClick={() => setActiveCategory('')}
              className="text-sm text-primary-600 hover:text-primary-700 underline transition-colors"
            >
              ✕ Сбросить фильтр
            </button>
          </div>
        )}
        {!loading && activeCategory && (
          <div className="text-center mt-6">
            <button
              onClick={() => setActiveCategory('')}
              className="text-sm text-primary-600 hover:text-primary-700 underline transition-colors"
            >
              ✕ Сбросить фильтр
            </button>
          </div>
        )}
        <div className="text-center mt-10">
          <Link to="/services" className="btn-secondary">
            Все услуги
            <svg className="w-4 h-4 ml-2 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Popular Services */}
      <section className="bg-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="section-title">{activeCategory ? categories.find(c => c.slug === activeCategory)?.name || 'Услуги' : 'Все услуги'}</h2>
          </div>
          {loading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-48 bg-gray-200 rounded-xl mb-4" />
                  <div className="h-5 bg-gray-200 rounded w-3/4 mb-3" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : filteredServices.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">🔍</div>
              <p className="text-gray-500">Нет услуг в этой категории</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredServices.map((service, idx) => {
                const price = service.base_price ?? 0
                const duration = service.base_duration_minutes ?? 0
                const catSlug = (service.category_name || '').toLowerCase()
                return (
                  <Link
                    key={service.id}
                    to={`/services/${service.slug}`}
                    className="group bg-white rounded-2xl shadow-soft border border-gray-100/50 overflow-hidden transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1"
                    style={{ animationDelay: `${idx * 100}ms` }}
                  >
                    <div className="relative h-48 overflow-hidden bg-gradient-to-br from-primary-100 to-rose-100">
                    <img
                        src={serviceImages[service.slug] || categoryImages[catSlug] || categoryImages[service.category_name?.toLowerCase() || ''] || heroImages[0]}
                        alt={service.name}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        loading="lazy"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                      <div className="absolute top-3 right-3">
                        <span className="bg-white/90 backdrop-blur-sm text-primary-600 font-bold px-3 py-1.5 rounded-full text-sm shadow-sm">
                          {Number(price).toLocaleString('ru-RU')} ₽
                        </span>
                      </div>
                    </div>
                    <div className="p-5">
                      <h3 className="font-semibold text-gray-900 text-lg mb-2 group-hover:text-primary-600 transition-colors">
                        {service.name}
                      </h3>
                      <div className="flex items-center justify-between text-sm text-gray-400">
                        <span>{service.category_name}</span>
                        <span>{duration} мин</span>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
          <div className="text-center mt-10">
            <Link to="/services" className="btn-secondary">
              Смотреть все услуги
              <svg className="w-4 h-4 ml-2 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Masters Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div className="text-center mb-12">
          <h2 className="section-title">Наши мастера</h2>
          <p className="section-subtitle mx-auto">Профессионалы с многолетним опытом, которые заботятся о вашей красоте</p>
        </div>
        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="card text-center animate-pulse">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gray-200" />
                <div className="h-5 bg-gray-200 rounded w-3/4 mx-auto mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {masters.map((master, idx) => (
              <Link
                key={master.id}
                to={`/masters/${master.id}`}
                className="group card text-center"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden ring-4 ring-primary-100 group-hover:ring-primary-200 transition-all">
                  {master.photo ? (
                    <img src={master.photo} alt={master.full_name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary-200 to-rose-200 flex items-center justify-center text-white text-2xl font-bold">
                      {master.full_name?.[0] || '?'}
                    </div>
                  )}
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                  {master.full_name}
                </h3>
                <p className="text-sm text-gray-500 mb-2">{master.bio || 'Мастер'}</p>
                {master.rating && master.rating > 0 && (
                  <div className="flex items-center justify-center gap-1">
                    <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-600">{Number(master.rating).toFixed(1)}</span>
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Promotions */}
      {promotions.length > 0 && (
        <section className="bg-gradient-to-br from-cream-50 to-primary-50 py-16 sm:py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="section-title">Акции и спецпредложения</h2>
              <p className="section-subtitle mx-auto">Выгодные предложения для наших клиентов</p>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {promotions.slice(0, 3).map((promo, idx) => (
                <div
                  key={promo.id}
                  className="card bg-white border-l-4 border-l-primary-500"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-gray-900 text-lg">{promo.name || promo.title}</h3>
                    <span className="badge bg-primary-500 text-white text-xs">
                      -{(promo as any).discount_percent}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4 leading-relaxed">{promo.description}</p>
                  <p className="text-xs text-gray-400">
                    Действует до {new Date((promo as any).end_date || (promo as any).valid_until).toLocaleDateString('ru-RU')}
                  </p>
                </div>
              ))}
            </div>
            <div className="text-center mt-10">
              <Link to="/promotions" className="btn-secondary">
                Все акции
                <svg className="w-4 h-4 ml-2 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-500 to-rose-500 text-white py-16 sm:py-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.4%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')]" />
        </div>
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Готовы к преображению?</h2>
          <p className="text-lg text-white/90 mb-8 max-w-xl mx-auto">
            Запишитесь прямо сейчас и получите скидку 10% на первый визит
          </p>
          <Link to="/booking" className="btn-primary bg-white text-primary-600 hover:bg-cream-100 shadow-xl shadow-black/20 text-lg px-10 py-4">
            Записаться со скидкой
          </Link>
        </div>
      </section>
    </div>
  )
}
