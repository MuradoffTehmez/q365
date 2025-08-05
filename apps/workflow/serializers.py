from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer, RoleSerializer
from .models import (
    Workflow, State, Transition, WorkflowInstance, WorkflowHistory,
    WorkflowTemplate, WorkflowTrigger, ScheduledWorkflow
)


class StateSerializer(serializers.ModelSerializer):
    """State serializer"""
    
    class Meta:
        model = State
        fields = '__all__'
        read_only_fields = ('created_at',)


class TransitionSerializer(serializers.ModelSerializer):
    """Transition serializer"""
    from_state_name = serializers.CharField(source='from_state.name', read_only=True)
    to_state_name = serializers.CharField(source='to_state.name', read_only=True)
    
    class Meta:
        model = Transition
        fields = '__all__'
        read_only_fields = ('created_at',)


class WorkflowSerializer(serializers.ModelSerializer):
    """Workflow serializer"""
    states_data = StateSerializer(source='states', many=True, read_only=True)
    transitions_data = TransitionSerializer(source='transitions', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        # Create workflow
        workflow = super().create(validated_data)
        
        # Create initial state if none exists
        if not workflow.states.exists():
            State.objects.create(
                workflow=workflow,
                name=_('Initial'),
                is_initial=True
            )
        
        return workflow


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Workflow instance serializer"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    current_state_name = serializers.CharField(source='current_state.name', read_only=True)
    current_state_color = serializers.CharField(source='current_state.color', read_only=True)
    started_by_name = serializers.CharField(source='started_by.get_full_name', read_only=True)
    available_transitions = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowInstance
        fields = '__all__'
        read_only_fields = ('started_by', 'started_at', 'completed_at')
    
    def get_available_transitions(self, obj):
        """Get available transitions for the workflow instance"""
        transitions = obj.get_available_transitions()
        return TransitionSerializer(transitions, many=True).data


class WorkflowHistorySerializer(serializers.ModelSerializer):
    """Workflow history serializer"""
    workflow_instance_name = serializers.CharField(source='workflow_instance.workflow.name', read_only=True)
    from_state_name = serializers.CharField(source='from_state.name', read_only=True)
    to_state_name = serializers.CharField(source='to_state.name', read_only=True)
    transition_name = serializers.CharField(source='transition.name', read_only=True)
    triggered_by_name = serializers.CharField(source='triggered_by.get_full_name', read_only=True)
    
    class Meta:
        model = WorkflowHistory
        fields = '__all__'
        read_only_fields = ('triggered_at',)


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Workflow template serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        # Generate workflow data if not provided
        if 'workflow_data' not in validated_data:
            # This would be populated from the UI when creating a template
            validated_data['workflow_data'] = {
                'states': [],
                'transitions': []
            }
        
        return super().create(validated_data)


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    """Workflow trigger serializer"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = WorkflowTrigger
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScheduledWorkflowSerializer(serializers.ModelSerializer):
    """Scheduled workflow serializer"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ScheduledWorkflow
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'last_run', 'next_run')