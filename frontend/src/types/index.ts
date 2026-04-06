export interface Category {
  id: number
  name: string
  slug: string
  icon: string
}

export interface Service {
  id: number
  name: string
  slug: string
  base_price: number
  base_duration_minutes: number
  category: number
  category_name: string
  description?: string
  photo?: string
  is_active?: boolean
  gender_target?: string
  masters?: { id: number; full_name: string; is_active: boolean }[]
}

export interface Master {
  id: number
  full_name: string
  first_name?: string
  last_name?: string
  specialty?: string
  bio?: string
  rating: number | null
  review_count?: number
  photo: string
  is_active?: boolean
  phone?: string
  services?: { service: { id: number; name: string } }[]
}

export interface Promotion {
  id: number
  name: string
  title?: string
  description: string
  discount_percent: number
  start_date: string
  valid_until?: string
  end_date: string
  promo_code?: string
  image?: string
  is_active?: boolean
}

export interface Appointment {
  id: number
  master: Master | { id: number; name: string }
  master_name?: string
  client_name?: string
  datetime_start: string
  datetime_end: string
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled_by_client' | 'cancelled_by_master' | 'no_show'
  total_price: number
  services: { id: number; name: string; price_at_booking: number }[]
  comment?: string
}

export interface User {
  id: number
  phone: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
  bonus_balance?: number
}

export interface ApiError {
  detail?: string
  non_field_errors?: string[]
  [key: string]: unknown
}

export interface TimeSlot {
  time: string
  available: boolean
}
