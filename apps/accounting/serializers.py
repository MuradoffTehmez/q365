from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer, OrganizationSerializer
from crm.serializers import CustomerSerializer
from .models import (
    Account, JournalEntry, JournalEntryLine, Transaction, Invoice, InvoiceLine,
    Payment, Expense, ExpenseCategory, Budget, BankAccount, Tax
)


class AccountSerializer(serializers.ModelSerializer):
    """Account serializer"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class JournalEntryLineSerializer(serializers.ModelSerializer):
    """Journal entry line serializer"""
    account_name = serializers.CharField(source='account.full_name', read_only=True)
    account_code = serializers.CharField(source='account.full_code', read_only=True)
    
    class Meta:
        model = JournalEntryLine
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    """Journal entry serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    lines_data = JournalEntryLineSerializer(source='lines', many=True, read_only=True)
    is_balanced = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ('created_by', 'posted_by', 'posted_at', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        journal_entry = JournalEntry.objects.create(**validated_data)
        
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=journal_entry, **line_data)
        
        # Calculate totals
        total_debit = sum(line.debit for line in journal_entry.lines.all())
        total_credit = sum(line.credit for line in journal_entry.lines.all())
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
        journal_entry.save()
        
        return journal_entry
    
    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', [])
        journal_entry = super().update(instance, validated_data)
        
        # Update lines
        journal_entry.lines.all().delete()
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=journal_entry, **line_data)
        
        # Calculate totals
        total_debit = sum(line.debit for line in journal_entry.lines.all())
        total_credit = sum(line.credit for line in journal_entry.lines.all())
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
        journal_entry.save()
        
        return journal_entry


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class InvoiceLineSerializer(serializers.ModelSerializer):
    """Invoice line serializer"""
    
    class Meta:
        model = InvoiceLine
        fields = '__all__'
        read_only_fields = ('total',)


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    lines_data = InvoiceLineSerializer(source='lines', many=True, read_only=True)
    payments_data = serializers.SerializerMethodField()
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'tax_amount', 'total', 'paid_amount')
    
    def get_payments_data(self, obj):
        """Get invoice payments"""
        from .models import Payment
        payments = Payment.objects.filter(invoice=obj)
        return PaymentSerializer(payments, many=True).data
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = Invoice.objects.create(**validated_data)
        
        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)
        
        # Calculate totals
        subtotal = sum(line.total for line in invoice.lines.all())
        invoice.subtotal = subtotal
        invoice.save()
        
        return invoice
    
    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', [])
        invoice = super().update(instance, validated_data)
        
        # Update lines
        invoice.lines.all().delete()
        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)
        
        # Calculate totals
        subtotal = sum(line.total for line in invoice.lines.all())
        invoice.subtotal = subtotal
        invoice.save()
        
        return invoice


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ExpenseSerializer(serializers.ModelSerializer):
    """Expense serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('submitted_by', 'approved_by', 'approved_at', 'created_at', 'updated_at')


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Expense category serializer"""
    account_name = serializers.CharField(source='account.full_name', read_only=True)
    
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BudgetSerializer(serializers.ModelSerializer):
    """Budget serializer"""
    account_name = serializers.CharField(source='account.full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    variance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    variance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'actual_amount')


class BankAccountSerializer(serializers.ModelSerializer):
    """Bank account serializer"""
    account_name = serializers.CharField(source='account.full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TaxSerializer(serializers.ModelSerializer):
    """Tax serializer"""
    account_name = serializers.CharField(source='account.full_name', read_only=True)
    
    class Meta:
        model = Tax
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class JournalEntryDetailSerializer(JournalEntrySerializer):
    """Journal entry detail serializer with related data"""
    transactions_data = TransactionSerializer(source='transactions', many=True, read_only=True)
    
    class Meta(JournalEntrySerializer.Meta):
        fields = JournalEntrySerializer.Meta.fields + ('transactions_data',)


class InvoiceDetailSerializer(InvoiceSerializer):
    """Invoice detail serializer with related data"""
    customer_data = CustomerSerializer(source='customer', read_only=True)
    
    class Meta(InvoiceSerializer.Meta):
        fields = InvoiceSerializer.Meta.fields + ('customer_data',)