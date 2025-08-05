from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Workflow, State, Transition, WorkflowInstance, WorkflowHistory,
    WorkflowTemplate, WorkflowTrigger, ScheduledWorkflow
)

class StateInline(admin.TabularInline):
    model = State
    extra = 1


class TransitionInline(admin.TabularInline):
    model = Transition
    extra = 1
    fk_name = 'workflow'


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'model', 'created_at')
    search_fields = ('name', 'description')
    inlines = [StateInline, TransitionInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter by allowed workflows for non-superusers
            return qs.filter(
                models.Q(is_public=True) |
                models.Q(allowed_users=request.user) |
                models.Q(allowed_roles__in=request.user.user_roles.all())
            ).distinct()
        return qs


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow', 'is_initial', 'is_final', 'color', 'order')
    list_filter = ('workflow', 'is_initial', 'is_final')
    search_fields = ('name', 'description', 'workflow__name')
    readonly_fields = ('created_at',)


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow', 'from_state', 'to_state', 'order')
    list_filter = ('workflow', 'from_state', 'to_state')
    search_fields = ('name', 'description', 'workflow__name')
    readonly_fields = ('created_at',)


class WorkflowHistoryInline(admin.TabularInline):
    model = WorkflowHistory
    extra = 0
    readonly_fields = ('from_state', 'to_state', 'transition', 'triggered_by', 'triggered_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'content_object', 'current_state', 'status', 'started_by', 'started_at')
    list_filter = ('workflow', 'status', 'current_state', 'started_at')
    search_fields = ('workflow__name', 'data')
    inlines = [WorkflowHistoryInline]
    readonly_fields = ('workflow', 'content_type', 'object_id', 'started_by', 'started_at', 'completed_at')
    
    def content_object(self, obj):
        if obj.content_object:
            url = reverse(f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change', args=[obj.object_id])
            return format_html('<a href="{}">{}</a>', url, obj.content_object)
        return "-"


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = ('workflow_instance', 'from_state', 'to_state', 'transition', 'triggered_by', 'triggered_at')
    list_filter = ('workflow_instance__workflow', 'from_state', 'to_state', 'triggered_at')
    search_fields = ('workflow_instance__workflow__name', 'notes')
    readonly_fields = ('workflow_instance', 'from_state', 'to_state', 'transition', 'triggered_by', 'triggered_at')


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'model', 'is_public', 'created_by', 'created_at')
    list_filter = ('category', 'model', 'is_public', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(WorkflowTrigger)
class WorkflowTriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow', 'type', 'field_name', 'is_active', 'created_at')
    list_filter = ('workflow', 'type', 'is_active', 'created_at')
    search_fields = ('name', 'workflow__name', 'field_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ScheduledWorkflow)
class ScheduledWorkflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow', 'schedule_type', 'scheduled_date', 'status', 'last_run', 'next_run')
    list_filter = ('workflow', 'schedule_type', 'status', 'scheduled_date')
    search_fields = ('name', 'description', 'workflow__name')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'last_run', 'next_run')