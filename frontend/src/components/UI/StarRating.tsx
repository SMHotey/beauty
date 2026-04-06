import { StarIcon as StarSolid } from '@heroicons/react/24/solid'
import { StarIcon as StarOutline } from '@heroicons/react/24/outline'

interface StarRatingProps {
  rating: number
  onRate?: (rating: number) => void
  size?: 'sm' | 'md' | 'lg'
}

export default function StarRating({ rating, onRate, size = 'md' }: StarRatingProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-7 h-7',
  }

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={!onRate}
          onClick={() => onRate?.(star)}
          className={`${onRate ? 'cursor-pointer hover:scale-110' : 'cursor-default'} transition-transform`}
        >
          {star <= rating ? (
            <StarSolid className={`${sizeClasses[size]} text-yellow-400`} />
          ) : (
            <StarOutline className={`${sizeClasses[size]} text-gray-300`} />
          )}
        </button>
      ))}
    </div>
  )
}
