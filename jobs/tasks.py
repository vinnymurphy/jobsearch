from .models import Job

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def perform_semantic_match(self, job_id):
    try:
        job = Job.objects.get(id=job_id)

        # 1. Prepare the prompt (Assume resume text is stored/accessible)
        resume_text = "Your RelOps & System Architect experience..."
        prompt = (
            f"Analyze this job: {job.description}\n"
            f"against this resume: {resume_text}"
        )

        # 2. Call the LLM (Mocking the AI call for now)
        # In production, use your preferred LLM client here
        ai_response = {
            "overall_score": 88,
            "technical_alignment": 92,
            "gap_analysis": ["React experience", "AWS Lambda"],
            "strategy": "Emphasize Django/Celery scaling and "
            "Linux workstation optimization.",
            "raw_prompt_used": prompt[
                :1000
            ],  # Store truncated prompt for debugging
        }

        # 3. Update the Job record
        job.match_score = ai_response
        job.last_matched_at = timezone.now()
        job.save()

        return f"Successfully matched Job {job_id}"
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found")
    except Exception as exc:
        logger.error(f"Error matching job {job_id}: {exc}")
        raise self.retry(exc=exc, countdown=60) from exc
