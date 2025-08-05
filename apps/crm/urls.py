from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeadViewSet, CustomerViewSet, ContactViewSet, OpportunityViewSet,
    QuotationViewSet, QuotationItemViewSet, CampaignViewSet, EmailTemplateViewSet,
    EmailCampaignViewSet, SalesActivityViewSet, CommissionViewSet
)

router = DefaultRouter()
router.register('leads', LeadViewSet)
router.register('customers', CustomerViewSet)
router.register('contacts', ContactViewSet)
router.register('opportunities', OpportunityViewSet)
router.register('quotations', QuotationViewSet)
router.register('quotation-items', QuotationItemViewSet)
router.register('campaigns', CampaignViewSet)
router.register('email-templates', EmailTemplateViewSet)
router.register('email-campaigns', EmailCampaignViewSet)
router.register('sales-activities', SalesActivityViewSet)
router.register('commissions', CommissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]