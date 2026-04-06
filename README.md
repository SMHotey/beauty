# Beauty Salon MVP — Салон красоты

Полнофункциональный MVP веб-сайта для салона красоты с онлайн-записью, системой лояльности, админ-панелью и PWA.

## Технологический стек

**Бэкенд:**
- Django 4.2+ / Django REST Framework
- PostgreSQL (dev: SQLite)
- Redis (кэш, Celery broker)
- Celery (отложенные задачи, напоминания)
- JWT авторизация (djangorestframework-simplejwt)
- drf-spectacular (OpenAPI / Swagger)

**Фронтенд:**
- React 18 + TypeScript + Vite
- Tailwind CSS + Headless UI
- Redux Toolkit (аутентификация, корзина записи)
- React Router 6
- PWA (Service Worker, manifest.json)

## Структура проекта

```
├── backend/                 # Django бэкенд
│   ├── beauty_backend/      # Настройки проекта
│   ├── apps/                # Приложения
│   │   ├── core/            # Базовые модели
│   │   ├── services/        # Услуги и категории
│   │   ├── staff/           # Мастера
│   │   ├── clients/         # Клиенты, избранное
│   │   ├── appointments/    # Записи, слоты
│   │   ├── reviews/         # Отзывы
│   │   ├── promotions/      # Акции, сертификаты, чёрный список
│   │   ├── auth_app/        # Авторизация, SMS
│   │   └── admin_panel/     # Админ API
│   ├── fixtures/            # Начальные данные
│   └── requirements/        # Зависимости Python
├── frontend/                # React фронтенд
│   ├── src/
│   │   ├── api/             # API клиент + сервисы
│   │   ├── components/      # UI компоненты
│   │   ├── pages/           # Страницы
│   │   ├── store/           # Redux slices
│   │   └── App.tsx
│   └── public/              # PWA ассеты
├── nginx/                   # Nginx конфигурация
├── docker-compose.yml
└── README.md
```

## Быстрый старт (Docker)

### 1. Клонирование и подготовка

```bash
cd Beauty
cp backend/.env.example backend/.env
```

### 2. Запуск всех сервисов

```bash
docker-compose up --build
```

Это запустит:
- **PostgreSQL** (порт 5432)
- **Redis** (порт 6379)
- **Django backend** (порт 8000)
- **Celery worker** (напоминания)
- **Celery beat** (расписание задач)
- **React frontend** (порт 5173)
- **Nginx** (порт 80)

### 3. Открыть приложение

- Фронтенд: http://localhost:5173
- API Swagger: http://localhost:8000/api/docs/swagger/
- API ReDoc: http://localhost:8000/api/docs/redoc/
- Django Admin: http://localhost:8000/admin/

### 4. Данные для входа

**Администратор:**
- Email/логин: `admin@example.com`
- Пароль: `admin123`

**Мастера (из фикстур):**
- Телефон: `+79001234567` (Стилист)
- Телефон: `+79007654321` (Косметолог)

## Локальная разработка (без Docker)

### Бэкенд

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements/dev.txt

# Миграции
python manage.py migrate

# Загрузка начальных данных
python manage.py loaddata fixtures/initial_data.json

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver

# Celery worker (в отдельном терминале)
celery -A beauty_backend worker -l info

# Celery beat (в отдельном терминале)
celery -A beauty_backend beat -l info
```

### Фронтенд

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка для продакшена
npm run build
```

## Миграции БД

```bash
# Создание миграций после изменений моделей
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Сброс и повторное применение (dev)
python manage.py migrate --run-syncdb
python manage.py loaddata fixtures/initial_data.json
```

## Тесты

```bash
cd backend

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=apps

# Запуск конкретного приложения
pytest apps/appointments/tests.py -v
```

## API документация

После запуска сервера Swagger UI доступен по адресу:
- **Swagger UI:** http://localhost:8000/api/docs/swagger/
- **ReDoc:** http://localhost:8000/api/docs/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Основные эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/services/services/` | Список услуг (фильтрация, пагинация) |
| GET | `/api/v1/services/service-categories/` | Категории услуг |
| GET | `/api/v1/staff/masters/` | Список мастеров |
| GET | `/api/v1/staff/masters/{id}/slots/?date=YYYY-MM-DD&service_ids=1,2` | Свободные слоты мастера |
| POST | `/api/v1/appointments/guest/` | Запись без регистрации |
| POST | `/api/v1/auth/register/` | Регистрация по телефону |
| POST | `/api/v1/auth/login/` | Вход (JWT) |
| POST | `/api/v1/auth/sms/send/` | Отправка SMS-кода |
| GET | `/api/v1/promotions/promotions/` | Активные акции |
| GET | `/api/v1/admin-panel/dashboard/stats/` | Статистика (админ) |
| GET | `/api/v1/admin-panel/calendar/` | Календарь записей (админ) |
| GET | `/api/v1/admin-panel/reports/sales/?format=xlsx` | Экспорт продаж в Excel |

## Фикстуры

Начальные данные загружаются автоматически при запуске через Docker. Включают:

- **5 категорий услуг:** Парикмахерские, Ногтевой сервис, Косметология, Визаж, Массаж
- **15+ услуг:** стрижки, маникюр, педикюр, чистка лица, макияж, массаж и др.
- **2 мастера** с расписанием и назначенными услугами
- **5 глобальных настроек** (буфер, отмена, бонусы, рефералы)

## Система лояльности

- **Бонусы:** 5% от суммы завершённой записи начисляется на бонусный баланс
- **Списание:** до 30% от суммы чека бонусами при следующей записи
- **Рефералы:** +500 бонусов пригласителю после первой записи приглашённого

## Алгоритм генерации слотов

Функция `get_available_slots(master_id, date, service_ids)`:
1. Получает рабочие часы мастера на указанный день недели
2. Учитывает перерывы и отпуска
3. Суммирует длительность выбранных услуг + буфер (10 мин)
4. Генерирует слоты с шагом 30 минут
5. Исключает пересекающиеся с существующими записями

## Celery задачи

| Задача | Расписание | Описание |
|--------|-----------|----------|
| `send_reminders` | Каждый час | Напоминания о записях за 24 часа |
| `send_bulk_sms` | По запросу | Массовая SMS-рассылка |

## PWA

Приложение поддерживает установку на мобильные устройства:
- `manifest.json` с иконками и метаданными
- Service Worker для офлайн-кэширования
- Адаптивный дизайн (mobile-first)

## Переключение на PostgreSQL

В `backend/.env`:

```env
DATABASE_URL=postgres://user:password@localhost:5432/beauty_db
```

В `docker-compose.yml` уже настроена PostgreSQL.

## Pre-commit хуки

```bash
cd backend
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Хуки: black (форматирование), isort (сортировка импортов), flake8 (линтер).

## Лицензия

MIT
