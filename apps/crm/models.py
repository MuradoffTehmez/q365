from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import User, Team

class Lead(models.Model):
    """Lead model for potential customers"""
    STATUS_CHOICES = (
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('qualified', _('Qualified')),
        ('unqualified', _('Unqualified')),
        ('converted', _('Converted')),
    )
    
    SOURCE_CHOICES = (
        ('website', _('Website')),
        ('referral', _('Referral')),
        ('advertisement', _('Advertisement')),
        ('social_media', _('Social Media')),
        ('other', _('Other')),
    )
    
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    company = models.CharField(_('company'), max_length=100, blank=True)
    position = models.CharField(_('position'), max_length=100, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    source = models.CharField(
        _('source'),
        max_length=20,
        choices=SOURCE_CHOICES,
        default='website'
    )
    description = models.TextField(_('description'), blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_leads'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Customer(models.Model):
    """Customer model"""
    TYPE_CHOICES = (
        ('individual', _('Individual')),
        ('company', _('Company')),
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='individual'
    )
    first_name = models.CharField(_('first name'), max_length=100, blank=True)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    company_name = models.CharField(_('company name'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    address = models.TextField(_('address'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_customers'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_customers'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-created_at']
    
    def __str__(self):
        if self.type == 'individual':
            return f"{self.first_name} {self.last_name}"
        return self.company_name
    
    @property
    def name(self):
        if self.type == 'individual':
            return f"{self.first_name} {self.last_name}"
        return self.company_name


class Contact(models.Model):
    """Contact model for customer contacts"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    position = models.CharField(_('position'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    is_primary = models.BooleanField(_('is primary'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.customer.name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Opportunity(models.Model):
    """Opportunity model"""
    STAGE_CHOICES = (
        ('qualification', _('Qualification')),
        ('needs_analysis', _('Needs Analysis')),
        ('proposal', _('Proposal')),
        ('negotiation', _('Negotiation')),
        ('closed_won', _('Closed Won')),
        ('closed_lost', _('Closed Lost')),
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    stage = models.CharField(
        _('stage'),
        max_length=20,
        choices=STAGE_CHOICES,
        default='qualification'
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    probability = models.IntegerField(
        _('probability'),
        default=50,
        help_text=_('Probability percentage (0-100)')
    )
    expected_close_date = models.DateField(_('expected close date'), null=True, blank=True)
    actual_close_date = models.DateField(_('actual close date'), null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_opportunities'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_opportunities'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Opportunity')
        verbose_name_plural = _('Opportunities')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"


class Quotation(models.Model):
    """Quotation model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    )
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='quotations',
        null=True,
        blank=True
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    valid_until = models.DateField(_('valid until'), null=True, blank=True)
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_rate = models.DecimalField(
        _('tax rate'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_quotations'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_quotations'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Quotation')
        verbose_name_plural = _('Quotations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        # Calculate tax amount and total
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    """Quotation item model"""
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(_('product name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=15, decimal_places=2)
    discount = models.DecimalField(_('discount'), max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=15, decimal_places=2, default=0)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('Quotation Item')
        verbose_name_plural = _('Quotation Items')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product_name} - {self.quotation.title}"
    
    def save(self, *args, **kwargs):
        # Calculate total with discount
        discount_amount = self.unit_price * (self.discount / 100)
        discounted_price = self.unit_price - discount_amount
        self.total = self.quantity * discounted_price
        super().save(*args, **kwargs)
        
        # Update quotation subtotal
        quotation = self.quotation
        subtotal = sum(item.total for item in quotation.items.all())
        quotation.subtotal = subtotal
        quotation.save()


class Campaign(models.Model):
    """Campaign model"""
    STATUS_CHOICES = (
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    TYPE_CHOICES = (
        ('email', _('Email')),
        ('social_media', _('Social Media')),
        ('event', _('Event')),
        ('advertisement', _('Advertisement')),
        ('other', _('Other')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='email'
    )
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    budget = models.DecimalField(
        _('budget'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_cost = models.DecimalField(
        _('actual cost'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_campaigns'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_campaigns'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """Email template model"""
    name = models.CharField(_('name'), max_length=255)
    subject = models.CharField(_('subject'), max_length=255)
    content = models.TextField(_('content'))
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_email_templates'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class EmailCampaign(models.Model):
    """Email campaign model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    )
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='email_campaigns'
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
        related_name='email_campaigns'
    )
    name = models.CharField(_('name'), max_length=255)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    scheduled_at = models.DateTimeField(_('scheduled at'), null=True, blank=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    recipients = models.ManyToManyField(
        Customer,
        related_name='email_campaigns'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_email_campaigns'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Email Campaign')
        verbose_name_plural = _('Email Campaigns')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class SalesActivity(models.Model):
    """Sales activity model"""
    TYPE_CHOICES = (
        ('call', _('Call')),
        ('email', _('Email')),
        ('meeting', _('Meeting')),
        ('task', _('Task')),
        ('other', _('Other')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    STATUS_CHOICES = (
        ('planned', _('Planned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    subject = models.CharField(_('subject'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    due_date = models.DateTimeField(_('due date'), null=True, blank=True)
    completed_date = models.DateTimeField(_('completed date'), null=True, blank=True)
    duration = models.DurationField(_('duration'), null=True, blank=True)
    
    # Relations
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sales_activities',
        null=True,
        blank=True
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='sales_activities',
        null=True,
        blank=True
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='sales_activities',
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_sales_activities'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_sales_activities'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sales Activity')
        verbose_name_plural = _('Sales Activities')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.assigned_to.get_full_name() if self.assigned_to else 'Unassigned'}"


class Commission(models.Model):
    """Commission model"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2
    )
    percentage = models.DecimalField(
        _('percentage'),
        max_digits=5,
        decimal_places=2,
        help_text=_('Commission percentage')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    paid_date = models.DateField(_('paid date'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_commissions'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.opportunity.name} - {self.amount}"