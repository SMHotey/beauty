import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getMaster, getReviews, createReview } from '../api/services'
import { addFavorite, removeFavorite } from '../api/services'
import StarRating from '../components/UI/StarRating'
import { SkeletonText } from '../components/UI/Skeleton'
import { useSelector } from 'react-redux'
import { RootState } from '../store'
import toast from 'react-hot-toast'
import { HeartIcon as HeartOutline } from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolid } from '@heroicons/react/24/solid'
import { handleApiError } from '../utils/apiErrors'

interface MasterDetail {
  id: number
  full_name: string
  bio: string
  rating: number
  review_count: number
  photo: string
  services?: { id: number; service_name: string; price: string; duration_minutes: number }[]
}

interface Review {
  id: number
  client_name: string
  rating: number
  text: string
  created_at: string
}

export default function MasterPage() {
  const { id } = useParams<{ id: string }>()
  const [master, setMaster] = useState<MasterDetail | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [isFavorite, setIsFavorite] = useState(false)
  const [newReview, setNewReview] = useState({ rating: 5, text: '' })
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated)

  useEffect(() => {
    if (!id) return
    Promise.all([getMaster(Number(id)), getReviews({ master: id })])
      .then(([masterRes, reviewsRes]) => {
        setMaster(masterRes.data)
        setReviews(reviewsRes.data.results || reviewsRes.data)
      })
      .catch((e) => handleApiError(e, 'Ошибка загрузки мастера'))
      .finally(() => setLoading(false))
  }, [id])

  const handleFavorite = async () => {
    if (!isAuthenticated || !master) return
    try {
      if (isFavorite) {
        await removeFavorite(master.id)
        toast.success('Удалено из избранного')
      } else {
        await addFavorite(master.id)
        toast.success('Добавлено в избранное')
      }
      setIsFavorite(!isFavorite)
    } catch {
      toast.error('Ошибка')
    }
  }

  const handleSubmitReview = async () => {
    if (!id || !newReview.text.trim()) return
    try {
      await createReview({ master: Number(id), rating: newReview.rating, text: newReview.text })
      toast.success('Отзыв отправлен')
      setNewReview({ rating: 5, text: '' })
      const res = await getReviews({ master: id })
      setReviews(res.data.results || res.data)
    } catch {
      toast.error('Ошибка при отправке отзыва')
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SkeletonText lines={8} />
      </div>
    )
  }

  if (!master) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500 text-lg">Мастер не найден</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="card mb-8">
        <div className="flex items-start gap-6">
          <div className="w-24 h-24 rounded-full bg-gray-200 overflow-hidden flex-shrink-0">
            {master.photo ? (
              <img src={master.photo} alt={master.full_name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400 text-3xl">
                {master.full_name?.[0] || '?'}
              </div>
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {master.full_name}
                </h1>
              </div>
              {isAuthenticated && (
                <button onClick={handleFavorite} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                  {isFavorite ? (
                    <HeartSolid className="w-6 h-6 text-red-500" />
                  ) : (
                    <HeartOutline className="w-6 h-6 text-gray-400" />
                  )}
                </button>
              )}
            </div>
            <div className="flex items-center gap-4 mt-3">
              <StarRating rating={master.rating} size="sm" />
              <span className="text-sm text-gray-500">
                {master.rating} ({master.review_count} отзывов)
              </span>
            </div>
            {master.bio && <p className="text-gray-600 mt-3">{master.bio}</p>}
            <Link
              to={`/booking?master=${master.id}`}
              className="btn-primary mt-4 inline-block"
            >
              Записаться
            </Link>
          </div>
        </div>
      </div>

      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Отзывы</h2>
        {isAuthenticated && (
          <div className="card mb-6">
            <h3 className="font-medium text-gray-900 mb-3">Оставить отзыв</h3>
            <div className="mb-3">
              <StarRating rating={newReview.rating} onRate={(r) => setNewReview({ ...newReview, rating: r })} size="lg" />
            </div>
            <textarea
              value={newReview.text}
              onChange={(e) => setNewReview({ ...newReview, text: e.target.value })}
              placeholder="Расскажите о вашем опыте..."
              className="input-field mb-3 resize-none"
              rows={3}
            />
            <button onClick={handleSubmitReview} className="btn-primary" disabled={!newReview.text.trim()}>
              Отправить
            </button>
          </div>
        )}

        {reviews.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Отзывов пока нет</p>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div key={review.id} className="card">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{review.client_name}</span>
                  <span className="text-sm text-gray-400">
                    {new Date(review.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
                <StarRating rating={review.rating} size="sm" />
                {review.text && <p className="text-gray-600 mt-2 text-sm">{review.text}</p>}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
