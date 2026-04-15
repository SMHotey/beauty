import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { store } from './store'
import { fetchProfile } from './store/authSlice'
import Layout from './components/Layout/Layout'
import HomePage from './pages/HomePage'
import ServicesPage from './pages/ServicesPage'
import ServiceDetailPage from './pages/ServiceDetailPage'
import MasterPage from './pages/MasterPage'
import BookingPage from './pages/BookingPage'
import PromotionsPage from './pages/PromotionsPage'
import ContactsPage from './pages/ContactsPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import AppointmentsPage from './pages/AppointmentsPage'
import FavoritesPage from './pages/FavoritesPage'
import AdminLayout from './components/AdminLayout'
import AdminDashboardPage from './pages/admin/DashboardPage'
import AdminMastersPage from './pages/admin/MastersPage'
import AdminCalendarPage from './pages/admin/CalendarPage'
import AdminAppointmentsPage from './pages/admin/AppointmentsPage'
import AdminServicesPage from './pages/admin/ServicesPage'
import AdminPromotionsPage from './pages/admin/PromotionsPage'
import AdminBlacklistPage from './pages/admin/BlacklistPage'
import AdminReportsPage from './pages/admin/ReportsPage'
import MasterProfilePage from './pages/admin/MasterProfilePage'
import ClientProfilePage from './pages/admin/ClientProfilePage'
import MasterLayout from './components/MasterLayout'
import MasterDashboardPage from './pages/master/MasterDashboardPage'
import MasterAppointmentsPage from './pages/master/MasterAppointmentsPage'
import MasterReviewsPage from './pages/master/MasterReviewsPage'
import MasterSchedulePage from './pages/master/MasterSchedulePage'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import MasterRoute from './components/MasterRoute'

/**
 * Основной компонент приложения.
 * Описывает роутинг и точку входа для всех основных страниц.
 * 
 * Роутинг:
 *  - ОбщеДоступные маршруты: /, /services, /masters, /booking, /promotions, /contacts, /login, /register
 *  - Защищенные маршруты для авторизованных пользователей: /profile, /profile/appointments, /profile/favorites
 *  - Админские маршруты (только для персонала с is_staff=True): /admin/*
 *  - Маршруты для мастеров: /master/*
 * 
 * Используются специальные компоненты-обертки:
 *  - <ProtectedRoute> — проверка авторизации
 *  - <AdminRoute> — проверка прав администратора
 *  - <MasterRoute> — проверка прав мастера
 */
export default function App() {
  useEffect(() => {
    store.dispatch(fetchProfile() as any)
  }, [])

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="services/:slug" element={<ServiceDetailPage />} />
        <Route path="masters" element={<HomePage />} />
        <Route path="masters/:id" element={<MasterPage />} />
        <Route path="booking" element={<BookingPage />} />
        <Route path="promotions" element={<PromotionsPage />} />
        <Route path="contacts" element={<ContactsPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>

      {/* Защищенные маршруты, доступные только авторизованным пользователям */}
      <Route path="profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="profile/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
      <Route path="profile/favorites" element={<ProtectedRoute><FavoritesPage /></ProtectedRoute>} />

      {/* Админские маршруты, доступные только пользователям с правами администратора */}
      <Route path="admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
        <Route index element={<AdminDashboardPage />} />
        <Route path="appointments" element={<AdminAppointmentsPage />} />
        <Route path="calendar" element={<AdminCalendarPage />} />
        <Route path="masters" element={<AdminMastersPage />} />
        <Route path="masters/:id" element={<MasterProfilePage />} />
        <Route path="services" element={<AdminServicesPage />} />
        <Route path="promotions" element={<AdminPromotionsPage />} />
        <Route path="reports" element={<AdminReportsPage />} />
        <Route path="blacklist" element={<AdminBlacklistPage />} />
        <Route path="clients/:id" element={<ClientProfilePage />} />
      </Route>

      {/* Маршруты для мастеров, доступные только проверенным мастерам */}
      <Route path="master" element={<MasterRoute><MasterLayout /></MasterRoute>}>
        <Route index element={<MasterDashboardPage />} />
        <Route path="appointments" element={<MasterAppointmentsPage />} />
        <Route path="reviews" element={<MasterReviewsPage />} />
        <Route path="schedule" element={<MasterSchedulePage />} />
      </Route>
    </Routes>
  )
}
