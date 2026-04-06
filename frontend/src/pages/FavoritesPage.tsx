import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getFavorites, removeFavorite } from '../api/services'
import { SkeletonCard } from '../components/UI/Skeleton'
import toast from 'react-hot-toast'
import StarRating from '../components/UI/StarRating'
import { handleApiError } from '../utils/apiErrors'

interface FavoriteMaster {
  id: number
  master_id: number
  master_name: string
  master_photo: string
  master_bio: string
  master_rating: number
}

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteMaster[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getFavorites()
      .then((res) => setFavorites(res.data.results || res.data))
      .catch((e) => handleApiError(e, 'Ошибка загрузки избранного'))
      .finally(() => setLoading(false))
  }, [])

  const handleRemove = async (id: number) => {
    try {
      await removeFavorite(id)
      setFavorites((prev) => prev.filter((f) => f.id !== id))
      toast.success('Удалено из избранного')
    } catch {
      toast.error('Ошибка')
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Избранные мастера</h1>

      {loading ? (
        <div className="grid sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : favorites.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">Список избранного пуст</p>
          <Link to="/masters" className="text-primary-500 hover:underline mt-2 inline-block">
            Посмотреть мастеров
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {favorites.map((fav) => (
            <div key={fav.id} className="card flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gray-200 overflow-hidden flex-shrink-0">
                {fav.master_photo ? (
                  <img src={fav.master_photo} alt={fav.master_name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 font-medium">
                    {fav.master_name?.[0] || '?'}
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <Link to={`/masters/${fav.master_id}`} className="font-semibold text-gray-900 hover:text-primary-500 transition-colors">
                  {fav.master_name}
                </Link>
                <p className="text-sm text-gray-500">{fav.master_bio || 'Мастер'}</p>
                <StarRating rating={fav.master_rating} size="sm" />
              </div>
              <button
                onClick={() => handleRemove(fav.id)}
                className="text-sm text-red-500 hover:text-red-600 font-medium flex-shrink-0"
              >
                Удалить
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
