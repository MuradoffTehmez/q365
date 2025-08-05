from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, JournalEntryViewSet, TransactionViewSet, InvoiceViewSet,
    PaymentViewSet, ExpenseViewSet, ExpenseCategoryViewSet, BudgetViewSet,
    BankAccountViewSet, TaxViewSet
)

router = DefaultRouter()
router.register('accounts', AccountViewSet)
router.register('journal-entries', JournalEntryViewSet)
router.register('transactions', TransactionViewSet)
router.register('invoices', InvoiceViewSet)
router.register('payments', PaymentViewSet)
router.register('expenses', ExpenseViewSet)
router.register('expense-categories', ExpenseCategoryViewSet)
router.register('budgets', BudgetViewSet)
router.register('bank-accounts', BankAccountViewSet)
router.register('taxes', TaxViewSet)

urlpatterns = [
    path('', include(router.urls)),
]