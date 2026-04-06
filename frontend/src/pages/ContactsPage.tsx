import { MapPinIcon, PhoneIcon, ClockIcon } from '@heroicons/react/24/outline'

export default function ContactsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Контакты</h1>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Как нас найти</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <MapPinIcon className="w-6 h-6 text-primary-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Адрес</p>
                <p className="text-gray-600">г. Москва, ул. Примерная, д. 1</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <PhoneIcon className="w-6 h-6 text-primary-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Телефон</p>
                <a href="tel:+79991234567" className="text-primary-500 hover:underline">
                  +7 (999) 123-45-67
                </a>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <ClockIcon className="w-6 h-6 text-primary-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Время работы</p>
                <p className="text-gray-600">Пн–Пт: 9:00 – 21:00</p>
                <p className="text-gray-600">Сб–Вс: 10:00 – 20:00</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Мы на карте</h2>
          <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
            <p className="text-gray-400">Здесь будет карта</p>
          </div>
        </div>
      </div>
    </div>
  )
}
