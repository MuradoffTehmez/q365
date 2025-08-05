from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.permissions import HasRolePermission
from .models import (
    Project, Task, Checklist, TaskComment, TaskAttachment, TaskTimeLog
)
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer, 
    TaskSerializer, TaskDetailSerializer,
    ChecklistSerializer, TaskCommentSerializer, 
    TaskAttachmentSerializer, TaskTimeLogSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """Project viewset"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_projects'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate project as template"""
        project = self.get_object()
        
        # Create new project as template
        new_project = Project.objects.create(
            name=f"{project.name} (Copy)",
            code=f"{project.code}_COPY_{timezone.now().strftime('%Y%m%d')}",
            description=project.description,
            status='planning',
            priority=project.priority,
            estimated_hours=project.estimated_hours,
            budget=project.budget,
            manager=project.manager,
            team=project.team,
            is_template=True,
            created_by=request.user
        )
        
        # Copy tasks
        for task in project.tasks.filter(parent=None):
            self._copy_task(task, new_project)
        
        serializer = self.get_serializer(new_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _copy_task(self, task, new_project, parent_task=None):
        """Helper method to copy task and its subtasks"""
        # Create new task
        new_task = Task.objects.create(
            project=new_project,
            parent=parent_task,
            name=task.name,
            description=task.description,
            priority=task.priority,
            estimated_hours=task.estimated_hours,
            is_milestone=task.is_milestone,
            tags=task.tags,
            created_by=self.request.user
        )
        
        # Copy checklists
        for checklist in task.checklists.all():
            Checklist.objects.create(
                task=new_task,
                title=checklist.title,
                order=checklist.order
            )
        
        # Copy subtasks
        for subtask in task.subtasks.all():
            self._copy_task(subtask, new_project, new_task)
        
        return new_task
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get project templates"""
        templates = Project.objects.filter(is_template=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_from_template(self, request, pk=None):
        """Create project from template"""
        template = self.get_object()
        
        # Get project data from request
        name = request.data.get('name', f"{template.name} Project")
        code = request.data.get('code', f"PRJ_{timezone.now().strftime('%Y%m%d%H%M')}")
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        manager_id = request.data.get('manager_id')
        team_id = request.data.get('team_id')
        
        # Create new project
        new_project = Project.objects.create(
            name=name,
            code=code,
            description=template.description,
            status='planning',
            priority=template.priority,
            start_date=start_date,
            end_date=end_date,
            estimated_hours=template.estimated_hours,
            budget=template.budget,
            manager_id=manager_id,
            team_id=team_id,
            is_template=False,
            created_by=request.user
        )
        
        # Copy tasks
        for task in template.tasks.filter(parent=None):
            self._copy_task(task, new_project)
        
        serializer = self.get_serializer(new_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskViewSet(viewsets.ModelViewSet):
    """Task viewset"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_tasks'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def check_conflicts(self, request, pk=None):
        """Check task conflicts"""
        task = self.get_object()
        conflicts = task.check_conflicts()
        return Response({'conflicts': conflicts})
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update task progress based on subtasks"""
        task = self.get_object()
        
        # Calculate progress based on subtasks
        if task.subtasks.exists():
            total_subtasks = task.subtasks.count()
            completed_subtasks = task.subtasks.filter(status='completed').count()
            progress = int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
            
            # Update task progress
            task.progress = progress
            task.save()
            
            # If all subtasks are completed, mark task as completed
            if progress == 100 and task.status != 'completed':
                task.status = 'completed'
                task.save()
            
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        
        return Response({'detail': _('Task has no subtasks')}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_time_log(self, request, pk=None):
        """Add time log to task"""
        task = self.get_object()
        
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
        time_log = TaskTimeLog.objects.create(
            task=task,
            user=request.user,
            hours=hours,
            date=date,
            description=description
        )
        
        # Update task actual hours
        total_hours = task.time_logs.aggregate(total=models.Sum('hours'))['total'] or 0
        task.actual_hours = total_hours
        task.save()
        
        serializer = TaskTimeLogSerializer(time_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChecklistViewSet(viewsets.ModelViewSet):
    """Checklist viewset"""
    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_tasks'
    
    @action(detail=True, methods=['post'])
    def toggle_completed(self, request, pk=None):
        """Toggle checklist completed status"""
        checklist = self.get_object()
        checklist.is_completed = not checklist.is_completed
        checklist.save()
        
        # Update task progress if all checklists are completed
        task = checklist.task
        if task.checklists.exists():
            total_checklists = task.checklists.count()
            completed_checklists = task.checklists.filter(is_completed=True).count()
            progress = int((completed_checklists / total_checklists) * 100) if total_checklists > 0 else 0
            
            # Update task progress
            task.progress = progress
            task.save()
        
        serializer = self.get_serializer(checklist)
        return Response(serializer.data)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """Task comment viewset"""
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """Task attachment viewset"""
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class TaskTimeLogViewSet(viewsets.ModelViewSet):
    """Task time log viewset"""
    queryset = TaskTimeLog.objects.all()
    serializer_class = TaskTimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Update task actual hours
        task = serializer.instance.task
        total_hours = task.time_logs.aggregate(total=models.Sum('hours'))['total'] or 0
        task.actual_hours = total_hours
        task.save()