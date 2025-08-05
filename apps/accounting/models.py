from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal
from core.models import User, Organization

class Account(models.Model):
    """Account model for chart of accounts"""
    TYPE_CHOICES = (
        ('asset', _('Asset')),
        ('liability', _('Liability')),
        ('equity', _('Equity')),
        ('revenue', _('Revenue')),
        ('expense', _('Expense')),
    )
    
    code = models.CharField(_('code'), max_length=20)
    name = models.CharField(_('name'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        ordering = ['code']
        unique_together = ('code', 'parent')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_code(self):
        """Get full account code including parent codes"""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code
    
    @property
    def full_name(self):
        """Get full account name including parent names"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name


class JournalEntry(models.Model):
    """Journal entry model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('posted', _('Posted')),
        ('cancelled', _('Cancelled')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    total_debit = models.DecimalField(
        _('total debit'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_credit = models.DecimalField(
        _('total credit'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_journal_entries'
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_journal_entries'
    )
    posted_at = models.DateTimeField(_('posted at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Journal Entry')
        verbose_name_plural = _('Journal Entries')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Generate journal entry number if not provided
        if not self.number:
            last_entry = JournalEntry.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_entry and last_entry.number.startswith(f"JE-{self.date.year}-"):
                try:
                    last_number = int(last_entry.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"JE-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)
    
    def is_balanced(self):
        """Check if journal entry is balanced (debit = credit)"""
        return self.total_debit == self.total_credit


class JournalEntryLine(models.Model):
    """Journal entry line model"""
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='journal_entry_lines'
    )
    description = models.CharField(_('description'), max_length=255, blank=True)
    debit = models.DecimalField(
        _('debit'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    credit = models.DecimalField(
        _('credit'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = _('Journal Entry Line')
        verbose_name_plural = _('Journal Entry Lines')
    
    def __str__(self):
        return f"{self.journal_entry.number} - {self.account.full_code} {self.account.name}"


class Transaction(models.Model):
    """Transaction model"""
    TYPE_CHOICES = (
        ('invoice', _('Invoice')),
        ('payment', _('Payment')),
        ('expense', _('Expense')),
        ('journal_entry', _('Journal Entry')),
        ('other', _('Other')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    description = models.TextField(_('description'), blank=True)
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2
    )
    reference = models.CharField(_('reference'), max_length=255, blank=True)
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.date} - {self.amount}"


class Invoice(models.Model):
    """Invoice model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    )
    
    TYPE_CHOICES = (
        ('sales', _('Sales')),
        ('purchase', _('Purchase')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='sales'
    )
    date = models.DateField(_('date'))
    due_date = models.DateField(_('due date'))
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
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
    paid_amount = models.DecimalField(
        _('paid amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_invoices'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        # Calculate tax amount and total
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount
        
        # Update status based on paid amount
        if self.paid_amount <= 0:
            self.status = 'draft'
        elif self.paid_amount >= self.total:
            self.status = 'paid'
        else:
            self.status = 'partially_paid'
        
        # Check if invoice is overdue
        if self.status in ['sent', 'partially_paid'] and self.due_date < timezone.now().date():
            self.status = 'overdue'
        
        # Generate invoice number if not provided
        if not self.number:
            last_invoice = Invoice.objects.filter(
                date__year=self.date.year,
                type=self.type
            ).order_by('-number').first()
            
            prefix = 'INV' if self.type == 'sales' else 'PUR'
            
            if last_invoice and last_invoice.number.startswith(f"{prefix}-{self.date.year}-"):
                try:
                    last_number = int(last_invoice.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"{prefix}-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)
    
    @property
    def remaining_amount(self):
        """Get remaining amount to be paid"""
        return self.total - self.paid_amount


class InvoiceLine(models.Model):
    """Invoice line model"""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    description = models.CharField(_('description'), max_length=255)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=15, decimal_places=2)
    discount = models.DecimalField(_('discount'), max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=15, decimal_places=2, default=0)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('Invoice Line')
        verbose_name_plural = _('Invoice Lines')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.description}"
    
    def save(self, *args, **kwargs):
        # Calculate total with discount and tax
        discount_amount = self.unit_price * (self.discount / 100)
        discounted_price = self.unit_price - discount_amount
        line_total = self.quantity * discounted_price
        tax_amount = line_total * (self.tax_rate / 100)
        self.total = line_total + tax_amount
        
        super().save(*args, **kwargs)
        
        # Update invoice subtotal
        invoice = self.invoice
        subtotal = sum(line.total for line in invoice.lines.all())
        invoice.subtotal = subtotal
        invoice.save()


class Payment(models.Model):
    """Payment model"""
    METHOD_CHOICES = (
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('other', _('Other')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2
    )
    method = models.CharField(
        _('method'),
        max_length=20,
        choices=METHOD_CHOICES
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reference = models.CharField(_('reference'), max_length=255, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_payments'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer.name} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Generate payment number if not provided
        if not self.number:
            last_payment = Payment.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_payment and last_payment.number.startswith(f"PAY-{self.date.year}-"):
                try:
                    last_number = int(last_payment.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"PAY-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)
        
        # Update invoice paid amount
        if self.status == 'completed':
            invoice = self.invoice
            total_paid = sum(
                payment.amount for payment in invoice.payments.filter(status='completed')
            )
            invoice.paid_amount = total_paid
            invoice.save()


class Expense(models.Model):
    """Expense model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    description = models.TextField(_('description'))
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    category = models.ForeignKey(
        'ExpenseCategory',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    vendor = models.CharField(_('vendor'), max_length=255, blank=True)
    receipt = models.FileField(_('receipt'), upload_to='expense_receipts/', blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_expenses'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses'
    )
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.description}"
    
    def save(self, *args, **kwargs):
        # Generate expense number if not provided
        if not self.number:
            last_expense = Expense.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_expense and last_expense.number.startswith(f"EXP-{self.date.year}-"):
                try:
                    last_number = int(last_expense.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"EXP-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    """Expense category model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='expense_categories'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Budget(models.Model):
    """Budget model"""
    PERIOD_CHOICES = (
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    )
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('closed', _('Closed')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    period = models.CharField(
        _('period'),
        max_length=20,
        choices=PERIOD_CHOICES
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2
    )
    actual_amount = models.DecimalField(
        _('actual amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_budgets'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.period}"
    
    @property
    def variance(self):
        """Get budget variance (actual - budgeted)"""
        return self.actual_amount - self.amount
    
    @property
    def variance_percentage(self):
        """Get budget variance percentage"""
        if self.amount == 0:
            return 0
        return (self.variance / self.amount) * 100


class BankAccount(models.Model):
    """Bank account model"""
    TYPE_CHOICES = (
        ('checking', _('Checking')),
        ('savings', _('Savings')),
        ('credit', _('Credit')),
        ('other', _('Other')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    account_number = models.CharField(_('account number'), max_length=50)
    bank_name = models.CharField(_('bank name'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    balance = models.DecimalField(
        _('balance'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    is_active = models.BooleanField(_('is active'), default=True)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.bank_name}"


class Tax(models.Model):
    """Tax model"""
    name = models.CharField(_('name'), max_length=100)
    rate = models.DecimalField(
        _('rate'),
        max_digits=5,
        decimal_places=2,
        help_text=_('Tax rate in percentage')
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='taxes'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tax')
        verbose_name_plural = _('Taxes')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.rate}%"