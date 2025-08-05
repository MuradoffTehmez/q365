from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowViewSet, StateViewSet, TransitionViewSet, WorkflowInstanceViewSet,
    WorkflowHistoryViewSet, WorkflowTemplateViewSet, WorkflowTriggerViewSet,
    ScheduledWorkflowViewSet
)

router = DefaultRouter()
router.register('workflows', WorkflowViewSet)
router.register('states', StateViewSet)
router.register('transitions', TransitionViewSet)
router.register('workflow-instances', WorkflowInstanceViewSet)
router.register('workflow-history', WorkflowHistoryViewSet)
router.register('workflow-templates', WorkflowTemplateViewSet)
router.register('workflow-triggers', WorkflowTriggerViewSet)
router.register('scheduled-workflows', ScheduledWorkflowViewSet)

urlpatterns = [
    path('', include(router.urls)),
]