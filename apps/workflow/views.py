from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from core.permissions import HasRolePermission
from .models import (
    Workflow, State, Transition, WorkflowInstance, WorkflowHistory,
    WorkflowTemplate, WorkflowTrigger, ScheduledWorkflow
)
from .serializers import (
    WorkflowSerializer, StateSerializer, TransitionSerializer, WorkflowInstanceSerializer,
    WorkflowHistorySerializer, WorkflowTemplateSerializer, WorkflowTriggerSerializer,
    ScheduledWorkflowSerializer
)


class WorkflowViewSet(viewsets.ModelViewSet):
    """Workflow viewset"""
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_workflows'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone workflow"""
        workflow = self.get_object()
        
        # Get clone data
        name = request.data.get('name')
        description = request.data.get('description')
        
        # Clone workflow
        new_workflow = workflow.clone(name=name, description=description)
        
        serializer = self.get_serializer(new_workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate workflow"""
        workflow = self.get_object()
        workflow.status = 'active'
        workflow.save()
        
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate workflow"""
        workflow = self.get_object()
        workflow.status = 'inactive'
        workflow.save()
        
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start workflow for an object"""
        workflow = self.get_object()
        
        # Get object data
        content_type_id = request.data.get('content_type_id')
        object_id = request.data.get('object_id')
        data = request.data.get('data', {})
        
        if not content_type_id or not object_id:
            return Response(
                {'detail': _('Content type ID and object ID are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            obj = content_type.get_object_for_this_type(id=object_id)
        except ContentType.DoesNotExist:
            return Response(
                {'detail': _('Content type not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        except content_type.model_class().DoesNotExist:
            return Response(
                {'detail': _('Object not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create workflow instance
        instance, created = WorkflowInstance.objects.get_or_create(
            workflow=workflow,
            content_type=content_type,
            object_id=object_id,
            defaults={
                'started_by': request.user,
                'data': data
            }
        )
        
        # If it's a new instance, set the initial state
        if created:
            initial_state = workflow.get_initial_state()
            if initial_state:
                instance.current_state = initial_state
                instance.save()
        
        serializer = WorkflowInstanceSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class StateViewSet(viewsets.ModelViewSet):
    """State viewset"""
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_workflows'


class TransitionViewSet(viewsets.ModelViewSet):
    """Transition viewset"""
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_workflows'


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """Workflow instance viewset"""
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_workflow_instances'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, HasRolePermission]
            self.required_permission = 'manage_workflow_instances'
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition to a new state"""
        instance = self.get_object()
        
        # Get transition data
        transition_id = request.data.get('transition_id')
        notes = request.data.get('notes', '')
        
        if not transition_id:
            return Response(
                {'detail': _('Transition ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            transition = Transition.objects.get(id=transition_id)
        except Transition.DoesNotExist:
            return Response(
                {'detail': _('Transition not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if transition is available
        if transition not in instance.get_available_transitions():
            return Response(
                {'detail': _('Transition is not available from the current state')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform transition
        try:
            instance.transition_to(transition, request.user)
            
            # Update history notes
            history = instance.history.filter(
                transition=transition,
                triggered_by=request.user
            ).first()
            if history:
                history.notes = notes
                history.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel workflow instance"""
        instance = self.get_object()
        instance.status = 'cancelled'
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class WorkflowHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Workflow history viewset (read-only)"""
    queryset = WorkflowHistory.objects.all()
    serializer_class = WorkflowHistorySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_workflow_instances'


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """Workflow template viewset"""
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_workflow_templates'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_workflow(self, request, pk=None):
        """Create workflow from template"""
        template = self.get_object()
        
        # Get workflow data
        name = request.data.get('name')
        description = request.data.get('description')
        
        # Create workflow
        workflow = template.create_workflow(name=name, description=description)
        
        serializer = WorkflowSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowTriggerViewSet(viewsets.ModelViewSet):
    """Workflow trigger viewset"""
    queryset = WorkflowTrigger.objects.all()
    serializer_class = WorkflowTriggerSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_workflow_triggers'
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate trigger"""
        trigger = self.get_object()
        trigger.is_active = True
        trigger.save()
        
        serializer = self.get_serializer(trigger)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate trigger"""
        trigger = self.get_object()
        trigger.is_active = False
        trigger.save()
        
        serializer = self.get_serializer(trigger)
        return Response(serializer.data)


class ScheduledWorkflowViewSet(viewsets.ModelViewSet):
    """Scheduled workflow viewset"""
    queryset = ScheduledWorkflow.objects.all()
    serializer_class = ScheduledWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_scheduled_workflows'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Run scheduled workflow now"""
        scheduled_workflow = self.get_object()
        
        try:
            scheduled_workflow.run(request.user)
            serializer = self.get_serializer(scheduled_workflow)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate scheduled workflow"""
        scheduled_workflow = self.get_object()
        scheduled_workflow.status = 'pending'
        scheduled_workflow.save()
        
        serializer = self.get_serializer(scheduled_workflow)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate scheduled workflow"""
        scheduled_workflow = self.get_object()
        scheduled_workflow.status = 'cancelled'
        scheduled_workflow.save()
        
        serializer = self.get_serializer(scheduled_workflow)
        return Response(serializer.data)