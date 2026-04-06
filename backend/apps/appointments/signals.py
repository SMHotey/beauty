from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import models
from django.db.models import F
from apps.appointments.models import Appointment
from apps.promotions.models import Setting


def get_setting(key, default):
    setting = Setting.objects.filter(key=key).first()
    if setting:
        try:
            return int(setting.value)
        except (ValueError, TypeError):
            pass
    return default


@receiver(pre_save, sender=Appointment)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        old = Appointment.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
        instance._old_status = old
    else:
        instance._old_status = None


@receiver(post_save, sender=Appointment)
def award_bonus_on_completion(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed' and instance.client:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != 'completed':
            bonus_percent = get_setting('BONUS_PERCENT', 5)
            bonus = int(instance.total_price * bonus_percent / 100)
            if bonus > 0:
                instance.client.bonus_balance = F('bonus_balance') + bonus
                instance.client.save(update_fields=['bonus_balance'])

                if instance.client.referred_by:
                    referral_bonus = get_setting('REFERRAL_BONUS', 500)
                    referrer = instance.client.referred_by
                    referrer.bonus_balance = F('bonus_balance') + referral_bonus
                    referrer.save(update_fields=['bonus_balance'])


def update_master_rating(master):
    """Recalculate and cache master's average rating."""
    from apps.reviews.models import Review
    reviews = Review.objects.filter(appointment__master=master, is_deleted=False)
    if reviews.exists():
        avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
        master._cached_rating = round(avg, 1) if avg else None
    else:
        master._cached_rating = None
    master.save(update_fields=['_cached_rating'])


@receiver(post_save, sender=Appointment)
def update_rating_on_completion(sender, instance, created, **kwargs):
    """Update master rating when appointment is completed."""
    if instance.status == 'completed':
        from apps.reviews.models import Review
        review = Review.objects.filter(appointment=instance, is_deleted=False).first()
        if review:
            update_master_rating(instance.master)


@receiver(post_save)
def update_rating_on_review_create(sender, instance, created, **kwargs):
    """Update master rating when a new review is created."""
    if sender.__name__ == 'Review' and created:
        update_master_rating(instance.appointment.master)


@receiver(post_delete)
def update_rating_on_review_delete(sender, instance, **kwargs):
    """Update master rating when a review is deleted."""
    if sender.__name__ == 'Review':
        update_master_rating(instance.appointment.master)
