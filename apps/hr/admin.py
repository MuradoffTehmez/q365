from django.contrib import admin
from .models import (
    Employee, Skill, EmployeeSkill, Certification, Education, Experience,
    LeaveType, Leave, LeaveBalance, Benefit, Training, TrainingParticipant,
    PerformanceReview, PerformanceGoal, Document
)

class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class LeaveInline(admin.TabularInline):
    model = Leave
    extra = 1


class LeaveBalanceInline(admin.TabularInline):
    model = LeaveBalance
    extra = 1


class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1


class TrainingParticipantInline(admin.TabularInline):
    model = TrainingParticipant
    extra = 1


class PerformanceGoalInline(admin.TabularInline):
    model = PerformanceGoal
    extra = 1


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'employee_id', 'department', 'position', 'employment_type', 'status', 'hire_date')
    list_filter = ('department', 'employment_type', 'status', 'hire_date')
    search_fields = ('first_name', 'last_name', 'employee_id', 'email', 'phone')
    inlines = [
        EmployeeSkillInline, CertificationInline, EducationInline, ExperienceInline,
        LeaveInline, LeaveBalanceInline, BenefitInline, TrainingParticipantInline,
        PerformanceGoalInline, DocumentInline
    ]
    readonly_fields = ('created_at', 'updated_at', 'years_of_service')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ('employee', 'skill', 'proficiency_level', 'years_of_experience', 'is_certified')
    list_filter = ('skill', 'proficiency_level', 'is_certified')
    search_fields = ('employee__first_name', 'employee__last_name', 'skill__name')
    readonly_fields = ('created_at',)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'issued_by', 'issue_date', 'expiry_date', 'is_expired')
    list_filter = ('issue_date', 'expiry_date', 'is_expired')
    search_fields = ('employee__first_name', 'employee__last_name', 'name', 'issued_by')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date')
    list_filter = ('degree', 'start_date', 'end_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'institution', 'field_of_study')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'position', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'company', 'position')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'requires_approval', 'paid', 'days_allowed', 'is_active')
    list_filter = ('requires_approval', 'paid', 'is_active')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'approved_by')
    list_filter = ('leave_type', 'status', 'start_date', 'end_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
    readonly_fields = ('approved_by', 'approved_at', 'created_at', 'updated_at', 'total_days')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'year', 'total_days', 'used_days', 'remaining_days')
    list_filter = ('leave_type', 'year')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at', 'remaining_days')


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'type', 'provider', 'start_date', 'end_date', 'is_active')
    list_filter = ('type', 'start_date', 'end_date', 'is_active')
    search_fields = ('employee__first_name', 'employee__last_name', 'name', 'provider')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location', 'provider', 'status', 'max_participants')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'location', 'provider')
    inlines = [TrainingParticipantInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(TrainingParticipant)
class TrainingParticipantAdmin(admin.ModelAdmin):
    list_display = ('training', 'employee', 'status', 'rating', 'certificate_issued')
    list_filter = ('status', 'training__start_date', 'certificate_issued')
    search_fields = ('training__name', 'employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'title', 'review_date', 'overall_rating', 'status')
    list_filter = ('status', 'review_date', 'overall_rating')
    search_fields = ('employee__first_name', 'employee__last_name', 'title')
    inlines = [PerformanceGoalInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'priority', 'progress', 'target_date')
    list_filter = ('status', 'priority', 'target_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'type', 'expiry_date', 'is_expired', 'is_confidential')
    list_filter = ('type', 'expiry_date', 'is_expired', 'is_confidential')
    search_fields = ('employee__first_name', 'employee__last_name', 'title')
    readonly_fields = ('created_at', 'updated_at')