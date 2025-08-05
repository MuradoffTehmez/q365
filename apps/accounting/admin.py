from django.contrib import admin
from .models import (
    Account, JournalEntry, JournalEntryLine, Transaction, Invoice, InvoiceLine,
    Payment, Expense, ExpenseCategory, Budget, BankAccount, Tax
)

class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 1


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('full_code', 'name', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'description', 'status', 'total_debit', 'total_credit', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('number', 'description')
    inlines = [JournalEntryLineInline, TransactionInline]
    readonly_fields = ('created_by', 'posted_by', 'posted_at', 'created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'type', 'amount', 'reference', 'journal_entry', 'created_at')
    list_filter = ('type', 'date', 'created_at')
    search_fields = ('number', 'description', 'reference')
    readonly_fields = ('created_at', 'updated_at')


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'customer', 'type', 'status', 'total', 'paid_amount', 'remaining_amount', 'created_at')
    list_filter = ('type', 'status', 'date', 'created_at')
    search_fields = ('number', 'customer__company_name', 'customer__first_name', 'customer__last_name')
    inlines = [InvoiceLineInline, PaymentInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'tax_amount', 'total', 'paid_amount')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'customer', 'invoice', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'date', 'created_at')
    search_fields = ('number', 'reference', 'customer__company_name', 'invoice__number')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'description', 'category', 'amount', 'status', 'submitted_by', 'approved_by', 'created_at')
    list_filter = ('status', 'category', 'date', 'created_at')
    search_fields = ('number', 'description', 'vendor')
    readonly_fields = ('submitted_by', 'approved_by', 'approved_at', 'created_at', 'updated_at')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'start_date', 'end_date', 'account', 'amount', 'actual_amount', 'variance', 'status', 'created_at')
    list_filter = ('period', 'status', 'start_date', 'end_date', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'actual_amount')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'bank_name', 'account_number', 'type', 'currency', 'balance', 'is_active', 'created_at')
    list_filter = ('type', 'currency', 'is_active', 'created_at')
    search_fields = ('name', 'bank_name', 'account_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')