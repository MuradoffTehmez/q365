from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer
from .models import (
    Project, Task, Checklist, TaskComment, TaskAttachment, TaskTimeLog
)


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    dependencies_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_dependencies_data(self, obj):
        """Get dependency tasks data"""
        return TaskSerializer(obj.dependencies.all(), many=True, context=self.context).data


class ChecklistSerializer(serializers.ModelSerializer):
    """Checklist serializer"""
    
    class Meta:
        model = Checklist
        fields = '__all__'
        read_only_fields = ('created_at',)


class TaskCommentSerializer(serializers.ModelSerializer):
    """Task comment serializer"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Task attachment serializer"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.CharField(source='file.url', read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'uploaded_at')


class TaskTimeLogSerializer(serializers.ModelSerializer):
    """Task time log serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TaskTimeLog
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class TaskDetailSerializer(TaskSerializer):
    """Task detail serializer with related data"""
    checklists = ChecklistSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    time_logs = TaskTimeLogSerializer(many=True, read_only=True)
    subtasks = TaskSerializer(many=True, read_only=True)
    conflicts = serializers.SerializerMethodField()
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + (
            'checklists', 'comments', 'attachments', 'time_logs', 'subtasks', 'conflicts'
        )
    
    def get_conflicts(self, obj):
        """Get task conflicts"""
        return obj.check_conflicts()


class ProjectDetailSerializer(ProjectSerializer):
    """Project detail serializer with related data"""
    tasks = TaskSerializer(many=True, read_only=True)
    subprojects = ProjectSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ('tasks', 'subprojects')