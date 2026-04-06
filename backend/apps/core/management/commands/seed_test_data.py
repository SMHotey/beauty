import uuid
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from apps.clients.models import Client, FavoriteMaster
from apps.appointments.models import Appointment, AppointmentService
from apps.reviews.models import Review
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient
from apps.staff.models import Master, MasterService
from apps.services.models import Service, ServiceCategory


class Command(BaseCommand):
    help = 'Заполняет БД полными тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начало заполнения тестовыми данными...')

        categories = self._create_categories()
        services = self._create_services(categories)
        masters = self._create_masters(services)
        clients = self._create_clients()
        self._create_promotions(services)
        self._create_gift_certificates()
        self._create_appointments(clients, masters)
        self._create_reviews()
        self._create_favorites(clients, masters)
        self._create_blacklisted()

        self.stdout.write(self.style.SUCCESS(
            f'Готово! {ServiceCategory.objects.count()} категорий, '
            f'{Service.objects.count()} услуг, '
            f'{Master.objects.count()} мастеров, '
            f'{len(clients)} клиентов, '
            f'{Promotion.objects.count()} акций, '
            f'{GiftCertificate.objects.count()} сертификатов, '
            f'{Appointment.objects.count()} записей, '
            f'{Review.objects.count()} отзывов, '
            f'{FavoriteMaster.objects.count()} избранных, '
            f'{BlacklistedClient.objects.count()} в чёрном списке'
        ))

    def _create_categories(self):
        self.stdout.write('Создание категорий услуг...')
        cats = [
            {'name': 'Парикмахерские услуги', 'slug': 'hair', 'icon': 'scissors'},
            {'name': 'Маникюр и педикюр', 'slug': 'nails', 'icon': 'hand'},
            {'name': 'Косметология', 'slug': 'cosmetology', 'icon': 'face'},
            {'name': 'Макияж и брови', 'slug': 'makeup', 'icon': 'eye'},
            {'name': 'Массаж', 'slug': 'massage', 'icon': 'spa'},
        ]
        result = []
        for c in cats:
            cat, _ = ServiceCategory.objects.update_or_create(
                name=c['name'],
                defaults={'slug': c['slug'], 'icon': c['icon']},
            )
            result.append(cat)
        self.stdout.write(f'  Создано {len(result)} категорий')
        return result

    def _create_services(self, categories):
        self.stdout.write('Создание услуг...')
        services_data = [
            # Парикмахерские
            {'name': 'Женская стрижка', 'slug': 'womens-haircut', 'category': 0, 'price': 2500, 'duration': 60, 'desc': 'Стрижка любой сложности с мытьём головы и укладкой'},
            {'name': 'Мужская стрижка', 'slug': 'mens-haircut', 'category': 0, 'price': 1500, 'duration': 40, 'desc': 'Классическая мужская стрижка машинкой и ножницами'},
            {'name': 'Окрашивание волос', 'slug': 'hair-coloring', 'category': 0, 'price': 5000, 'duration': 120, 'desc': 'Окрашивание в один тон профессиональными красителями'},
            {'name': 'Мелирование', 'slug': 'highlights', 'category': 0, 'price': 6000, 'duration': 150, 'desc': 'Мелирование на длинные или короткие волосы'},
            {'name': 'Укладка', 'slug': 'styling', 'category': 0, 'price': 1800, 'duration': 45, 'desc': 'Вечерняя или повседневная укладка'},
            # Маникюр
            {'name': 'Маникюр классический', 'slug': 'classic-manicure', 'category': 1, 'price': 1500, 'duration': 60, 'desc': 'Классический обрезной маникюр с обработкой кутикулы'},
            {'name': 'Маникюр с покрытием', 'slug': 'gel-manicure', 'category': 1, 'price': 2500, 'duration': 90, 'desc': 'Маникюр с покрытием гель-лаком, широкая палитра цветов'},
            {'name': 'Педикюр', 'slug': 'pedicure', 'category': 1, 'price': 2800, 'duration': 90, 'desc': 'Аппаратный педикюр с покрытием'},
            # Косметология
            {'name': 'Чистка лица', 'slug': 'face-cleaning', 'category': 2, 'price': 3500, 'duration': 90, 'desc': 'Комбинированная чистка лица с ультразвуком'},
            {'name': 'Пилинг', 'slug': 'peeling', 'category': 2, 'price': 3000, 'duration': 60, 'desc': 'Химический пилинг лица для обновления кожи'},
            {'name': 'Мезотерапия', 'slug': 'mesotherapy', 'category': 2, 'price': 4500, 'duration': 60, 'desc': 'Мезотерапия лица витаминными коктейлями'},
            # Макияж
            {'name': 'Дневной макияж', 'slug': 'day-makeup', 'category': 3, 'price': 2000, 'duration': 45, 'desc': 'Лёгкий дневной макияж для повседневного образа'},
            {'name': 'Вечерний макияж', 'slug': 'evening-makeup', 'category': 3, 'price': 3000, 'duration': 60, 'desc': 'Яркий вечерний макияж для мероприятий'},
            {'name': 'Коррекция бровей', 'slug': 'eyebrow-shaping', 'category': 3, 'price': 1000, 'duration': 30, 'desc': 'Коррекция и окрашивание бровей'},
            # Массаж
            {'name': 'Массаж спины', 'slug': 'back-massage', 'category': 4, 'price': 2000, 'duration': 30, 'desc': 'Классический расслабляющий массаж спины и шеи'},
            {'name': 'Общий массаж', 'slug': 'full-massage', 'category': 4, 'price': 4000, 'duration': 60, 'desc': 'Общий расслабляющий массаж всего тела'},
        ]

        result = []
        for s in services_data:
            cat = categories[s.pop('category')]
            price = s.pop('price')
            duration = s.pop('duration')
            desc = s.pop('desc')
            svc, _ = Service.objects.get_or_create(
                slug=s['slug'],
                defaults={
                    **s,
                    'category': cat,
                    'base_price': Decimal(str(price)),
                    'base_duration_minutes': duration,
                    'description': desc,
                    'is_active': True,
                }
            )
            result.append(svc)
        self.stdout.write(f'  Создано {len(result)} услуг')
        return result

    def _create_masters(self, services):
        self.stdout.write('Создание мастеров...')

        master_configs = [
            {
                'username': 'master_anna', 'first': 'Анна', 'last': 'Иванова',
                'phone': '+79001000001', 'bio': 'Стилист-колорист с 8-летним опытом. Специализация — сложные окрашивания.',
                'services': ['womens-haircut', 'mens-haircut', 'hair-coloring', 'highlights', 'styling'],
                'hours': {'mon': {'start': '09:00', 'end': '18:00'}, 'tue': {'start': '09:00', 'end': '18:00'}, 'wed': {'start': '09:00', 'end': '18:00'}, 'thu': {'start': '09:00', 'end': '18:00'}, 'fri': {'start': '09:00', 'end': '18:00'}, 'sat': {'start': '10:00', 'end': '16:00'}},
            },
            {
                'username': 'master_elena', 'first': 'Елена', 'last': 'Смирнова',
                'phone': '+79001000002', 'bio': 'Мастер маникюра и педикюра. 5 лет опыта. Работает с премиум-материалами.',
                'services': ['classic-manicure', 'gel-manicure', 'pedicure'],
                'hours': {'mon': {'start': '10:00', 'end': '19:00'}, 'tue': {'start': '10:00', 'end': '19:00'}, 'wed': {'start': '10:00', 'end': '19:00'}, 'thu': {'start': '10:00', 'end': '19:00'}, 'fri': {'start': '10:00', 'end': '19:00'}, 'sat': {'start': '10:00', 'end': '17:00'}},
            },
            {
                'username': 'master_maria', 'first': 'Мария', 'last': 'Козлова',
                'phone': '+79001000003', 'bio': 'Косметолог-эстетист. Сертифицированный специалист по мезотерапии и пилингам.',
                'services': ['face-cleaning', 'peeling', 'mesotherapy'],
                'hours': {'mon': {'start': '09:00', 'end': '17:00'}, 'tue': {'start': '09:00', 'end': '17:00'}, 'wed': {'start': '09:00', 'end': '17:00'}, 'thu': {'start': '09:00', 'end': '17:00'}, 'fri': {'start': '09:00', 'end': '17:00'}},
            },
            {
                'username': 'master_olga', 'first': 'Ольга', 'last': 'Петрова',
                'phone': '+79001000004', 'bio': 'Визажист и бровист. Создаёт образы для фотосессий и мероприятий.',
                'services': ['day-makeup', 'evening-makeup', 'eyebrow-shaping'],
                'hours': {'mon': {'start': '10:00', 'end': '18:00'}, 'tue': {'start': '10:00', 'end': '18:00'}, 'wed': {'start': '10:00', 'end': '18:00'}, 'thu': {'start': '10:00', 'end': '18:00'}, 'fri': {'start': '10:00', 'end': '18:00'}, 'sat': {'start': '10:00', 'end': '15:00'}},
            },
            {
                'username': 'master_dmitry', 'first': 'Дмитрий', 'last': 'Волков',
                'phone': '+79001000005', 'bio': 'Массажист с медицинским образованием. 10 лет практики.',
                'services': ['back-massage', 'full-massage'],
                'hours': {'mon': {'start': '09:00', 'end': '20:00'}, 'tue': {'start': '09:00', 'end': '20:00'}, 'wed': {'start': '09:00', 'end': '20:00'}, 'thu': {'start': '09:00', 'end': '20:00'}, 'fri': {'start': '09:00', 'end': '20:00'}, 'sat': {'start': '10:00', 'end': '18:00'}},
            },
        ]

        result = []
        for cfg in master_configs:
            svc_slugs = cfg.pop('services')
            hours = cfg.pop('hours')
            phone = cfg.pop('phone')
            bio = cfg.pop('bio')

            user, _ = User.objects.get_or_create(
                username=cfg['username'],
                defaults={
                    'first_name': cfg['first'],
                    'last_name': cfg['last'],
                    'is_active': True,
                }
            )
            user.set_password('master123')
            user.save()

            master, _ = Master.objects.get_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'bio': bio,
                    'is_active': True,
                    'working_hours': hours,
                    'break_slots': [{'start': '13:00', 'end': '14:00'}],
                    'vacations': [],
                }
            )

            for slug in svc_slugs:
                svc = Service.objects.get(slug=slug)
                MasterService.objects.get_or_create(
                    master=master,
                    service=svc,
                    defaults={'is_enabled': True},
                )

            result.append(master)

        self.stdout.write(f'  Создано {len(result)} мастеров')
        return result

    def _create_clients(self):
        self.stdout.write('Создание клиентов...')

        client_data = [
            ('maria_petrova', 'Мария', 'Петрова', 'maria@example.com', '+79001111111', '1234'),
            ('alex_smirnov', 'Алексей', 'Смирнов', 'alex@example.com', '+79002222222', '1234'),
            ('elena_kozlova', 'Елена', 'Козлова', 'elena@example.com', '+79003333333', '1234'),
            ('dmitry_novikov', 'Дмитрий', 'Новиков', 'dmitry@example.com', '+79004444444', '1234'),
            ('olga_sokolova', 'Ольга', 'Соколова', 'olga@example.com', '+79005555555', '1234'),
            ('igor_mikhailov', 'Игорь', 'Михайлов', 'igor@example.com', '+79006666666', '1234'),
            ('natasha_fedorova', 'Наталья', 'Фёдорова', 'natasha@example.com', '+79007777777', '1234'),
            ('sergey_volkov', 'Сергей', 'Волков', 'sergey@example.com', '+79008888888', '1234'),
        ]

        clients = []
        for username, first, last, email, phone, password in client_data:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                    'is_active': True,
                }
            )
            user.set_password(password)
            user.save()

            client, _ = Client.objects.get_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'bonus_balance': random.choice([0, 150, 300, 500, 750]),
                    'referral_code': uuid.uuid4().hex[:12].upper(),
                }
            )
            clients.append(client)

        clients[0].referred_by = clients[4]
        clients[0].save()
        clients[2].referred_by = clients[5]
        clients[2].save()

        self.stdout.write(f'  Создано {len(clients)} клиентов')
        return clients

    def _create_promotions(self, services):
        self.stdout.write('Создание акций...')

        now = timezone.now()

        promo_data = [
            {
                'name': 'Весенняя скидка на стрижки',
                'description': 'Скидка 20% на все стрижки до конца весны',
                'discount_percent': 20,
                'promo_code': 'SPRING20',
                'start_date': date(now.year, 1, 1),
                'end_date': date(now.year, 12, 31),
                'service_slugs': ['womens-haircut', 'mens-haircut', 'styling'],
            },
            {
                'name': 'Скидка на чистку лица',
                'description': 'Специальная цена на чистку лица — скидка 25%',
                'discount_percent': 25,
                'promo_code': 'FACE25',
                'start_date': date(now.year, 1, 1),
                'end_date': date(now.year, 12, 31),
                'service_slugs': ['face-cleaning'],
            },
            {
                'name': 'Массаж со скидкой',
                'description': 'Скидка 10% на все виды массажа по будням',
                'discount_percent': 10,
                'promo_code': 'MASSAGE10',
                'start_date': date(now.year, 1, 1),
                'end_date': date(now.year, 12, 31),
                'service_slugs': ['back-massage', 'full-massage'],
            },
        ]

        for data in promo_data:
            slugs = data.pop('service_slugs')
            svcs = [s for s in services if s.slug in slugs]
            promo, created = Promotion.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if created or not promo.applicable_services.exists():
                promo.applicable_services.set(svcs)
            self.stdout.write(f'  Акция: {data["name"]}')

    def _create_gift_certificates(self):
        self.stdout.write('Создание подарочных сертификатов...')

        cert_data = [
            {'nominal': 3000, 'buyer': 'Иван Петров', 'email': 'ivan@test.ru'},
            {'nominal': 5000, 'buyer': 'Анна Сидорова', 'email': 'anna.s@test.ru'},
            {'nominal': 10000, 'buyer': 'ООО Подарки', 'email': 'office@gifts.ru'},
        ]

        for data in cert_data:
            GiftCertificate.objects.get_or_create(
                code=uuid.uuid4().hex[:12].upper(),
                defaults={
                    'nominal': data['nominal'],
                    'buyer_name': data['buyer'],
                    'recipient_email': data['email'],
                }
            )
            self.stdout.write(f'  Сертификат: {data["nominal"]} RUB для {data["email"]}')

    def _create_appointments(self, clients, masters):
        self.stdout.write('Создание записей...')

        now = timezone.now()
        today = now.date()
        count = 0

        master_services_map = {}
        for m in masters:
            ms_list = list(m.master_services.filter(is_enabled=True).select_related('service'))
            master_services_map[m.pk] = ms_list

        past_dates = [today - timedelta(days=d) for d in [30, 21, 14, 7, 3, 2, 1]]
        future_dates = [today + timedelta(days=d) for d in [1, 2, 3, 5, 7, 10, 14]]

        for dt in past_dates:
            client = random.choice(clients)
            master = random.choice(masters)
            ms_list = master_services_map.get(master.pk, [])
            if not ms_list:
                continue

            ms = random.choice(ms_list)
            svc = ms.service
            dur = ms.duration_minutes
            price = ms.price
            start_dt = timezone.make_aware(datetime.combine(dt, time(random.choice([9, 10, 11, 14, 15, 16]), 0)))
            end_dt = start_dt + timedelta(minutes=dur)

            status = random.choices(
                ['completed', 'cancelled_by_client', 'cancelled_by_admin', 'no_show'],
                weights=[70, 15, 10, 5],
                k=1,
            )[0]

            apt = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=start_dt,
                datetime_end=end_dt,
                status=status,
                comment=random.choice(['', '', '', 'Прошу не опаздывать', 'Аллергия на краску']),
            )
            AppointmentService.objects.create(
                appointment=apt,
                service=svc,
                price_at_booking=price,
                duration_at_booking=dur,
            )
            apt.total_price = price
            apt.save()
            count += 1

        for dt in future_dates:
            client = random.choice(clients)
            master = random.choice(masters)
            ms_list = master_services_map.get(master.pk, [])
            if not ms_list:
                continue

            ms = random.choice(ms_list)
            svc = ms.service
            dur = ms.duration_minutes
            price = ms.price
            start_dt = timezone.make_aware(datetime.combine(dt, time(random.choice([9, 10, 11, 14, 15, 16]), 0)))
            end_dt = start_dt + timedelta(minutes=dur)

            apt = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=start_dt,
                datetime_end=end_dt,
                status=random.choice(['pending', 'confirmed']),
                comment='',
            )
            AppointmentService.objects.create(
                appointment=apt,
                service=svc,
                price_at_booking=price,
                duration_at_booking=dur,
            )
            apt.total_price = price
            apt.save()
            count += 1

        for dt in [today]:
            for _ in range(2):
                client = random.choice(clients)
                master = random.choice(masters)
                ms_list = master_services_map.get(master.pk, [])
                if not ms_list:
                    continue

                ms = random.choice(ms_list)
                svc = ms.service
                dur = ms.duration_minutes
                price = ms.price
                start_dt = timezone.make_aware(datetime.combine(dt, time(random.choice([10, 12, 15]), 0)))
                end_dt = start_dt + timedelta(minutes=dur)

                apt = Appointment.objects.create(
                    client=client,
                    master=master,
                    datetime_start=start_dt,
                    datetime_end=end_dt,
                    status='confirmed',
                    comment='',
                )
                AppointmentService.objects.create(
                    appointment=apt,
                    service=svc,
                    price_at_booking=price,
                    duration_at_booking=dur,
                )
                apt.total_price = price
                apt.save()
                count += 1

        self.stdout.write(f'  Создано {count} записей')

    def _create_reviews(self):
        self.stdout.write('Создание отзывов...')

        completed = Appointment.objects.filter(status='completed')
        count = 0

        review_texts = [
            'Отличный мастер! Очень довольна результатом, обязательно приду ещё.',
            'Всё прошло хорошо, но пришлось немного подождать.',
            'Превосходное качество, рекомендую всем!',
            'Мастер внимательный и аккуратный. Результат превзошёл ожидания.',
            'Нормально, но есть куда расти.',
            'Замечательный сервис, приятная атмосфера.',
            'Довольна на все 100%, спасибо большое!',
            'Хорошая работа, но хотелось бы более внимательного отношения.',
        ]

        for apt in completed:
            if Review.objects.filter(appointment=apt).exists():
                continue

            Review.objects.create(
                client=apt.client,
                appointment=apt,
                rating=random.choices([3, 4, 5], weights=[10, 30, 60], k=1)[0],
                comment=random.choice(review_texts),
            )
            count += 1

        self.stdout.write(f'  Создано {count} отзывов')

    def _create_favorites(self, clients, masters):
        self.stdout.write('Создание избранных мастеров...')
        count = 0

        for client in clients[:5]:
            for master in random.sample(masters, min(2, len(masters))):
                FavoriteMaster.objects.get_or_create(client=client, master=master)
                count += 1

        self.stdout.write(f'  Создано {count} избранных')

    def _create_blacklisted(self):
        self.stdout.write('Создание чёрного списка...')

        clients = list(Client.objects.all())
        if len(clients) > 1:
            client = clients[1]
            BlacklistedClient.objects.get_or_create(
                client=client,
                defaults={'reason': 'Систематические неявки на записи без предупреждения'},
            )
            self.stdout.write('  Добавлен 1 клиент в чёрный список')
