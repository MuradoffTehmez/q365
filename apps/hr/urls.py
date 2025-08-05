from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, SkillViewSet, EmployeeSkillViewSet, CertificationViewSet,
    EducationViewSet, ExperienceViewSet, LeaveTypeViewSet, LeaveViewSet, LeaveBalanceViewSet,
    BenefitViewSet, TrainingViewSet, TrainingParticipantViewSet, PerformanceReviewViewSet,
    PerformanceGoalViewSet, DocumentViewSet
)

router = DefaultRouter()
router.register('employees', EmployeeViewSet)
router.register('skills', SkillViewSet)
router.register('employee-skills', EmployeeSkillViewSet)
router.register('certifications', CertificationViewSet)
router.register('educations', EducationViewSet)
router.register('experiences', ExperienceViewSet)
router.register('leave-types', LeaveTypeViewSet)
router.register('leaves', LeaveViewSet)
router.register('leave-balances', LeaveBalanceViewSet)
router.register('benefits', BenefitViewSet)
router.register('trainings', TrainingViewSet)
router.register('training-participants', TrainingParticipantViewSet)
router.register('performance-reviews', PerformanceReviewViewSet)
router.register('performance-goals', PerformanceGoalViewSet)
router.register('documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]