from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import User, Department, Sector, Team

class Employee(models.Model):
    """Employee model"""
    GENDER_CHOICES = (
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', _('Single')),
        ('married', _('Married')),
        ('divorced', _('Divorced')),
        ('widowed', _('Widowed')),
    )
    
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('contract', _('Contract')),
        ('intern', _('Intern')),
        ('other', _('Other')),
    )
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('on_leave', _('On Leave')),
        ('terminated', _('Terminated')),
        ('retired', _('Retired')),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee'
    )
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    middle_name = models.CharField(_('middle name'), max_length=100, blank=True)
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    place_of_birth = models.CharField(_('place of birth'), max_length=100, blank=True)
    nationality = models.CharField(_('nationality'), max_length=100, blank=True)
    marital_status = models.CharField(
        _('marital status'),
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )
    employment_type = models.CharField(
        _('employment type'),
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    hire_date = models.DateField(_('hire date'))
    termination_date = models.DateField(_('termination date'), null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    position = models.CharField(_('position'), max_length=100, blank=True)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    emergency_contact_name = models.CharField(_('emergency contact name'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('emergency contact phone'), max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(_('emergency contact relationship'), max_length=50, blank=True)
    bank_name = models.CharField(_('bank name'), max_length=100, blank=True)
    bank_account = models.CharField(_('bank account'), max_length=100, blank=True)
    bank_branch = models.CharField(_('bank branch'), max_length=100, blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    social_security_id = models.CharField(_('social security ID'), max_length=50, blank=True)
    passport_number = models.CharField(_('passport number'), max_length=50, blank=True)
    passport_expiry = models.DateField(_('passport expiry'), null=True, blank=True)
    visa_number = models.CharField(_('visa number'), max_length=50, blank=True)
    visa_expiry = models.DateField(_('visa expiry'), null=True, blank=True)
    work_permit_number = models.CharField(_('work permit number'), max_length=50, blank=True)
    work_permit_expiry = models.DateField(_('work permit expiry'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='employee_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def years_of_service(self):
        """Calculate years of service"""
        if not self.hire_date:
            return 0
        
        end_date = self.termination_date or timezone.now().date()
        delta = end_date - self.hire_date
        return delta.days // 365


class Skill(models.Model):
    """Skill model"""
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    category = models.CharField(_('category'), max_length=100, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    """Employee skill model"""
    PROFICIENCY_CHOICES = (
        (1, _('Beginner')),
        (2, _('Novice')),
        (3, _('Intermediate')),
        (4, _('Advanced')),
        (5, _('Expert')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    proficiency_level = models.IntegerField(
        _('proficiency level'),
        choices=PROFICIENCY_CHOICES,
        default=1
    )
    years_of_experience = models.IntegerField(
        _('years of experience'),
        default=0
    )
    is_certified = models.BooleanField(_('is certified'), default=False)
    certification_date = models.DateField(_('certification date'), null=True, blank=True)
    certification_expiry = models.DateField(_('certification expiry'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Employee Skill')
        verbose_name_plural = _('Employee Skills')
        unique_together = ('employee', 'skill')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.skill.name}"


class Certification(models.Model):
    """Certification model"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    name = models.CharField(_('name'), max_length=255)
    issued_by = models.CharField(_('issued by'), max_length=255)
    issue_date = models.DateField(_('issue date'))
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    credential_id = models.CharField(_('credential ID'), max_length=100, blank=True)
    credential_url = models.URLField(_('credential URL'), blank=True)
    attachment = models.FileField(_('attachment'), upload_to='certification_attachments/', blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.name}"
    
    @property
    def is_expired(self):
        """Check if certification is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()


class Education(models.Model):
    """Education model"""
    DEGREE_CHOICES = (
        ('high_school', _('High School')),
        ('associate', _('Associate Degree')),
        ('bachelor', _('Bachelor Degree')),
        ('master', _('Master Degree')),
        ('doctorate', _('Doctorate Degree')),
        ('other', _('Other')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    institution = models.CharField(_('institution'), max_length=255)
    degree = models.CharField(
        _('degree'),
        max_length=20,
        choices=DEGREE_CHOICES
    )
    field_of_study = models.CharField(_('field of study'), max_length=255)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    gpa = models.DecimalField(
        _('GPA'),
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    description = models.TextField(_('description'), blank=True)
    attachment = models.FileField(_('attachment'), upload_to='education_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Education')
        verbose_name_plural = _('Educations')
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.degree} at {self.institution}"


class Experience(models.Model):
    """Experience model"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    company = models.CharField(_('company'), max_length=255)
    position = models.CharField(_('position'), max_length=255)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Experience')
        verbose_name_plural = _('Experiences')
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.position} at {self.company}"


class LeaveType(models.Model):
    """Leave type model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    requires_approval = models.BooleanField(_('requires approval'), default=True)
    paid = models.BooleanField(_('paid'), default=True)
    days_allowed = models.IntegerField(
        _('days allowed'),
        null=True,
        blank=True,
        help_text=_('Number of days allowed per year, leave empty for unlimited')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Leave(models.Model):
    """Leave model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    total_days = models.DecimalField(
        _('total days'),
        max_digits=5,
        decimal_places=1,
        default=0
    )
    reason = models.TextField(_('reason'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    rejection_reason = models.TextField(_('rejection reason'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        # Calculate total days
        if self.start_date and self.end_date:
            from datetime import timedelta
            start = self.start_date
            end = self.end_date
            
            # Calculate business days (excluding weekends)
            days = 0
            current = start
            while current <= end:
                if current.weekday() < 5:  # Monday to Friday
                    days += 1
                current += timedelta(days=1)
            
            self.total_days = days
        
        super().save(*args, **kwargs)


class LeaveBalance(models.Model):
    """Leave balance model"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    year = models.IntegerField(_('year'))
    total_days = models.DecimalField(
        _('total days'),
        max_digits=5,
        decimal_places=1,
        default=0
    )
    used_days = models.DecimalField(
        _('used days'),
        max_digits=5,
        decimal_places=1,
        default=0
    )
    remaining_days = models.DecimalField(
        _('remaining days'),
        max_digits=5,
        decimal_places=1,
        default=0
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Leave Balance')
        verbose_name_plural = _('Leave Balances')
        unique_together = ('employee', 'leave_type', 'year')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.year}"
    
    def save(self, *args, **kwargs):
        # Calculate remaining days
        self.remaining_days = self.total_days - self.used_days
        super().save(*args, **kwargs)


class Benefit(models.Model):
    """Benefit model"""
    TYPE_CHOICES = (
        ('health_insurance', _('Health Insurance')),
        ('life_insurance', _('Life Insurance')),
        ('retirement_plan', _('Retirement Plan')),
        ('paid_time_off', _('Paid Time Off')),
        ('other', _('Other')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='benefits'
    )
    name = models.CharField(_('name'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    description = models.TextField(_('description'), blank=True)
    provider = models.CharField(_('provider'), max_length=255, blank=True)
    policy_number = models.CharField(_('policy number'), max_length=100, blank=True)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    premium_amount = models.DecimalField(
        _('premium amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    premium_frequency = models.CharField(
        _('premium frequency'),
        max_length=20,
        blank=True,
        help_text=_('e.g., monthly, quarterly, annually')
    )
    employee_contribution = models.DecimalField(
        _('employee contribution'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    employer_contribution = models.DecimalField(
        _('employer contribution'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    attachment = models.FileField(_('attachment'), upload_to='benefit_attachments/', blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Benefit')
        verbose_name_plural = _('Benefits')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.name}"


class Training(models.Model):
    """Training model"""
    STATUS_CHOICES = (
        ('planned', _('Planned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    location = models.CharField(_('location'), max_length=255, blank=True)
    provider = models.CharField(_('provider'), max_length=255, blank=True)
    cost = models.DecimalField(
        _('cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    max_participants = models.IntegerField(
        _('max participants'),
        null=True,
        blank=True
    )
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_trainings'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Training')
        verbose_name_plural = _('Trainings')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class TrainingParticipant(models.Model):
    """Training participant model"""
    STATUS_CHOICES = (
        ('invited', _('Invited')),
        ('confirmed', _('Confirmed')),
        ('attended', _('Attended')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='trainings'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited'
    )
    feedback = models.TextField(_('feedback'), blank=True)
    rating = models.IntegerField(
        _('rating'),
        null=True,
        blank=True,
        help_text=_('Rating from 1 to 5')
    )
    certificate_issued = models.BooleanField(_('certificate issued'), default=False)
    certificate_date = models.DateField(_('certificate date'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Training Participant')
        verbose_name_plural = _('Training Participants')
        unique_together = ('training', 'employee')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.training.name}"


class PerformanceReview(models.Model):
    """Performance review model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    RATING_CHOICES = (
        (1, _('Unsatisfactory')),
        (2, _('Needs Improvement')),
        (3, _('Meets Expectations')),
        (4, _('Exceeds Expectations')),
        (5, _('Outstanding')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    reviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_reviews'
    )
    title = models.CharField(_('title'), max_length=255)
    review_period_start = models.DateField(_('review period start'))
    review_period_end = models.DateField(_('review period end'))
    review_date = models.DateField(_('review date'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    overall_rating = models.IntegerField(
        _('overall rating'),
        choices=RATING_CHOICES,
        null=True,
        blank=True
    )
    strengths = models.TextField(_('strengths'), blank=True)
    areas_for_improvement = models.TextField(_('areas for improvement'), blank=True)
    goals = models.TextField(_('goals'), blank=True)
    comments = models.TextField(_('comments'), blank=True)
    employee_comments = models.TextField(_('employee comments'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Performance Review')
        verbose_name_plural = _('Performance Reviews')
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"


class PerformanceGoal(models.Model):
    """Performance goal model"""
    STATUS_CHOICES = (
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
        ('cancelled', _('Cancelled')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_goals'
    )
    performance_review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name='goals',
        null=True,
        blank=True
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    start_date = models.DateField(_('start date'), null=True, blank=True)
    target_date = models.DateField(_('target date'), null=True, blank=True)
    completion_date = models.DateField(_('completion date'), null=True, blank=True)
    progress = models.IntegerField(
        _('progress'),
        default=0,
        help_text=_('Progress percentage (0-100)')
    )
    weight = models.IntegerField(
        _('weight'),
        default=100,
        help_text=_('Weight percentage (0-100)')
    )
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Performance Goal')
        verbose_name_plural = _('Performance Goals')
        ordering = ['target_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"


class Document(models.Model):
    """Document model"""
    TYPE_CHOICES = (
        ('resume', _('Resume')),
        ('id_card', _('ID Card')),
        ('passport', _('Passport')),
        ('visa', _('Visa')),
        ('work_permit', _('Work Permit')),
        ('contract', _('Contract')),
        ('certificate', _('Certificate')),
        ('other', _('Other')),
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(_('title'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    file = models.FileField(_('file'), upload_to='employee_documents/')
    description = models.TextField(_('description'), blank=True)
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    is_confidential = models.BooleanField(_('is confidential'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()