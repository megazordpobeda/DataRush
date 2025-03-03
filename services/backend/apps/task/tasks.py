import hashlib

import httpx
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import base64

from apps.task.models import CompetitionTaskSubmission


@shared_task(bind=True, max_retries=3)
def analyze_data_task(self, submission_id):
    submission = CompetitionTaskSubmission.objects.get(id=submission_id)
    try:
        code = submission.content.read()
        files = [
            {
                "url": (
                    f"{settings.MINIO_DEFAULT_CUSTOM_ENDPOINT_URL}/"
                    f"{urlparse(attachment.file.url).path}"
                ),
                "bind_path": attachment.bind_at,
            }
            for attachment in submission.task.attachments.filter(
                bind_at__isnull=False
            )
        ]

        response = httpx.post(
            f"{settings.CHECKER_API_ENDPOINT}/execute",
            json={
                "files": files,
                "code": base64.b64encode(code),
                "answer_file_path": submission.task.answer_file_path,
                "expected_hash": hashlib.sha256(
                    submission.task.correct_answer_file.read()
                ).hexdigest(),
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        submission.stdout.save("output.txt", ContentFile(result["output"]))
        submission.result = {
            "correct": result["correct"],
            "hash_match": result["hash_match"],
            "error": result.get("error"),
        }
        submission.earned_points = (
            submission.task.points if result["correct"] else 0
        )
        submission.status = CompetitionTaskSubmission.StatusChoices.CHECKED

    except httpx.RequestError:
        self.retry(countdown=2**self.request.retries)
    except Exception as e:
        submission.result = {"error": str(e), "success": False}
        submission.status = CompetitionTaskSubmission.StatusChoices.CHECKED
        submission.earned_points = 0
    finally:
        submission.save()
