from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from core.permissions import HasRolePermission
from .models import (
    Account, JournalEntry, JournalEntryLine, Transaction, Invoice, InvoiceLine,
    Payment, Expense, ExpenseCategory, Budget, BankAccount, Tax
)
from .serializers import (
    AccountSerializer, JournalEntrySerializer, JournalEntryDetailSerializer, JournalEntryLineSerializer,
    TransactionSerializer, InvoiceSerializer, InvoiceDetailSerializer, InvoiceLineSerializer,
    PaymentSerializer, ExpenseSerializer, ExpenseCategorySerializer, BudgetSerializer,
    BankAccountSerializer, TaxSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    """Account viewset"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_accounts'
    
    @action(detail=False, methods=['get'])
    def chart_of_accounts(self, request):
        """Get chart of accounts"""
        accounts = Account.objects.filter(parent=None)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)


class JournalEntryViewSet(viewsets.ModelViewSet):
    """Journal entry viewset"""
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_journal_entries'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JournalEntryDetailSerializer
        return JournalEntrySerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Post journal entry"""
        journal_entry = self.get_object()
        
        # Check if journal entry is balanced
        if not journal_entry.is_balanced():
            return Response(
                {'detail': _('Journal entry is not balanced')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        journal_entry.status = 'posted'
        journal_entry.posted_by = request.user
        journal_entry.posted_at = timezone.now()
        journal_entry.save()
        
        serializer = self.get_serializer(journal_entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel journal entry"""
        journal_entry = self.get_object()
        
        # Check if journal entry is posted
        if journal_entry.status == 'posted':
            return Response(
                {'detail': _('Cannot cancel a posted journal entry')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        journal_entry.status = 'cancelled'
        journal_entry.save()
        
        serializer = self.get_serializer(journal_entry)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Transaction viewset (read-only)"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_transactions'


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice viewset"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_invoices'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send invoice to customer"""
        invoice = self.get_object()
        
        # Update status
        if invoice.status == 'draft':
            invoice.status = 'sent'
            invoice.save()
        
        # Here you would implement the actual email sending logic
        # For now, just update the status
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record payment for invoice"""
        invoice = self.get_object()
        
        # Get payment data
        amount = request.data.get('amount')
        date = request.data.get('date')
        method = request.data.get('method')
        reference = request.data.get('reference', '')
        notes = request.data.get('notes', '')
        
        if not amount or not date or not method:
            return Response(
                {'detail': _('Amount, date, and method are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment
        payment = Payment.objects.create(
            date=date,
            amount=amount,
            method=method,
            reference=reference,
            notes=notes,
            customer=invoice.customer,
            invoice=invoice,
            created_by=request.user
        )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def create_journal_entry(self, request, pk=None):
        """Create journal entry for invoice"""
        invoice = self.get_object()
        
        # Check if journal entry already exists
        if invoice.journal_entry:
            return Response(
                {'detail': _('Journal entry already exists for this invoice')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get accounts
        try:
            if invoice.type == 'sales':
                receivable_account = Account.objects.get(code='1200')  # Accounts Receivable
                revenue_account = Account.objects.get(code='4000')     # Sales Revenue
                tax_account = Account.objects.get(code='2200')        # Sales Tax Payable
            else:
                payable_account = Account.objects.get(code='2000')    # Accounts Payable
                expense_account = Account.objects.get(code='5000')    # Purchases
                tax_account = Account.objects.get(code='2200')        # Sales Tax Payable
        except Account.DoesNotExist:
            return Response(
                {'detail': _('Required accounts not found')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                date=invoice.date,
                description=f"Invoice {invoice.number}",
                status='draft',
                created_by=request.user
            )
            
            # Create journal entry lines
            if invoice.type == 'sales':
                # Debit: Accounts Receivable
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=receivable_account,
                    description=f"Invoice {invoice.number}",
                    debit=invoice.total,
                    credit=0
                )
                
                # Credit: Sales Revenue
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=revenue_account,
                    description=f"Invoice {invoice.number}",
                    debit=0,
                    credit=invoice.subtotal
                )
                
                # Credit: Sales Tax Payable
                if invoice.tax_amount > 0:
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=tax_account,
                        description=f"Invoice {invoice.number} - Tax",
                        debit=0,
                        credit=invoice.tax_amount
                    )
            else:
                # Debit: Purchases
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=expense_account,
                    description=f"Invoice {invoice.number}",
                    debit=invoice.subtotal,
                    credit=0
                )
                
                # Debit: Sales Tax Payable
                if invoice.tax_amount > 0:
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=tax_account,
                        description=f"Invoice {invoice.number} - Tax",
                        debit=invoice.tax_amount,
                        credit=0
                    )
                
                # Credit: Accounts Payable
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=payable_account,
                    description=f"Invoice {invoice.number}",
                    debit=0,
                    credit=invoice.total
                )
            
            # Calculate totals
            total_debit = sum(line.debit for line in journal_entry.lines.all())
            total_credit = sum(line.credit for line in journal_entry.lines.all())
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()
            
            # Link journal entry to invoice
            invoice.journal_entry = journal_entry
            invoice.save()
        
        serializer = JournalEntrySerializer(journal_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment viewset"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_payments'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete payment"""
        payment = self.get_object()
        
        # Update status
        payment.status = 'completed'
        payment.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_journal_entry(self, request, pk=None):
        """Create journal entry for payment"""
        payment = self.get_object()
        
        # Check if journal entry already exists
        if payment.journal_entry:
            return Response(
                {'detail': _('Journal entry already exists for this payment')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get accounts
        try:
            bank_account = BankAccount.objects.get(id=request.data.get('bank_account_id'))
            receivable_account = Account.objects.get(code='1200')  # Accounts Receivable
        except (BankAccount.DoesNotExist, Account.DoesNotExist):
            return Response(
                {'detail': _('Required accounts not found')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                date=payment.date,
                description=f"Payment {payment.number}",
                status='draft',
                created_by=request.user
            )
            
            # Create journal entry lines
            # Debit: Bank Account
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=bank_account.account,
                description=f"Payment {payment.number}",
                debit=payment.amount,
                credit=0
            )
            
            # Credit: Accounts Receivable
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=receivable_account,
                description=f"Payment {payment.number}",
                debit=0,
                credit=payment.amount
            )
            
            # Calculate totals
            total_debit = sum(line.debit for line in journal_entry.lines.all())
            total_credit = sum(line.credit for line in journal_entry.lines.all())
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()
            
            # Link journal entry to payment
            payment.journal_entry = journal_entry
            payment.save()
        
        serializer = JournalEntrySerializer(journal_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense viewset"""
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_expenses'
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit expense for approval"""
        expense = self.get_object()
        
        # Update status
        expense.status = 'submitted'
        expense.save()
        
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve expense"""
        expense = self.get_object()
        
        # Update status
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.save()
        
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject expense"""
        expense = self.get_object()
        
        # Update status
        expense.status = 'rejected'
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.save()
        
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark expense as paid"""
        expense = self.get_object()
        
        # Update status
        expense.status = 'paid'
        expense.save()
        
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_journal_entry(self, request, pk=None):
        """Create journal entry for expense"""
        expense = self.get_object()
        
        # Check if journal entry already exists
        if expense.journal_entry:
            return Response(
                {'detail': _('Journal entry already exists for this expense')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get accounts
        try:
            expense_account = expense.category.account
            bank_account = BankAccount.objects.get(id=request.data.get('bank_account_id'))
        except BankAccount.DoesNotExist:
            return Response(
                {'detail': _('Bank account not found')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                date=expense.date,
                description=f"Expense {expense.number}",
                status='draft',
                created_by=request.user
            )
            
            # Create journal entry lines
            # Debit: Expense Account
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=expense_account,
                description=f"Expense {expense.number}",
                debit=expense.amount,
                credit=0
            )
            
            # Credit: Bank Account
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=bank_account.account,
                description=f"Expense {expense.number}",
                debit=0,
                credit=expense.amount
            )
            
            # Calculate totals
            total_debit = sum(line.debit for line in journal_entry.lines.all())
            total_credit = sum(line.credit for line in journal_entry.lines.all())
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()
            
            # Link journal entry to expense
            expense.journal_entry = journal_entry
            expense.save()
        
        serializer = JournalEntrySerializer(journal_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """Expense category viewset"""
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_expense_categories'


class BudgetViewSet(viewsets.ModelViewSet):
    """Budget viewset"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_budgets'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active budgets"""
        today = timezone.now().date()
        budgets = Budget.objects.filter(
            status='active',
            start_date__lte=today,
            end_date__gte=today
        )
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)


class BankAccountViewSet(viewsets.ModelViewSet):
    """Bank account viewset"""
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_bank_accounts'


class TaxViewSet(viewsets.ModelViewSet):
    """Tax viewset"""
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_taxes'