from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.permissions import HasRolePermission
from .models import (
    ServiceTicket, TicketComment, TicketAttachment, TicketTimeLog,
    RMA, ServiceCall, ServicePlan, SLA, Region, Zone, Skill, TechnicianSkill
)
from .serializers import (
    ServiceTicketSerializer, ServiceTicketDetailSerializer, TicketCommentSerializer,
    TicketAttachmentSerializer, TicketTimeLogSerializer, RMASerializer, ServiceCallSerializer,
    ServicePlanSerializer, SLASerializer, RegionSerializer, ZoneSerializer, SkillSerializer,
    TechnicianSkillSerializer
)


class ServiceTicketViewSet(viewsets.ModelViewSet):
    """Service ticket viewset"""
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_service_tickets'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServiceTicketDetailSerializer
        return ServiceTicketSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to a user"""
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'detail': _('User ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from core.models import User
            user = User.objects.get(id=user_id)
            ticket.assigned_to = user
            ticket.save()
            
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': _('User not found')},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change ticket status"""
        ticket = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'detail': _('Status is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(ServiceTicket.STATUS_CHOICES):
            return Response(
                {'detail': _('Invalid status')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = new_status
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_time_log(self, request, pk=None):
        """Add time log to ticket"""
        ticket = self.get_object()
        
        # Get time log data
        hours = request.data.get('hours')
        date = request.data.get('date')
        description = request.data.get('description', '')
        
        if not hours or not date:
            return Response(
                {'detail': _('Hours and date are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create time log
        time_log = TicketTimeLog.objects.create(
            ticket=ticket,
            user=request.user,
            hours=hours,
            date=date,
            description=description
        )
        
        serializer = TicketTimeLogSerializer(time_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def create_rma(self, request, pk=None):
        """Create RMA for ticket"""
        ticket = self.get_object()
        
        # Get RMA data
        product_name = request.data.get('product_name')
        serial_number = request.data.get('serial_number', '')
        reason = request.data.get('reason')
        notes = request.data.get('notes', '')
        
        if not product_name or not reason:
            return Response(
                {'detail': _('Product name and reason are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate RMA number
        rma_number = f"RMA-{timezone.now().strftime('%Y%m%d')}-{ticket.id}"
        
        # Create RMA
        rma = RMA.objects.create(
            ticket=ticket,
            rma_number=rma_number,
            product_name=product_name,
            serial_number=serial_number,
            reason=reason,
            notes=notes,
            created_by=request.user
        )
        
        serializer = RMASerializer(rma)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def schedule_service_call(self, request, pk=None):
        """Schedule service call for ticket"""
        ticket = self.get_object()
        
        # Get service call data
        title = request.data.get('title')
        scheduled_date = request.data.get('scheduled_date')
        duration = request.data.get('duration')
        technician_id = request.data.get('technician_id')
        address = request.data.get('address')
        notes = request.data.get('notes', '')
        
        if not title or not scheduled_date or not address:
            return Response(
                {'detail': _('Title, scheduled date, and address are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create service call
        service_call = ServiceCall.objects.create(
            ticket=ticket,
            title=title,
            scheduled_date=scheduled_date,
            duration=duration,
            technician_id=technician_id,
            address=address,
            notes=notes,
            created_by=request.user
        )
        
        serializer = ServiceCallSerializer(service_call)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """Ticket comment viewset"""
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TicketAttachmentViewSet(viewsets.ModelViewSet):
    """Ticket attachment viewset"""
    queryset = TicketAttachment.objects.all()
    serializer_class = TicketAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class TicketTimeLogViewSet(viewsets.ModelViewSet):
    """Ticket time log viewset"""
    queryset = TicketTimeLog.objects.all()
    serializer_class = TicketTimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RMAViewSet(viewsets.ModelViewSet):
    """RMA viewset"""
    queryset = RMA.objects.all()
    serializer_class = RMASerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_rmas'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change RMA status"""
        rma = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'detail': _('Status is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(RMA.STATUS_CHOICES):
            return Response(
                {'detail': _('Invalid status')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rma.status = new_status
        rma.save()
        
        serializer = self.get_serializer(rma)
        return Response(serializer.data)


class ServiceCallViewSet(viewsets.ModelViewSet):
    """Service call viewset"""
    queryset = ServiceCall.objects.all()
    serializer_class = ServiceCallSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_service_calls'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change service call status"""
        service_call = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'detail': _('Status is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(ServiceCall.STATUS_CHOICES):
            return Response(
                {'detail': _('Invalid status')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service_call.status = new_status
        service_call.save()
        
        serializer = self.get_serializer(service_call)
        return Response(serializer.data)


class ServicePlanViewSet(viewsets.ModelViewSet):
    """Service plan viewset"""
    queryset = ServicePlan.objects.all()
    serializer_class = ServicePlanSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_service_plans'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get service plans expiring soon"""
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now().date()
        to_date = from_date + timezone.timedelta(days=days)
        
        plans = ServicePlan.objects.filter(
            end_date__gte=from_date,
            end_date__lte=to_date,
            status='active'
        )
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)


class SLAViewSet(viewsets.ModelViewSet):
    """SLA viewset"""
    queryset = SLA.objects.all()
    serializer_class = SLASerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_slas'


class RegionViewSet(viewsets.ModelViewSet):
    """Region viewset"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_regions'


class ZoneViewSet(viewsets.ModelViewSet):
    """Zone viewset"""
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_zones'


class SkillViewSet(viewsets.ModelViewSet):
    """Skill viewset"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_skills'


class TechnicianSkillViewSet(viewsets.ModelViewSet):
    """Technician skill viewset"""
    queryset = TechnicianSkill.objects.all()
    serializer_class = TechnicianSkillSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_technician_skills'
    
    @action(detail=False, methods=['get'])
    def find_technicians(self, request):
        """Find technicians with required skills"""
        skill_ids = request.query_params.get('skill_ids', '').split(',')
        skill_ids = [int(skill_id) for skill_id in skill_ids if skill_id.isdigit()]
        
        if not skill_ids:
            return Response(
                {'detail': _('Skill IDs are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find technicians with all required skills
        from core.models import User
        technicians = User.objects.filter(
            skills__skill_id__in=skill_ids
        ).distinct()
        
        # Filter by proficiency level if specified
        min_proficiency = request.query_params.get('min_proficiency')
        if min_proficiency and min_proficiency.isdigit():
            min_proficiency = int(min_proficiency)
            technicians = technicians.filter(
                skills__proficiency_level__gte=min_proficiency
            )
        
        # Filter by certification if specified
        certified_only = request.query_params.get('certified_only', 'false').lower() == 'true'
        if certified_only:
            technicians = technicians.filter(skills__certified=True)
        
        serializer = UserSerializer(technicians, many=True)
        return Response(serializer.data)