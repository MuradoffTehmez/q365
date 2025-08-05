from django.contrib import admin
from .models import (
    ServiceTicket, TicketComment, TicketAttachment, TicketTimeLog,
    RMA, ServiceCall, ServicePlan, SLA, Region, Zone, Skill, TechnicianSkill
)

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 1


class TicketTimeLogInline(admin.TabularInline):
    model = TicketTimeLog
    extra = 1


class RMAInline(admin.TabularInline):
    model = RMA
    extra = 1


class ServiceCallInline(admin.TabularInline):
    model = ServiceCall
    extra = 1


@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'customer', 'status', 'priority', 'type', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'type', 'created_at')
    search_fields = ('title', 'description', 'customer__company_name', 'customer__first_name', 'customer__last_name')
    inlines = [TicketCommentInline, TicketAttachmentInline, TicketTimeLogInline, RMAInline, ServiceCallInline]
    readonly_fields = ('created_at', 'updated_at', 'resolved_at', 'closed_at')


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('content', 'ticket__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'ticket', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'ticket__title')
    readonly_fields = ('uploaded_at',)


@admin.register(TicketTimeLog)
class TicketTimeLogAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'hours', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('description', 'ticket__title')
    readonly_fields = ('created_at',)


@admin.register(RMA)
class RMAAdmin(admin.ModelAdmin):
    list_display = ('rma_number', 'ticket', 'product_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('rma_number', 'product_name', 'serial_number', 'ticket__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceCall)
class ServiceCallAdmin(admin.ModelAdmin):
    list_display = ('title', 'ticket', 'status', 'scheduled_date', 'technician', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'ticket__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'type', 'status', 'start_date', 'end_date', 'price')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('name', 'description', 'customer__company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'response_time', 'resolution_time', 'business_hours_only', 'is_active')
    list_filter = ('priority', 'business_hours_only', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'is_active', 'created_at')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TechnicianSkill)
class TechnicianSkillAdmin(admin.ModelAdmin):
    list_display = ('technician', 'skill', 'proficiency_level', 'certified', 'certification_date')
    list_filter = ('skill', 'proficiency_level', 'certified')
    search_fields = ('technician__first_name', 'technician__last_name', 'skill__name')
    readonly_fields = ('created_at',)