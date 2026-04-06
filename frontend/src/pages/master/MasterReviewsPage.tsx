import { useEffect, useState } from 'react'
import api from '../../api/client'
import { handleApiError } from '../../utils/apiErrors'
import toast from 'react-hot-toast'
import { StarIcon } from '@heroicons/react/24/solid'

interface Review {
  id: number
  client_name: string
  rating: number
  comment: string
  created_at: string
  master_reply: string
  service_name: string | null
}

export default function MasterReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [replyingTo, setReplyingTo] = useState<number | null>(null)
  const [replyText, setReplyText] = useState('')
  const [canReply, setCanReply] = useState(false)

  useEffect(() => {
    Promise.all([
      api.get('/staff/master/reviews/').then((r) => r.data),
      api.get('/staff/master/profile/').then((r) => r.data),
    ])
      .then(([reviewsData, profileData]) => {
        setReviews(reviewsData)
        setCanReply(profileData.permissions?.can_reply_reviews || false)
      })
      .catch((e) => handleApiError(e, 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [])

  const handleReply = async (reviewId: number) => {
    try {
      await api.patch('/staff/master/reviews/', { review_id: reviewId, reply: replyText })
      setReviews((prev) => prev.map((r) => (r.id === reviewId ? { ...r, master_reply: replyText } : r)))
      setReplyingTo(null)
      setReplyText('')
      toast.success('Ответ сохранён')
    } catch {
      toast.error('Ошибка')
    }
  }

  if (loading) return <div className="space-y-4">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse h-32" />)}</div>

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Отзывы</h1>
        <p className="text-sm text-gray-500 mt-1">Отзывы клиентов о вашей работе</p>
      </div>

      {reviews.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-16 text-center">
          <p className="text-gray-500">Отзывов пока нет</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{review.client_name}</span>
                    <div className="flex gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <StarIcon key={i} className={`w-4 h-4 ${i < review.rating ? 'text-amber-400' : 'text-gray-200'}`} />
                      ))}
                    </div>
                  </div>
                  {review.service_name && <p className="text-xs text-gray-400">{review.service_name}</p>}
                </div>
                <span className="text-xs text-gray-400">{new Date(review.created_at).toLocaleDateString('ru-RU')}</span>
              </div>
              <p className="text-sm text-gray-700 mb-3">{review.comment}</p>

              {review.master_reply ? (
                <div className="bg-primary-50 rounded-lg p-3 border border-primary-100">
                  <p className="text-xs font-medium text-primary-700 mb-1">Ваш ответ:</p>
                  <p className="text-sm text-primary-600">{review.master_reply}</p>
                </div>
              ) : canReply ? (
                <div>
                  {replyingTo === review.id ? (
                    <div className="space-y-2">
                      <textarea
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        placeholder="Ваш ответ..."
                        className="input-field resize-none text-sm"
                        rows={2}
                      />
                      <div className="flex gap-2">
                        <button onClick={() => handleReply(review.id)} className="btn-primary text-sm py-1 px-3">Отправить</button>
                        <button onClick={() => { setReplyingTo(null); setReplyText('') }} className="btn-secondary text-sm py-1 px-3">Отмена</button>
                      </div>
                    </div>
                  ) : (
                    <button onClick={() => setReplyingTo(review.id)} className="text-sm text-primary-500 hover:underline">Ответить</button>
                  )}
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic">Ответы недоступны — обратитесь к администратору</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
