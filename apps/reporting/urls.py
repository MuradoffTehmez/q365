from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet, DashboardViewSet, DashboardWidgetViewSet, KPIViewSet, ScheduledReportViewSet
)

router = DefaultRouter()
router.register('reports', ReportViewSet)
router.register('dashboards', DashboardViewSet)
router.register('dashboard-widgets', DashboardWidgetViewSet)
router.register('kpis', KPIViewSet)
router.register('scheduled-reports', ScheduledReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]