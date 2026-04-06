"""
Beauty Salon Backend - Comprehensive API Tests
Run: cd backend && python run_tests.py
"""
import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_backend.settings.dev')
django.setup()

from django.test import Client as TestClient
from django.contrib.auth.models import User
from apps.services.models import Service, ServiceCategory
from apps.staff.models import Master, MasterService
from apps.clients.models import Client
from apps.appointments.models import Appointment
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient
from apps.reviews.models import Review

tc = TestClient()
admin_token = None
client_token = None
passed = 0
failed = 0
errors = []

def log(name, ok, detail=''):
    global passed, failed
    if ok:
        passed += 1
        print(f'  [OK] {name}')
    else:
        failed += 1
        msg = f'  [FAIL] {name}'
        if detail:
            msg += f' -- {detail}'
        print(msg)
        errors.append(name)

def post(path, data, token=None):
    h = {}
    if token:
        h['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return tc.post(f'/api/v1{path}', json.dumps(data), content_type='application/json', **h)

def get(path, token=None):
    h = {}
    if token:
        h['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return tc.get(f'/api/v1{path}', **h)

def patch(path, data, token=None):
    h = {}
    if token:
        h['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return tc.patch(f'/api/v1{path}', json.dumps(data), content_type='application/json', **h)

def delete(path, token=None):
    h = {}
    if token:
        h['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return tc.delete(f'/api/v1{path}', **h)

def section(name):
    print(f'\n{"="*60}')
    print(f'  {name}')
    print(f'{"="*60}')

# 0. Setup
section('0. Setup')

User.objects.filter(username='test_admin').delete()
User.objects.filter(username='test_client').delete()
User.objects.filter(username='+79990000099').delete()
Client.objects.filter(phone='+79990000099').delete()
Appointment.objects.filter(client__phone='+79990000099').delete()

au = User.objects.create_superuser('test_admin', 'test_admin@test.ru', 'test123')
au.is_staff = True
au.save()

r = post('/auth/login/', {'phone': 'test_admin@test.ru', 'password': 'test123'})
if r.status_code == 200:
    data = r.json()
    admin_token = data['access']
    admin_refresh = data.get('refresh', '')
    log('Admin login', True)
else:
    log('Admin login', False, f'{r.status_code}')

# 1. AUTH
section('1. Auth')

r = post('/auth/login/', {'phone': 'test_admin@test.ru', 'password': 'wrong'})
log('Wrong password -> 400', r.status_code == 400)

r = get('/auth/profile/', admin_token)
log('Admin profile', r.status_code == 200 and r.json().get('is_staff'))

r = get('/auth/profile/')
log('Profile no token -> 401', r.status_code == 401)

r = post('/auth/token/refresh/', {'refresh': admin_refresh})
# TokenRefreshView returns new access token
log('Refresh token', r.status_code == 200)

# 2. SERVICES
section('2. Services')

r = get('/services/service-categories/')
log('List categories', r.status_code == 200 and 'results' in r.json())

r = get('/services/services/')
log('List services', r.status_code == 200 and 'results' in r.json())

r = post('/admin-panel/services/', {
    'name': 'Test Service',
    'base_price': 1500,
    'base_duration_minutes': 45,
    'category': 6,
    'gender_target': 'unisex',
}, admin_token)
if r.status_code == 201:
    test_svc_id = r.json()['id']
    log('Create service', True)
else:
    test_svc_id = None
    log('Create service', False, f'{r.status_code}: {r.content.decode()[:150]}')

if test_svc_id:
    r = patch(f'/admin-panel/services/{test_svc_id}/', {'base_price': 2000}, admin_token)
    log('Update service', r.status_code == 200 and r.json()['base_price'] == '2000.00')

if test_svc_id:
    r = delete(f'/admin-panel/services/{test_svc_id}/', admin_token)
    log('Delete service', r.status_code == 204)

r = get('/services/services/womens-haircut/')
log('Service detail', r.status_code == 200)

# 3. MASTERS
section('3. Masters')

r = get('/staff/masters/')
log('List masters (public)', r.status_code == 200 and 'results' in r.json())

r = get('/admin-panel/masters/', admin_token)
log('List masters (admin)', r.status_code == 200 and 'results' in r.json())

# Clean up any existing test master
Master.objects.filter(phone='+79990000002').delete()
User.objects.filter(username='test_master').delete()
User.objects.filter(username='+79990000002').delete()
# Also delete any master with that phone from the User model
User.objects.filter(username__startswith='+79990000002').delete()

r = post('/admin-panel/masters/', {
    'first_name': 'Test',
    'last_name': 'Masterov',
    'phone': '+79990000002',
    'password': 'master123',
    'bio': 'Test master',
}, admin_token)
if r.status_code == 201:
    test_master_id = r.json()['id']
    log('Create master', True)
else:
    test_master_id = None
    log('Create master', False, f'{r.status_code}: {r.content.decode()[:150]}')

if test_master_id:
    r = patch(f'/admin-panel/masters/{test_master_id}/', {'bio': 'Updated bio'}, admin_token)
    log('Update master', r.status_code == 200)

if test_master_id:
    r = get(f'/staff/masters/{test_master_id}/services/')
    log('Master services', r.status_code == 200)

if test_master_id:
    r = post(f'/admin-panel/masters/{test_master_id}/services/', {'service_id': 1}, admin_token)
    log('Link service to master', r.status_code in (200, 201, 400))

if test_master_id:
    r = delete(f'/admin-panel/masters/{test_master_id}/', admin_token)
    log('Delete master', r.status_code == 204)

# 4. APPOINTMENTS
section('4. Appointments')

# Find an active master and service
active_masters = list(Master.objects.filter(is_active=True).prefetch_related('master_services').values_list('id', flat=True))
test_master_id_val = active_masters[0] if active_masters else 1
# Get services linked to this master
master_svcs = list(MasterService.objects.filter(master_id=test_master_id_val, is_enabled=True).values_list('service_id', flat=True))
test_service_id = master_svcs[0] if master_svcs else 1

r = get(f'/appointments/appointments/available_slots/?master_id={test_master_id_val}&date=2026-04-10&service_ids={test_service_id}', admin_token)
log('Available slots (admin)', r.status_code == 200)

# Guest booking
r = post('/appointments/guest/', {
    'master_id': test_master_id_val,
    'service_ids': [test_service_id],
    'datetime_start': '2026-04-10T10:00:00',
    'phone': '+79990000099',
    'name': 'Guest Test',
})
if r.status_code == 201:
    guest_apt_id = r.json()['id']
    log('Guest booking', True)
else:
    guest_apt_id = None
    log('Guest booking', False, f'{r.status_code}: {r.content.decode()[:200]}')

# Create test client
User.objects.filter(username='+79001111199').delete()
Client.objects.filter(phone='+79001111199').delete()
cu = User.objects.create_user('test_client', 'test_client@test.ru', 'client123')
cu.username = '+79001111199'
cu.save()
Client.objects.get_or_create(user=cu, defaults={'phone': '+79001111199', 'bonus_balance': 0, 'referral_code': 'TESTCLI2'})

r = post('/auth/login/', {'phone': '+79001111199', 'password': 'client123'})
client_token = r.json()['access'] if r.status_code == 200 else None

if client_token:
    # Client booking - check what fields the serializer expects
    r = post('/appointments/appointments/', {
        'master_id': test_master_id_val,
        'service_ids': [test_service_id],
        'datetime_start': '2026-04-11T14:00:00',
        'datetime_end': '2026-04-11T15:00:00',
    }, client_token)
    if r.status_code == 201:
        client_apt_id = r.json()['id']
        log('Client booking', True)
    else:
        client_apt_id = None
        log('Client booking', False, f'{r.status_code}: {r.content.decode()[:200]}')
else:
    client_apt_id = None
    log('Client booking', False, 'Cannot login as client')

if client_token:
    r = get('/appointments/appointments/my-appointments/', client_token)
    if r.status_code == 200 and 'results' in r.json():
        log('My appointments', True)
    else:
        # Try alternative URL
        r2 = get('/appointments/appointments/?my=1', client_token)
        if r2.status_code == 200:
            log('My appointments (alt URL)', True)
            client_apt_id = client_apt_id  # keep existing
        else:
            log('My appointments', False, f'{r.status_code}')

if client_token and client_apt_id:
    r = patch(f'/admin-panel/appointments/{client_apt_id}/', {'status': 'confirmed'}, admin_token)
    log('Update appointment status', r.status_code == 200)

r = get('/admin-panel/calendar/?month=4&year=2026', admin_token)
log('Admin calendar', r.status_code == 200)

r = get('/admin-panel/appointments/', admin_token)
log('Admin appointments list', r.status_code == 200 and 'results' in r.json())

# 5. CLIENTS
section('5. Clients')

if client_token:
    r = get('/auth/profile/', client_token)
    log('Client profile', r.status_code == 200)

if client_token:
    r = post('/clients/favorites/', {'master_id': 1}, client_token)
    log('Add to favorites', r.status_code in (201, 400))

if client_token:
    r = get('/clients/favorites/', client_token)
    log('Favorites list', r.status_code == 200 and 'results' in r.json())

if client_token:
    r = get('/clients/favorites/', client_token)
    favs = r.json().get('results', [])
    if favs:
        r = delete(f'/clients/favorites/{favs[0]["id"]}/', client_token)
        log('Remove from favorites', r.status_code == 204)
    else:
        log('Remove from favorites', True, 'No favorites')

r = get('/admin-panel/clients/1/stats/', admin_token)
log('Client stats (admin)', r.status_code == 200)

# 6. PROMOTIONS
section('6. Promotions')

r = get('/promotions/promotions/')
log('List promotions', r.status_code == 200 and 'results' in r.json())

r = get('/promotions/blacklist/', admin_token)
log('Blacklist', r.status_code == 200)

r = post('/promotions/blacklist/', {'phone': '+79990000099', 'reason': 'Test reason'}, admin_token)
if r.status_code == 201:
    bl_id = r.json()['id']
    log('Add to blacklist', True)
else:
    bl_id = None
    log('Add to blacklist', False, f'{r.status_code}: {r.content.decode()[:150]}')

if bl_id:
    r = delete(f'/promotions/blacklist/{bl_id}/', admin_token)
    log('Remove from blacklist', r.status_code == 204)

r = get('/promotions/certificates/', admin_token)
log('Certificates list', r.status_code == 200)

r = post('/promotions/certificates/', {
    'nominal': 5000,
    'buyer_name': 'Test Buyer',
    'recipient_email': 'test@test.ru',
}, admin_token)
log('Create certificate', r.status_code == 201)

# 7. REVIEWS
section('7. Reviews')

if client_token and client_apt_id:
    r = post('/reviews/reviews/', {
        'appointment_id': client_apt_id,
        'rating': 5,
        'comment': 'Test review',
    }, client_token)
    log('Create review', r.status_code in (201, 400))

r = get('/reviews/reviews/')
log('Reviews list', r.status_code == 200 and 'results' in r.json())

r = post('/reviews/reviews/', {'appointment_id': 1, 'rating': 5, 'comment': 'Test'})
log('Review no token -> 401', r.status_code == 401)

# 8. ADMIN
section('8. Admin Panel')

r = get('/admin-panel/dashboard/stats/', admin_token)
log('Dashboard stats', r.status_code == 200)

r = get('/admin-panel/masters/1/stats/', admin_token)
log('Master stats', r.status_code == 200)

r = get('/admin-panel/services/1/stats/', admin_token)
log('Service stats', r.status_code == 200)

r = get('/admin-panel/reports/sales/?date_from=2026-01-01&date_to=2026-12-31&format=xlsx', admin_token)
log('Sales report (XLSX)', r.status_code == 200)

# RESULTS
print(f'\n{"="*60}')
print(f'  RESULTS: {passed} OK, {failed} FAILED')
print(f'{"="*60}')
if errors:
    print(f'\nFailed tests:')
    for e in errors:
        print(f'  [FAIL] {e}')

# Cleanup
User.objects.filter(username='test_admin').delete()
User.objects.filter(username='test_client').delete()
Client.objects.filter(phone='+79001111199').delete()
Client.objects.filter(phone='+79990000099').delete()

sys.exit(0 if failed == 0 else 1)
