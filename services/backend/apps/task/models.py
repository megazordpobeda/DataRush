from uuid import uuid4

from django.db import models

from apps.task.validators import ContestTaskCriteriesValidator
from apps.competition.models import Competition
from apps.core.models import BaseModel
from apps.user.models import User


class CompetitionTask(BaseModel):
    class CompetitionTaskType(models.TextChoices):
        INPUT = "input"
        CHECKER = "checker"
        REVIEW = "review"

    def answer_file_upload_to(instance, filename) -> str:
        return f"/tasks/{instance.id}/answer/{uuid4()}/filename"

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    title = models.TextField(verbose_name="заголовок", max_length=50)
    description = models.TextField(verbose_name="описание", max_length=300)
    type = models.CharField(choices=CompetitionTaskType, max_length=8)

    # only when "input" or "checker" type
    correct_answer_file = models.FileField(
        upload_to=answer_file_upload_to, null=True, blank=True
    )
    points = models.IntegerField(null=True, blank=True)

    # only when "checker" type
    answer_file_path = models.TextField(null=True, blank=True)

    # only when "review" type
    criteries = models.JSONField(blank=True, null=True)

    def clean(self):
        ContestTaskCriteriesValidator()(self)


class CompetetionTaskSumbission(BaseModel):
    class StatusChoices(models.TextChoices):
        SENT = "sent"
        CHECKING = "checking"
        CHECKED = "checked"

    def submission_content_upload_to(instance, filename) -> str:
        return f"/submissions/{instance.id}/content"

    def submission_stdout_upload_to(instance, filename) -> str:
        return f"/submissions/{instance.id}/stdout"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(CompetitionTask, on_delete=models.CASCADE)

    status = models.CharField(
        choices=StatusChoices.choices,
        default=StatusChoices.SENT,
        max_length=8,
    )

    # code or text or file
    content = models.FileField(upload_to=submission_content_upload_to)

    # only if task type is checker
    stdout = models.FileField(
        upload_to=submission_stdout_upload_to, null=True, blank=True
    )

    # depends on task type:
    # - input: {"correct": boolean}
    # - file: {"total_points": integer, "by_criteria": ["criteria_name": integer]}
    # - code: {"correct": boolean}
    result = models.JSONField(default=None, null=True, blank=True)
    # just more readable result representation, maybe will be calcuated somehow more complex depends on criteria
    earned_points = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)
