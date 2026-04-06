"""
Management command to populate the database with comprehensive test data.
Usage: python manage.py populate_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
import random
from django.db import models


class Command(BaseCommand):
    help = 'Populate database with test data (users, schedules, appointments, reviews, promotions)'

    def handle(self, *args, **options):
        self.stdout.write('Populating test data...')
        self._create_users()
        self._create_schedules()
        self._create_appointments()
        self._create_reviews()
        self._create_promotions()
        self.stdout.write(self.style.SUCCESS('Test data populated successfully!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write('  Admin:    admin@example.com / admin123')
        self.stdout.write('  Master 1: +79001234567 / master123')
        self.stdout.write('  Master 2: +79007654321 / master123')
        self.stdout.write('  Master 3: +79005554433 / master123')
        self.stdout.write('  Client:   +79009998877 / client123')

    def _create_users(self):
        from apps.clients.models import Client
        from apps.staff.models import Master

        # Admin user
        admin, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@example.com',
            'first_name': 'Админ',
            'last_name': 'Главный',
            'is_superuser': True,
            'is_staff': True,
        })
        admin.set_password('admin123')
        admin.save()
        self.stdout.write('  [OK] Admin ready (admin@example.com / admin123)')

        # Master 1
        u1, _ = User.objects.get_or_create(username='+79001234567', defaults={
            'email': 'anna@beauty.ru',
            'first_name': 'Анна',
            'last_name': 'Иванова',
        })
        u1.set_password('master123')
        u1.save()
        master1, _ = Master.objects.get_or_create(phone='+79001234567', defaults={
            'user': u1,
            'bio': 'Стилист-колорист с 10-летним опытом. Специализация — сложные окрашивания.',
            'is_active': True,
            'working_hours': {
                '0': [{'start': '09:00', 'end': '18:00'}],
                '1': [{'start': '09:00', 'end': '18:00'}],
                '2': [{'start': '09:00', 'end': '18:00'}],
                '3': [{'start': '09:00', 'end': '18:00'}],
                '4': [{'start': '09:00', 'end': '18:00'}],
                '5': [{'start': '10:00', 'end': '16:00'}],
                '6': None,
            },
            'break_slots': [{'start': '13:00', 'end': '14:00', 'weekday': i} for i in range(5)],
            'vacations': [],
        })
        if master1.user != u1:
            master1.user = u1
            master1.save()
        self.stdout.write(f'  [OK] Master 1 ready: {master1} (+79001234567 / master123)')

        # Master 2
        u2, _ = User.objects.get_or_create(username='+79007654321', defaults={
            'email': 'petr@beauty.ru',
            'first_name': 'Петр',
            'last_name': 'Сидоров',
        })
        u2.set_password('master123')
        u2.save()
        master2, _ = Master.objects.get_or_create(phone='+79007654321', defaults={
            'user': u2,
            'bio': 'Косметолог-дерматолог. Эксперт по уходу за кожей лица.',
            'is_active': True,
            'working_hours': {
                '0': [{'start': '10:00', 'end': '19:00'}],
                '1': [{'start': '10:00', 'end': '19:00'}],
                '2': [{'start': '10:00', 'end': '19:00'}],
                '3': [{'start': '10:00', 'end': '19:00'}],
                '4': [{'start': '10:00', 'end': '19:00'}],
                '5': None,
                '6': None,
            },
            'break_slots': [{'start': '14:00', 'end': '15:00', 'weekday': i} for i in range(5)],
            'vacations': [],
        })
        if master2.user != u2:
            master2.user = u2
            master2.save()
        self.stdout.write(f'  [OK] Master 2 ready: {master2} (+79007654321 / master123)')

        # Master 3
        u3, _ = User.objects.get_or_create(username='+79005554433', defaults={
            'email': 'maria@beauty.ru',
            'first_name': 'Мария',
            'last_name': 'Козлова',
        })
        u3.set_password('master123')
        u3.save()
        master3, created = Master.objects.get_or_create(phone='+79005554433', defaults={
            'user': u3,
            'bio': 'Мастер маникюра и педикюра. 7 лет опыта.',
            'is_active': True,
            'working_hours': {
                '0': [{'start': '09:00', 'end': '18:00'}],
                '1': [{'start': '09:00', 'end': '18:00'}],
                '2': [{'start': '09:00', 'end': '18:00'}],
                '3': [{'start': '09:00', 'end': '18:00'}],
                '4': [{'start': '09:00', 'end': '17:00'}],
                '5': [{'start': '10:00', 'end': '15:00'}],
                '6': None,
            },
            'break_slots': [{'start': '12:00', 'end': '13:00', 'weekday': i} for i in range(5)],
            'vacations': [],
        })
        if created or master3.user != u3:
            master3.user = u3
            master3.save()
        self.stdout.write(f'  [OK] Master 3 ready: {master3} (+79005554433 / master123)')

        # Client 1
        uc, _ = User.objects.get_or_create(username='+79009998877', defaults={
            'email': 'client@test.ru',
            'first_name': 'Елена',
            'last_name': 'Смирнова',
        })
        uc.set_password('client123')
        uc.save()
        client1, created = Client.objects.get_or_create(phone='+79009998877', defaults={
            'user': uc,
            'bonus_balance': 350.00,
        })
        if not created and client1.user != uc:
            client1.user = uc
            client1.save()
        self.stdout.write(f'  [OK] Client 1 ready: {client1} (+79009998877 / client123)')

        # Client 2
        uc2, _ = User.objects.get_or_create(username='+79008887766', defaults={
            'email': 'client2@test.ru',
            'first_name': 'Ольга',
            'last_name': 'Петрова',
        })
        uc2.set_password('client123')
        uc2.save()
        client2, created = Client.objects.get_or_create(phone='+79008887766', defaults={
            'user': uc2,
            'bonus_balance': 120.00,
        })
        if not created and client2.user != uc2:
            client2.user = uc2
            client2.save()
        self.stdout.write(f'  [OK] Client 2 ready: {client2} (+79008887766 / client123)')

    def _create_schedules(self):
        from apps.staff.models import Master, MasterSchedule

        masters = Master.objects.filter(is_active=True)
        today = date.today()

        for master in masters:
            existing = MasterSchedule.objects.filter(master=master).count()
            if existing >= 30:
                self.stdout.write(f'  ⏭ Schedule exists for {master} ({existing} entries)')
                continue

            # Clear old schedules
            MasterSchedule.objects.filter(master=master).delete()

            schedules = []
            for i in range(60):
                d = today + timedelta(days=i)
                weekday = d.weekday()
                hours = master.working_hours.get(str(weekday))
                if hours:
                    for slot in hours:
                        schedules.append(MasterSchedule(
                            master=master,
                            date=d,
                            start_time=slot['start'],
                            end_time=slot['end'],
                            is_working=True,
                        ))
                else:
                    schedules.append(MasterSchedule(
                        master=master,
                        date=d,
                        start_time='09:00',
                        end_time='09:00',
                        is_working=False,
                    ))

            MasterSchedule.objects.bulk_create(schedules)
            self.stdout.write(f'  ✓ Schedule created for {master} ({len(schedules)} entries)')

    def _create_appointments(self):
        from apps.appointments.models import Appointment, AppointmentService
        from apps.staff.models import Master, MasterService
        from apps.clients.models import Client
        from apps.services.models import Service

        if Appointment.objects.count() > 10:
            self.stdout.write('  ⏭ Appointments already exist, skipping')
            return

        masters = list(Master.objects.filter(is_active=True))
        clients = list(Client.objects.all())
        now = timezone.now()

        # Past completed
        for i in range(8):
            days_ago = random.randint(3, 30)
            dt = now - timedelta(days=days_ago, hours=random.randint(1, 10))
            master = random.choice(masters)
            client = random.choice(clients)
            services = list(Service.objects.filter(is_active=True)[:2])
            if not services:
                continue

            appt = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=dt,
                datetime_end=dt + timedelta(minutes=60),
                status='completed',
            )
            for svc in services:
                AppointmentService.objects.create(
                    appointment=appt,
                    service=svc,
                    price_at_booking=svc.base_price,
                    duration_at_booking=svc.base_duration_minutes,
                )
            appt.total_price = appt.services.aggregate(
                s=models.Sum('price_at_booking')
            )['s'] or 0
            appt.save(update_fields=['total_price'])

        # Future confirmed
        for i in range(4):
            days_ahead = random.randint(1, 7)
            dt = now + timedelta(days=days_ahead, hours=random.randint(2, 8))
            master = random.choice(masters)
            client = random.choice(clients)
            services = list(Service.objects.filter(is_active=True)[:1])
            if not services:
                continue

            appt = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=dt,
                datetime_end=dt + timedelta(minutes=60),
                status='confirmed',
            )
            for svc in services:
                AppointmentService.objects.create(
                    appointment=appt,
                    service=svc,
                    price_at_booking=svc.base_price,
                    duration_at_booking=svc.base_duration_minutes,
                )
            appt.total_price = appt.services.aggregate(
                s=models.Sum('price_at_booking')
            )['s'] or 0
            appt.save(update_fields=['total_price'])

        self.stdout.write(f'  ✓ {Appointment.objects.count()} appointments created')

    def _create_reviews(self):
        from apps.appointments.models import Appointment
        from apps.reviews.models import Review

        if Review.objects.count() > 3:
            self.stdout.write('  ⏭ Reviews already exist, skipping')
            return

        completed = Appointment.objects.filter(status='completed').select_related('client', 'master')
        texts = [
            'Отличная работа! Очень довольна результатом.',
            'Профессиональный подход, рекомендую!',
            'Прекрасный мастер, обязательно вернусь.',
            'Всё прошло замечательно, спасибо!',
            'Качественная услуга, приятная атмосфера.',
        ]

        for i, appt in enumerate(completed[:5]):
            Review.objects.create(
                appointment=appt,
                client=appt.client,
                rating=random.choice([4, 5, 5, 5, 4]),
                comment=texts[i % len(texts)],
            )

        self.stdout.write(f'  ✓ {Review.objects.count()} reviews created')

    def _create_promotions(self):
        from apps.promotions.models import Promotion, GiftCertificate
        from apps.services.models import Service

        if Promotion.objects.count() > 2:
            self.stdout.write('  ⏭ Promotions already exist, skipping')
            return

        now = timezone.now()
        services = list(Service.objects.filter(is_active=True)[:3])

        p1 = Promotion.objects.create(
            name='Скидка 20% на первое посещение',
            description='Получите скидку 20% на любую услугу при первом визите в наш салон. Акция действует для новых клиентов.',
            discount_percent=20,
            start_date=now - timedelta(days=10),
            end_date=now + timedelta(days=30),
        )
        p1.applicable_services.set(services)

        Promotion.objects.create(
            name='Весеннее обновление',
            description='Скидка 15% на все услуги парикмахерского отделения. Обновите свой образ к весне!',
            discount_percent=15,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=25),
        )

        if GiftCertificate.objects.count() == 0:
            GiftCertificate.objects.create(nominal=5000, buyer_name='Салон Beauty', recipient_email='gift@beauty.ru')
            GiftCertificate.objects.create(nominal=10000, buyer_name='Салон Beauty', recipient_email='gift@beauty.ru')

        self.stdout.write(f'  ✓ {Promotion.objects.count()} promotions created')
