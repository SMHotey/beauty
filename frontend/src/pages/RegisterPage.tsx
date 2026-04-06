import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { register } from '../store/authSlice'
import { AppDispatch } from '../store'
import toast from 'react-hot-toast'
import api from '../api/client'

export default function RegisterPage() {
  const [step, setStep] = useState<'form' | 'sms'>('form')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [referralCode, setReferralCode] = useState('')
  const [smsCode, setSmsCode] = useState('')
  const [loading, setLoading] = useState(false)
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()

  const handleSendSms = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== passwordConfirm) {
      toast.error('Пароли не совпадают')
      return
    }
    setLoading(true)
    try {
      await api.post('/auth/sms/send/', { phone })
      toast.success('Код подтверждения отправлен')
      setStep('sms')
    } catch {
      toast.error('Ошибка отправки кода')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!smsCode) {
      toast.error('Введите код подтверждения')
      return
    }
    setLoading(true)
    try {
      await dispatch(register({
        phone,
        password,
        sms_code: smsCode,
        first_name: firstName,
        last_name: lastName,
        referral_code: referralCode || undefined,
      })).unwrap()
      toast.success('Регистрация успешна!')
      navigate('/profile')
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : 'Ошибка при регистрации'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          {step === 'form' ? 'Регистрация' : 'Подтверждение телефона'}
        </h1>

        {step === 'form' && (
          <form onSubmit={handleSendSms} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Имя"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Фамилия"
                  className="input-field"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+7 (___) ___-__-__"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Минимум 6 символов"
                className="input-field"
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Подтвердите пароль</label>
              <input
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                placeholder="Повторите пароль"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Реферальный код <span className="text-gray-400">(необязательно)</span>
              </label>
              <input
                type="text"
                value={referralCode}
                onChange={(e) => setReferralCode(e.target.value)}
                placeholder="Код"
                className="input-field"
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Отправка кода...' : 'Получить код'}
            </button>
          </form>
        )}

        {step === 'sms' && (
          <form onSubmit={handleRegister} className="space-y-4">
            <p className="text-sm text-gray-600 text-center">
              Код отправлен на <strong>{phone}</strong>
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Код подтверждения</label>
              <input
                type="text"
                value={smsCode}
                onChange={(e) => setSmsCode(e.target.value)}
                placeholder="123456"
                className="input-field text-center text-2xl tracking-widest"
                maxLength={6}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
            <button
              type="button"
              onClick={() => setStep('form')}
              className="w-full text-sm text-gray-500 hover:text-gray-700"
            >
              ← Изменить номер телефона
            </button>
          </form>
        )}

        <p className="text-center text-sm text-gray-500 mt-4">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-primary-500 hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
