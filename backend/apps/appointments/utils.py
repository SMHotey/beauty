from datetime import datetime, timedelta, date
from django.utils import timezone
from apps.staff.models import Master
from apps.promotions.models import Setting


def get_setting(key, default):
    setting = Setting.objects.filter(key=key).first()
    return int(setting.value) if setting else default


def get_available_slots(master_id, date_str, service_ids):
    try:
        master = Master.objects.get(id=master_id)
    except Master.DoesNotExist:
        return []

    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    weekday = target_date.weekday()

    work_hours = master.working_hours.get(str(weekday))
    if not work_hours:
        return []

    # work_hours can be a dict {'start': ..., 'end': ...} or a list of such dicts
    if isinstance(work_hours, list):
        if not work_hours:
            return []
        work_hours = work_hours[0]

    work_start = datetime.strptime(work_hours['start'], '%H:%M').time()
    work_end = datetime.strptime(work_hours['end'], '%H:%M').time()

    breaks = [b for b in master.break_slots if b.get('weekday') == weekday]

    existing = master.appointments.filter(
        datetime_start__date=target_date,
        status__in=['pending', 'confirmed']
    ).order_by('datetime_start')

    buffer = get_setting('APPOINTMENT_BUFFER_MINUTES', 10)

    total_duration = 0
    from apps.staff.models import MasterService
    for sid in service_ids:
        ms = MasterService.objects.filter(master=master, service_id=sid, is_enabled=True).first()
        if ms:
            total_duration += ms.duration_minutes
        else:
            from apps.services.models import Service
            s = Service.objects.get(id=sid)
            total_duration += s.base_duration_minutes
    total_duration += buffer

    slots = []
    current = datetime.combine(target_date, work_start)
    end_limit = datetime.combine(target_date, work_end) - timedelta(minutes=total_duration)

    while current <= end_limit:
        slot_end = current + timedelta(minutes=total_duration)
        overlaps = False

        for appt in existing:
            if current < appt.datetime_end and slot_end > appt.datetime_start:
                overlaps = True
                break

        if not overlaps:
            for brk in breaks:
                brk_start = datetime.combine(target_date, datetime.strptime(brk['start'], '%H:%M').time())
                brk_end = datetime.combine(target_date, datetime.strptime(brk['end'], '%H:%M').time())
                if current < brk_end and slot_end > brk_start:
                    overlaps = True
                    break

        if not overlaps:
            slots.append(current.strftime('%Y-%m-%dT%H:%M:%S'))

        current += timedelta(minutes=30)

    return slots
