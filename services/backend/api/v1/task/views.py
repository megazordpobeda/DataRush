from http import HTTPStatus as status
from uuid import UUID

from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import File, Router, UploadedFile

from api.v1.ping.schemas import PingOut
from api.v1.schemas import ForbiddenError, NotFoundError, UnauthorizedError
from api.v1.task.schemas import (
    HistorySubmissionOut,
    TaskAttachmentSchema,
    TaskOutSchema,
    TaskStatusSchema,
    TaskSubmissionOut,
)
from apps.achievement.models import Achievement, UserAchievement
from apps.competition.models import State
from apps.task.models import (
    Competition,
    CompetitionTask,
    CompetitionTaskAttachment,
    CompetitionTaskSubmission,
)
from apps.task.tasks import analyze_data_task

router = Router(tags=["competition"])


@router.post(
    "competitions/{competition_id}/start",
    description="Start a competition completing (open access to tasks)",
    response={
        status.OK: PingOut,
        status.UNAUTHORIZED: UnauthorizedError,
        status.NOT_FOUND: NotFoundError,
    },
)
def start_competition(request, competition_id: UUID) -> PingOut:
    competition = get_object_or_404(Competition, pk=competition_id)
    competition.participants.add(request.auth)
    state_obj, _ = State.objects.update_or_create(
        user=request.auth, competition=competition, state="started"
    )
    return status.OK, PingOut()


@router.get(
    "competitions/{competition_id}/tasks",
    description="Get all tasks of competition (works only if user started competition)",
    response={
        status.OK: list[TaskOutSchema],
        status.UNAUTHORIZED: UnauthorizedError,
        status.FORBIDDEN: ForbiddenError,
        status.NOT_FOUND: NotFoundError,
    },
)
def get_competition_tasks(
    request, competition_id: UUID
) -> list[TaskOutSchema]:
    competition = get_object_or_404(Competition, pk=competition_id)
    state = State.objects.filter(
        user=request.auth, competition=competition, state="started"
    ).first()
    if not state:
        return 403, ForbiddenError()

    return status.OK, CompetitionTask.objects.filter(
        competition=competition
    ).all()


@router.get(
    "competitions/{competition_id}/tasks/{task_id}",
    description="Get a task of competition task",
    response={
        status.OK: TaskOutSchema,
        status.UNAUTHORIZED: UnauthorizedError,
        status.FORBIDDEN: ForbiddenError,
        status.NOT_FOUND: NotFoundError,
    },
)
def get_task(request, competition_id: str, task_id: str) -> TaskOutSchema: ...


@router.post(
    "competitions/{competition_id}/tasks/{task_id}/submit",
    description="Submit task solution",
    response={
        status.OK: TaskSubmissionOut,
        status.UNAUTHORIZED: UnauthorizedError,
        status.FORBIDDEN: ForbiddenError,
        status.NOT_FOUND: NotFoundError,
    },
)
def submit_task(
    request,
    competition_id: str,
    task_id: str,
    content: UploadedFile = File(...),  # TODO: вот это надо переделать
) -> TaskSubmissionOut:
    user = request.auth
    competition = get_object_or_404(Competition, id=competition_id)
    task = get_object_or_404(
        CompetitionTask, competition=competition, id=task_id
    )

    if not CompetitionTaskSubmission.objects.filter(user=user).exists():
        first_steps_achievement = Achievement.objects.get(slug="first_steps")
        UserAchievement.objects.create(
            user=user, achievement=first_steps_achievement
        )

    total_attempts = CompetitionTaskSubmission.objects.filter(
        user=user, task=task
    ).count()
    if task.max_attempts == total_attempts:
        return status.FORBIDDEN, ForbiddenError()

    if task.type == CompetitionTask.CompetitionTaskType.INPUT:
        user_input = content.read()
        correct_answer = task.correct_answer_file.read()
        verdict = user_input == correct_answer
        submission = CompetitionTaskSubmission.objects.create(
            user=user,
            task=task,
            status=CompetitionTaskSubmission.StatusChoices.CHECKED,
            content=content,
            result={"correct": verdict},
            earned_points=task.points if verdict else 0,
        )
    if task.type == CompetitionTask.CompetitionTaskType.REVIEW:
        submission = CompetitionTaskSubmission.objects.create(
            user=user,
            task=task,
            status=CompetitionTaskSubmission.StatusChoices.SENT,
            content=content,
        )
        submission.send_on_review()
    if task.type == CompetitionTask.CompetitionTaskType.CHECKER:
        submission = CompetitionTaskSubmission.objects.create(
            user=user,
            task=task,
            status=CompetitionTaskSubmission.StatusChoices.CHECKING,
            content=content,
        )
        analyze_data_task.delay(submission_id=submission.id)

    return TaskSubmissionOut(submission_id=submission.id)


@router.get(
    "competitions/{competition_id}/tasks/{task_id}/history",
    response={
        status.OK: list[HistorySubmissionOut],
        status.UNAUTHORIZED: UnauthorizedError,
    },
)
def get_submissions_history(request, competition_id: UUID, task_id: UUID):
    task = get_object_or_404(
        CompetitionTask, competition_id=competition_id, id=task_id
    )
    submissions_history = CompetitionTaskSubmission.objects.filter(
        task=task, user=request.auth
    )

    return status.OK, submissions_history


@router.get(
    "competitions/{competition_id}/tasks/{task_id}/attachments",
    response={
        status.OK: list[TaskAttachmentSchema],
        status.UNAUTHORIZED: UnauthorizedError,
    },
)
def get_task_attachments(request, competition_id: UUID, task_id: UUID):
    task = get_object_or_404(CompetitionTask, id=task_id)
    return status.OK, CompetitionTaskAttachment.objects.filter(task=task).all()


@router.get(
    "competitions/{competition_id}/results",
    response={
        status.OK: list[TaskStatusSchema],
        status.UNAUTHORIZED: UnauthorizedError,
    },
)
def get_competition_results(request, competition_id: UUID):
    tasks = get_list_or_404(CompetitionTask, competition_id=competition_id)

    data = []

    for task in tasks:
        submissions = (
            CompetitionTaskSubmission.objects.filter(
                user=request.auth, task=task
            )
            .filter(status="checked")
            .order_by("-earned_points")
            .all()
        )
        if not submissions:
            all_submissions_count = CompetitionTaskSubmission.objects.filter(
                user=request.auth, task=task
            ).count()
            if all_submissions_count == 0:
                result = -2
            else:
                result = -1
        else:
            result = submissions[0].earned_points
        data.append(
            TaskStatusSchema(
                task_name=task.title,
                result=result,
                max_points=task.points,
                position=task.in_competition_position,
            )
        )

    return status.OK, data
