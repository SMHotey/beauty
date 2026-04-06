import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { getCategories, getServices, getAvailableMasters, createAppointment } from '../api/services'
import api from '../api/client'
import { RootState } from '../store'
import toast from 'react-hot-toast'
import { format, addDays, isSameDay } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline'

type BookingStep = 'mode' | 'repeat' | 'category' | 'service' | 'date' | 'time' | 'master' | 'phone' | 'phone_sms' | 'confirm'

interface PastAppointment {
  id: number
  master_name: string
  master_id: number
  datetime_start: string
  services: { name: string; price_at_booking: number; duration_at_booking: number }[]
  total_price: number
}

interface AvailableMaster {
  id: number
  full_name: string
  bio: string
  photo: string | null
  rating: number | null
  review_count: number
  available_slots: string[]
}

export default function BookingPage() {
  const navigate = useNavigate()
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)

  const [step, setStep] = useState<BookingStep>('mode')
  const [categories, setCategories] = useState<any[]>([])
  const [services, setServices] = useState<any[]>([])
  const [pastAppointments, setPastAppointments] = useState<PastAppointment[]>([])
  const [loading, setLoading] = useState(true)

  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [selectedService, setSelectedService] = useState<any>(null)
  const [selectedMaster, setSelectedMaster] = useState<number | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [selectedSlot, setSelectedSlot] = useState<string>('')
  const [availableMasters, setAvailableMasters] = useState<AvailableMaster[]>([])
  const [mastersLoading, setMastersLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const [guestPhone, setGuestPhone] = useState('')
  const [guestName, setGuestName] = useState('')
  const [guestSmsCode, setGuestSmsCode] = useState('')
  const [guestSmsSent, setGuestSmsSent] = useState(false)
  const [phoneLoading, setPhoneLoading] = useState(false)

  const [weekStart, setWeekStart] = useState(new Date())

  useEffect(() => {
    Promise.all([
      getCategories().catch(() => null),
      getServices({}).catch(() => null),
    ])
      .then(([catRes, svcRes]) => {
        if (catRes) setCategories(catRes.data.results || catRes.data || [])
        if (svcRes) setServices(svcRes.data.results || svcRes.data || [])
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (step === 'repeat' && isAuthenticated) {
      api.get('/appointments/appointments/my-appointments/')
        .then((res) => {
          const all = res.data.results || res.data || []
          const completed = all.filter((a: any) => a.status === 'completed')
          setPastAppointments(completed)
        })
        .catch(() => setPastAppointments([]))
    }
  }, [step, isAuthenticated])

  const handleRepeat = (apt: PastAppointment) => {
    setSelectedMaster(apt.master_id)
    const svc = services.find((s) => s.name === apt.services[0]?.name)
    if (svc) {
      setSelectedService(svc)
      setSelectedCategory(svc.category?.id || null)
    }
    setStep('date')
  }

  const handleCreate = () => {
    setSelectedCategory(null)
    setSelectedService(null)
    setSelectedMaster(null)
    setSelectedDate('')
    setSelectedSlot('')
    setWeekStart(new Date())
    setStep('category')
  }

  const handleServiceSelect = (svc: any) => {
    setSelectedService(svc)
    setSelectedDate('')
    setSelectedSlot('')
    setSelectedMaster(null)
    setWeekStart(new Date())
    setStep('date')
  }

  const handleDateSelect = (date: string) => {
    setSelectedDate(date)
    setSelectedSlot('')
    setSelectedMaster(null)
    setStep('time')
  }

  useEffect(() => {
    if (selectedService && selectedDate && step === 'time') {
      setMastersLoading(true)
      getAvailableMasters(selectedService.id, selectedDate)
        .then((res) => {
          const mastersWithSlots = (res.data.masters || []).filter(
            (m: AvailableMaster) => m.available_slots.length > 0
          )
          setAvailableMasters(mastersWithSlots)
        })
        .catch(() => setAvailableMasters([]))
        .finally(() => setMastersLoading(false))
    }
  }, [selectedService, selectedDate, step])

  const handleTimeSelect = (slot: string, masterId: number) => {
    setSelectedSlot(slot)
    setSelectedMaster(masterId)
    if (isAuthenticated) {
      setStep('confirm')
    } else {
      setGuestPhone('')
      setGuestName('')
      setGuestSmsCode('')
      setGuestSmsSent(false)
      setStep('phone')
    }
  }

  const handleSendGuestSms = async () => {
    if (!guestPhone || !guestName) {
      toast.error('Заполните имя и телефон')
      return
    }
    setPhoneLoading(true)
    try {
      await api.post('/auth/sms/send/', { phone: guestPhone })
      setGuestSmsSent(true)
      toast.success('Код подтверждения отправлен')
      setStep('phone_sms')
    } catch {
      toast.error('Ошибка отправки кода')
    } finally {
      setPhoneLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!selectedMaster || !selectedService || !selectedSlot) return
    setSubmitting(true)
    try {
      if (isAuthenticated) {
        await createAppointment({
          master_id: selectedMaster,
          service_ids: [selectedService.id],
          datetime_start: selectedSlot,
        })
      } else {
        await api.post('/appointments/guest/', {
          master_id: selectedMaster,
          service_ids: [selectedService.id],
          datetime_start: selectedSlot,
          name: guestName,
          phone: guestPhone,
        })
      }
      toast.success('Запись создана!')
      navigate(isAuthenticated ? '/profile/appointments' : '/')
    } catch {
      toast.error('Ошибка при создании записи')
    } finally {
      setSubmitting(false)
    }
  }

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + i)
    return d
  })

  const back = () => {
    const order: BookingStep[] = ['mode', 'repeat', 'category', 'service', 'date', 'time', 'master', 'phone', 'phone_sms', 'confirm']
    const idx = order.indexOf(step)
    if (idx > 0) setStep(order[idx - 1])
  }

  if (loading) return <div className="max-w-2xl mx-auto px-4 py-8"><div className="animate-pulse h-64 bg-gray-200 rounded-xl" /></div>

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {step !== 'mode' && (
        <button onClick={back} className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 transition-colors">
          <ArrowLeftIcon className="w-5 h-5" />
          <span className="text-sm font-medium">Назад</span>
        </button>
      )}

      {/* Step 0: Mode selection */}
      {step === 'mode' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Запись на услугу</h1>
          <p className="text-gray-500 mb-8">Выберите способ записи</p>
          <div className="space-y-4">
            <button
              onClick={handleCreate}
              className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-left hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                  <CheckIcon className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Создать новую запись</p>
                  <p className="text-sm text-gray-500">Выберите услугу, дату и время</p>
                </div>
              </div>
            </button>

            {isAuthenticated && pastAppointments.length > 0 && (
              <button
                onClick={() => setStep('repeat')}
                className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-left hover:border-primary-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Повторить запись</p>
                    <p className="text-sm text-gray-500">Выберите из предыдущих записей</p>
                  </div>
                </div>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Step 1: Repeat */}
      {step === 'repeat' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Повторить запись</h1>
          <p className="text-gray-500 mb-6">Выберите предыдущую запись для повторения</p>
          {pastAppointments.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Нет завершённых записей</p>
          ) : (
            <div className="space-y-3">
              {pastAppointments.map((apt) => (
                <button
                  key={apt.id}
                  onClick={() => handleRepeat(apt)}
                  className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-left hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{apt.master_name}</p>
                      <p className="text-sm text-gray-500">{apt.services.map((s) => s.name).join(', ')}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary-500">{apt.total_price} ₽</p>
                      <p className="text-xs text-gray-400">{new Date(apt.datetime_start).toLocaleDateString('ru-RU')}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 2: Category */}
      {step === 'category' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Категория услуг</h1>
          <p className="text-gray-500 mb-6">Выберите категорию</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => { setSelectedCategory(cat.id); setStep('service') }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center hover:border-primary-300 hover:shadow-md transition-all"
              >
                <div className="text-3xl mb-2">{cat.icon}</div>
                <p className="text-sm font-medium text-gray-900">{cat.name}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Service */}
      {step === 'service' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Выберите услугу</h1>
          <p className="text-gray-500 mb-6">
            {categories.find((c) => c.id === selectedCategory)?.name || 'Услуги'}
          </p>
          {(() => {
            const filtered = services.filter((s) => {
              const catId = typeof s.category === 'object' ? s.category?.id : s.category
              return catId === selectedCategory && s.is_active !== false
            })
            if (filtered.length === 0) {
              return <p className="text-gray-500 text-center py-8">В этой категории пока нет услуг</p>
            }
            return (
              <div className="space-y-3">
                {filtered.map((svc) => (
                  <button
                    key={svc.id}
                    onClick={() => handleServiceSelect(svc)}
                    className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-left hover:border-primary-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{svc.name}</p>
                        <p className="text-sm text-gray-500">{svc.base_duration_minutes} мин</p>
                      </div>
                      <p className="font-bold text-primary-500">{Number(svc.base_price).toLocaleString('ru-RU')} ₽</p>
                    </div>
                  </button>
                ))}
              </div>
            )
          })()}
        </div>
      )}

      {/* Step 4: Date */}
      {step === 'date' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Выберите дату</h1>
          <p className="text-gray-500 mb-6">{selectedService?.name}</p>
          <div className="flex items-center justify-between mb-4">
            <button onClick={() => setWeekStart((d) => addDays(d, -7))} className="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronLeftIcon className="w-5 h-5" />
            </button>
            <span className="font-medium text-gray-700">
              {format(weekDays[0], 'd MMM', { locale: ru })} — {format(weekDays[6], 'd MMMM yyyy', { locale: ru })}
            </span>
            <button onClick={() => setWeekStart((d) => addDays(d, 7))} className="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          </div>
          <div className="grid grid-cols-7 gap-2">
            {weekDays.map((day) => {
              const dateStr = format(day, 'yyyy-MM-dd')
              const isSelected = selectedDate === dateStr
              const isToday = isSameDay(day, new Date())
              return (
                <button
                  key={dateStr}
                  onClick={() => handleDateSelect(dateStr)}
                  className={`p-3 rounded-xl text-center transition-colors ${
                    isSelected
                      ? 'bg-primary-500 text-white'
                      : isToday
                      ? 'bg-primary-50 text-primary-600 border border-primary-200'
                      : 'bg-white border border-gray-200 hover:border-primary-300'
                  }`}
                >
                  <p className="text-xs font-medium">{['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][day.getDay()]}</p>
                  <p className="text-lg font-bold">{format(day, 'd')}</p>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Step 5: Time + Master combined */}
      {step === 'time' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Выберите время и мастера</h1>
          <p className="text-gray-500 mb-6">
            {selectedDate && format(new Date(selectedDate), 'd MMMM yyyy', { locale: ru })} — {selectedService?.name}
          </p>
          {mastersLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
                  <div className="flex gap-2">
                    {Array.from({ length: 4 }).map((_, j) => (
                      <div key={j} className="w-20 h-10 bg-gray-200 rounded-lg" />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : availableMasters.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Нет свободных мастеров на эту дату</p>
          ) : (
            <div className="space-y-4">
              {availableMasters.map((master) => (
                <div key={master.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-medium">
                      {master.full_name?.[0] || '?'}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{master.full_name}</p>
                      <p className="text-sm text-gray-500">{master.bio || 'Мастер'}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {master.available_slots.map((slot) => {
                      const timeStr = new Date(slot).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
                      const isSelected = selectedSlot === slot && selectedMaster === master.id
                      return (
                        <button
                          key={slot}
                          onClick={() => handleTimeSelect(slot, master.id)}
                          className={`px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                            isSelected
                              ? 'bg-primary-500 text-white'
                              : 'bg-white border border-gray-200 hover:border-primary-300 text-gray-700'
                          }`}
                        >
                          {timeStr}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 6: Guest phone */}
      {step === 'phone' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Контактные данные</h1>
          <p className="text-gray-500 mb-6">Для подтверждения записи нужен телефон</p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
              <input
                type="text"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                placeholder="Ваше имя"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input
                type="tel"
                value={guestPhone}
                onChange={(e) => setGuestPhone(e.target.value)}
                placeholder="+7 (___) ___-__-__"
                className="input-field"
                required
              />
            </div>
            <button
              onClick={handleSendGuestSms}
              disabled={phoneLoading}
              className="btn-primary w-full"
            >
              {phoneLoading ? 'Отправка...' : 'Получить код'}
            </button>
          </div>
        </div>
      )}

      {/* Step 7: Guest SMS verification */}
      {step === 'phone_sms' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Подтверждение телефона</h1>
          <p className="text-gray-500 mb-6">Код отправлен на <strong>{guestPhone}</strong></p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Код подтверждения</label>
              <input
                type="text"
                value={guestSmsCode}
                onChange={(e) => setGuestSmsCode(e.target.value)}
                placeholder="123456"
                className="input-field text-center text-2xl tracking-widest"
                maxLength={6}
                required
              />
            </div>
            <button
              onClick={() => {
                if (!guestSmsCode) {
                  toast.error('Введите код')
                  return
                }
                api.post('/auth/sms/verify/', { phone: guestPhone, sms_code: guestSmsCode })
                  .then(() => setStep('confirm'))
                  .catch(() => toast.error('Неверный код'))
              }}
              className="btn-primary w-full"
            >
              Подтвердить
            </button>
            <button
              onClick={() => setStep('phone')}
              className="w-full text-sm text-gray-500 hover:text-gray-700"
            >
              ← Изменить номер
            </button>
          </div>
        </div>
      )}

      {/* Step 8: Confirm */}
      {step === 'confirm' && (
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Подтверждение</h1>
          <p className="text-gray-500 mb-6">Проверьте данные записи</p>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-500">Услуга</span>
              <span className="font-medium text-gray-900">{selectedService?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Мастер</span>
              <span className="font-medium text-gray-900">
                {availableMasters.find((m) => m.id === selectedMaster)?.full_name || '—'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Дата</span>
              <span className="font-medium text-gray-900">{selectedDate && format(new Date(selectedDate), 'd MMMM yyyy', { locale: ru })}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Время</span>
              <span className="font-medium text-gray-900">{selectedSlot && new Date(selectedSlot).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Длительность</span>
              <span className="font-medium text-gray-900">{selectedService?.base_duration_minutes} мин</span>
            </div>
            <div className="border-t border-gray-100 pt-4 flex justify-between">
              <span className="font-semibold text-gray-900">Итого</span>
              <span className="font-bold text-primary-500 text-lg">{Number(selectedService?.base_price).toLocaleString('ru-RU')} ₽</span>
            </div>
          </div>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
          >
            {submitting ? (
              <span>Создание...</span>
            ) : (
              <>
                <CheckIcon className="w-5 h-5" />
                <span>Подтвердить запись</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
