from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from core.permissions import HasRolePermission
from .models import (
    Employee, Skill, EmployeeSkill, Certification, Education, Experience,
    LeaveType, Leave, LeaveBalance, Benefit, Training, TrainingParticipant,
    PerformanceReview, PerformanceGoal, Document
)
from .serializers import (
    EmployeeSerializer, EmployeeDetailSerializer, SkillSerializer, EmployeeSkillSerializer,
    CertificationSerializer, EducationSerializer, ExperienceSerializer, LeaveTypeSerializer,
    LeaveSerializer, LeaveBalanceSerializer, BenefitSerializer, TrainingSerializer, TrainingDetailSerializer,
    TrainingParticipantSerializer, PerformanceReviewSerializer, PerformanceGoalSerializer, DocumentSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """Employee viewset"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_employees'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate employee"""
        employee = self.get_object()
        
        # Get termination date
        termination_date = request.data.get('termination_date')
        if not termination_date:
            return Response(
                {'detail': _('Termination date is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update employee status and termination date
        employee.status = 'terminated'
        employee.termination_date = termination_date
        employee.save()
        
        # Deactivate user account
        if employee.user:
            employee.user.is_active = False
            employee.user.save()
        
        serializer = self.get_serializer(employee)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_leave_balance(self, request, pk=None):
        """Update employee leave balance"""
        employee = self.get_object()
        
        # Get leave balance data
        leave_type_id = request.data.get('leave_type_id')
        year = request.data.get('year', timezone.now().year)
        total_days = request.data.get('total_days')
        used_days = request.data.get('used_days', 0)
        
        if not leave_type_id or total_days is None:
            return Response(
                {'detail': _('Leave type ID and total days are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id)
        except LeaveType.DoesNotExist:
            return Response(
                {'detail': _('Leave type not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create leave balance
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={
                'total_days': total_days,
                'used_days': used_days
            }
        )
        
        if not created:
            leave_balance.total_days = total_days
            leave_balance.used_days = used_days
            leave_balance.save()
        
        serializer = LeaveBalanceSerializer(leave_balance)
        return Response(serializer.data)


class SkillViewSet(viewsets.ModelViewSet):
    """Skill viewset"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_skills'


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    """Employee skill viewset"""
    queryset = EmployeeSkill.objects.all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_employee_skills'


class CertificationViewSet(viewsets.ModelViewSet):
    """Certification viewset"""
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_certifications'


class EducationViewSet(viewsets.ModelViewSet):
    """Education viewset"""
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_educations'


class ExperienceViewSet(viewsets.ModelViewSet):
    """Experience viewset"""
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_experiences'


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """Leave type viewset"""
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_leave_types'


class LeaveViewSet(viewsets.ModelViewSet):
    """Leave viewset"""
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_leaves'
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit leave for approval"""
        leave = self.get_object()
        
        # Update status
        if leave.status == 'draft':
            leave.status = 'pending'
            leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave"""
        leave = self.get_object()
        
        # Update status
        if leave.status == 'pending':
            leave.status = 'approved'
            leave.approved_by = request.user.employee
            leave.approved_at = timezone.now()
            leave.save()
            
            # Update leave balance
            try:
                leave_balance = LeaveBalance.objects.get(
                    employee=leave.employee,
                    leave_type=leave.leave_type,
                    year=leave.start_date.year
                )
                leave_balance.used_days += leave.total_days
                leave_balance.save()
            except LeaveBalance.DoesNotExist:
                pass
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave"""
        leave = self.get_object()
        
        # Get rejection reason
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Update status
        if leave.status == 'pending':
            leave.status = 'rejected'
            leave.approved_by = request.user.employee
            leave.approved_at = timezone.now()
            leave.rejection_reason = rejection_reason
            leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel leave"""
        leave = self.get_object()
        
        # Update status
        if leave.status in ['draft', 'pending']:
            leave.status = 'cancelled'
            leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)


class LeaveBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """Leave balance viewset (read-only)"""
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_leave_balances'
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Get current user's leave balance"""
        try:
            employee = request.user.employee
            year = request.query_params.get('year', timezone.now().year)
            
            balances = LeaveBalance.objects.filter(
                employee=employee,
                year=year
            )
            
            serializer = self.get_serializer(balances, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'detail': _('Employee profile not found')},
                status=status.HTTP_404_NOT_FOUND
            )


class BenefitViewSet(viewsets.ModelViewSet):
    """Benefit viewset"""
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_benefits'


class TrainingViewSet(viewsets.ModelViewSet):
    """Training viewset"""
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_trainings'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainingDetailSerializer
        return TrainingSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add participant to training"""
        training = self.get_object()
        
        # Get participant data
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response(
                {'detail': _('Employee ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'detail': _('Employee not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if employee is already a participant
        if TrainingParticipant.objects.filter(training=training, employee=employee).exists():
            return Response(
                {'detail': _('Employee is already a participant')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check max participants
        if training.max_participants:
            current_participants = TrainingParticipant.objects.filter(training=training).count()
            if current_participants >= training.max_participants:
                return Response(
                    {'detail': _('Training is full')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create participant
        participant = TrainingParticipant.objects.create(
            training=training,
            employee=employee
        )
        
        serializer = TrainingParticipantSerializer(participant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def update_participant_status(self, request, pk=None):
        """Update participant status"""
        training = self.get_object()
        
        # Get participant data
        participant_id = request.data.get('participant_id')
        status = request.data.get('status')
        
        if not participant_id or not status:
            return Response(
                {'detail': _('Participant ID and status are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            participant = TrainingParticipant.objects.get(id=participant_id, training=training)
        except TrainingParticipant.DoesNotExist:
            return Response(
                {'detail': _('Participant not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update status
        participant.status = status
        
        # Update additional fields based on status
        if status == 'completed':
            participant.certificate_issued = request.data.get('certificate_issued', False)
            if participant.certificate_issued:
                participant.certificate_date = timezone.now().date()
            
            feedback = request.data.get('feedback', '')
            if feedback:
                participant.feedback = feedback
            
            rating = request.data.get('rating')
            if rating is not None:
                participant.rating = rating
        
        participant.save()
        
        serializer = TrainingParticipantSerializer(participant)
        return Response(serializer.data)


class TrainingParticipantViewSet(viewsets.ModelViewSet):
    """Training participant viewset"""
    queryset = TrainingParticipant.objects.all()
    serializer_class = TrainingParticipantSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_trainings'


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    """Performance review viewset"""
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_performance_reviews'
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete performance review"""
        review = self.get_object()
        
        # Get review data
        overall_rating = request.data.get('overall_rating')
        strengths = request.data.get('strengths', '')
        areas_for_improvement = request.data.get('areas_for_improvement', '')
        goals = request.data.get('goals', '')
        comments = request.data.get('comments', '')
        
        if not overall_rating:
            return Response(
                {'detail': _('Overall rating is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update review
        review.status = 'completed'
        review.overall_rating = overall_rating
        review.strengths = strengths
        review.areas_for_improvement = areas_for_improvement
        review.goals = goals
        review.comments = comments
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)


class PerformanceGoalViewSet(viewsets.ModelViewSet):
    """Performance goal viewset"""
    queryset = PerformanceGoal.objects.all()
    serializer_class = PerformanceGoalSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_performance_goals'
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress"""
        goal = self.get_object()
        
        # Get progress data
        progress = request.data.get('progress')
        
        if progress is None:
            return Response(
                {'detail': _('Progress is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update progress
        goal.progress = progress
        
        # Update status based on progress
        if progress <= 0:
            goal.status = 'not_started'
        elif progress < 100:
            goal.status = 'in_progress'
        else:
            goal.status = 'completed'
            goal.completion_date = timezone.now().date()
        
        goal.save()
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """Document viewset"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_documents'
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get documents expiring soon"""
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now().date()
        to_date = from_date + timezone.timedelta(days=days)
        
        documents = Document.objects.filter(
            expiry_date__gte=from_date,
            expiry_date__lte=to_date
        )
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)