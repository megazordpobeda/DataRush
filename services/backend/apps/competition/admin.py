from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils.html import format_html

from apps.user.models import User
from apps.competition.models import Competition
from apps.task.admin import CompetitionTaskInline
from apps.task.models import CompetitionTaskSubmission, CompetitionTask


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "end_date",
        "type",
        "view_leaderboard",
    )
    search_fields = (
        "title",
        "description",
    )
    list_filter = (
        "type",
        "participation_type",
    )
    inlines = [CompetitionTaskInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('leaderboard/', self.admin_site.admin_view(self.leaderboard_view), name='competition_leaderboard'),
            path('<uuid:competition_id>/leaderboard/', self.admin_site.admin_view(self.competition_leaderboard_view), 
                 name='competition_specific_leaderboard'),
        ]
        return custom_urls + urls

    def view_leaderboard(self, obj):
        url = reverse('admin:competition_specific_leaderboard', args=[obj.id])
        return format_html('<a href="{}">перейти</a>', url)
    
    view_leaderboard.short_description = "Лидерборд"
    view_leaderboard.allow_tags = True

    def competition_leaderboard_view(self, request, competition_id):
        competition = get_object_or_404(Competition, id=competition_id)
        
        competition_tasks = CompetitionTask.objects.filter(competition=competition)
        
        leaderboard = User.objects.annotate(
            total_score=Sum(
                'competitiontasksubmission__earned_points',
                filter=Q(
                    competitiontasksubmission__status='checked',
                    competitiontasksubmission__task__in=competition_tasks
                )
            )
        ).exclude(total_score__isnull=True).order_by('-total_score')[:20]

        context = dict(
            self.admin_site.each_context(request),
            title=f"Лидерборд для {competition.title}",
            leaderboard=leaderboard,
            competition=competition,
        )
        return TemplateResponse(request, "admin/competition_leaderboard.html", context)

    def leaderboard_view(self, request):
        leaderboard = User.objects.annotate(
            total_score=Sum(
                'competitiontasksubmission__earned_points',
                filter=Q(competitiontasksubmission__status='checked')
            )
        ).exclude(total_score__isnull=True).order_by('-total_score')[:20]

        context = dict(
            self.admin_site.each_context(request),
            title="Global Competition Leaderboard",
            leaderboard=leaderboard,
        )
        return TemplateResponse(request, "admin/competition_leaderboard.html", context)
