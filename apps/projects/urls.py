from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, TaskViewSet, ChecklistViewSet,
    TaskCommentViewSet, TaskAttachmentViewSet, TaskTimeLogViewSet
)

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('tasks', TaskViewSet)
router.register('checklists', ChecklistViewSet)
router.register('task-comments', TaskCommentViewSet)
router.register('task-attachments', TaskAttachmentViewSet)
router.register('task-time-logs', TaskTimeLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]