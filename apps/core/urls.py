from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RoleViewSet, PermissionViewSet, UserRoleViewSet,
    OrganizationViewSet, DepartmentViewSet, SectorViewSet, TeamViewSet,
    NotificationViewSet, ReminderViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('roles', RoleViewSet)
router.register('permissions', PermissionViewSet)
router.register('user-roles', UserRoleViewSet)
router.register('organizations', OrganizationViewSet)
router.register('departments', DepartmentViewSet)
router.register('sectors', SectorViewSet)
router.register('teams', TeamViewSet)
router.register('notifications', NotificationViewSet)
router.register('reminders', ReminderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]