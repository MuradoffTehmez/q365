from django.contrib import admin
from .models import (
    Lead, Customer, Contact, Opportunity, Quotation, QuotationItem,
    Campaign, EmailTemplate, EmailCampaign, SalesActivity, Commission
)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'status', 'source', 'assigned_to', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('first_name', 'last_name', 'company', 'email')
    readonly_fields = ('created_at', 'updated_at')


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'email', 'phone', 'assigned_to', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('first_name', 'last_name', 'company_name', 'email')
    inlines = [ContactInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'customer', 'position', 'email', 'phone', 'is_primary')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'customer__company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'stage', 'amount', 'probability', 'expected_close_date', 'assigned_to')
    list_filter = ('stage', 'created_at')
    search_fields = ('name', 'customer__company_name', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('created_at', 'updated_at')


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'status', 'total', 'valid_until', 'assigned_to')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'customer__company_name')
    inlines = [QuotationItemInline]
    readonly_fields = ('created_at', 'updated_at', 'tax_amount', 'total')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'start_date', 'end_date', 'budget', 'assigned_to')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'subject', 'content')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'template', 'status', 'scheduled_at', 'sent_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'campaign__name', 'template__name')
    filter_horizontal = ('recipients',)
    readonly_fields = ('created_at', 'updated_at', 'sent_at')


@admin.register(SalesActivity)
class SalesActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'type', 'status', 'priority', 'due_date', 'assigned_to')
    list_filter = ('type', 'status', 'priority', 'created_at')
    search_fields = ('subject', 'description')
    readonly_fields = ('created_at', 'updated_at', 'completed_date')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'opportunity', 'amount', 'percentage', 'status', 'paid_date')
    list_filter = ('status', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'opportunity__name')
    readonly_fields = ('created_at', 'updated_at')