from django.contrib import admin
from .models import Report, Dashboard, DashboardWidget, KPI, ScheduledReport

class DashboardWidgetInline(admin.TabularInline):
    model = DashboardWidget
    extra = 1


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'organization', 'is_public', 'created_by', 'created_at')
    list_filter = ('type', 'status', 'is_public', 'organization', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('allowed_users', 'allowed_roles')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_public', 'created_by', 'created_at')
    list_filter = ('is_public', 'organization', 'created_at')
    search_fields = ('name', 'description')
    inlines = [DashboardWidgetInline]
    filter_horizontal = ('allowed_users', 'allowed_roles')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('dashboard', 'title', 'type', 'position_x', 'position_y', 'width', 'height')
    list_filter = ('type', 'dashboard')
    search_fields = ('title', 'dashboard__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'model', 'field', 'aggregation', 'organization', 'is_public', 'created_by', 'created_at')
    list_filter = ('type', 'model', 'aggregation', 'is_public', 'organization', 'created_at')
    search_fields = ('name', 'description', 'model', 'field')
    filter_horizontal = ('allowed_users', 'allowed_roles')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report', 'frequency', 'format', 'is_active', 'next_run', 'last_run', 'created_by', 'created_at')
    list_filter = ('frequency', 'format', 'is_active', 'created_at')
    search_fields = ('name', 'report__name')
    filter_horizontal = ('recipients',)
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'last_run', 'next_run')