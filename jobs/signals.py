from .models import Job
from .tasks import perform_semantic_match

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Job)
def trigger_ai_analysis(sender, instance, created, **kwargs):
    if created and settings.JOBS_ENABLE_AI_ANALYSIS:
        # Send the job to Celery for background processing
        perform_semantic_match.delay(instance.id)
