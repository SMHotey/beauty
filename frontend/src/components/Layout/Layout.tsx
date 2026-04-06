import { Outlet } from 'react-router-dom'
import Header from './Header'
import MobileNav from './MobileNav'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 pb-20 md:pb-8">
        <Outlet />
      </main>
      <MobileNav />
    </div>
  )
}
