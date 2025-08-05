from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceTicketViewSet, TicketCommentViewSet, TicketAttachmentViewSet, TicketTimeLogViewSet,
    RMAViewSet, ServiceCallViewSet, ServicePlanViewSet, SLAViewSet, RegionViewSet, ZoneViewSet,
    SkillViewSet, TechnicianSkillViewSet
)

router = DefaultRouter()
router.register('service-tickets', ServiceTicketViewSet)
router.register('ticket-comments', TicketCommentViewSet)
router.register('ticket-attachments', TicketAttachmentViewSet)
router.register('ticket-time-logs', TicketTimeLogViewSet)
router.register('rmas', RMAViewSet)
router.register('service-calls', ServiceCallViewSet)
router.register('service-plans', ServicePlanViewSet)
router.register('slas', SLAViewSet)
router.register('regions', RegionViewSet)
router.register('zones', ZoneViewSet)
router.register('skills', SkillViewSet)
router.register('technician-skills', TechnicianSkillViewSet)

urlpatterns = [
    path('', include(router.urls)),
]