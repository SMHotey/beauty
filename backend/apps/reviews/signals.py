from django.db.models import Avg
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from apps.reviews.models import Review


@receiver(post_save, sender=Review)
def update_master_rating_on_review_save(sender, instance, created, **kwargs):
    if created:
        _recalculate_master_rating(instance.appointment.master)


@receiver(post_delete, sender=Review)
def update_master_rating_on_review_delete(sender, instance, **kwargs):
    _recalculate_master_rating(instance.appointment.master)


def _recalculate_master_rating(master):
    avg = Review.objects.filter(appointment__master=master).aggregate(avg_rating=Avg('rating'))['avg_rating']
    master._cached_rating = round(avg, 1) if avg else None
