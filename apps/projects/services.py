from django.utils import timezone
from django.db import transaction
from .models import Project, Task, ProjectTemplate, ProjectTemplateTask

class ProjectService:
    """Service for managing projects"""
    
    @staticmethod
    def create_project_from_template(template, user, project_data):
        """Create a new project from a template"""
        with transaction.atomic():
            # Create project
            project = Project.objects.create(
                name=project_data.get('name', f"{template.name} Project"),
                code=project_data.get('code', f"PRJ-{timezone.now().strftime('%Y%m%d%H%M')}"),
                description=project_data.get('description', template.description),
                start_date=project_data.get('start_date'),
                end_date=project_data.get('end_date'),
                manager_id=project_data.get('manager_id'),
                team_id=project_data.get('team_id'),
                created_by=user
            )
            
            # Create tasks from template
            template_tasks = ProjectTemplateTask.objects.filter(template=template)
            task_mapping = {}  # Maps template task IDs to new task IDs
            
            # First pass: create tasks without dependencies
            for template_task in template_tasks.filter(parent=None):
                task = Task.objects.create(
                    project=project,
                    name=template_task.name,
                    description=template_task.description,
                    estimated_hours=template_task.estimated_hours,
                    order=template_task.order,
                    is_milestone=template_task.is_milestone,
                    created_by=user
                )
                task_mapping[template_task.id] = task.id
            
            # Second pass: create subtasks and set dependencies
            for template_task in template_tasks:
                if template_task.parent_id:
                    parent_task_id = task_mapping.get(template_task.parent_id)
                    if parent_task_id:
                        parent_task = Task.objects.get(id=parent_task_id)
                    else:
                        parent_task = None
                else:
                    parent_task = None
                
                task = Task.objects.create(
                    project=project,
                    name=template_task.name,
                    description=template_task.description,
                    estimated_hours=template_task.estimated_hours,
                    order=template_task.order,
                    is_milestone=template_task.is_milestone,
                    parent=parent_task,
                    created_by=user
                )
                task_mapping[template_task.id] = task.id
            
            return project
    
    @staticmethod
    def duplicate_project(project, user):
        """Duplicate a project as a template"""
        with transaction.atomic():
            # Create new project
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
                created_by=user
            )
            
            # Copy tasks
            for task in project.tasks.filter(parent=None):
                ProjectService._copy_task(task, new_project, user)
            
            return new_project
    
    @staticmethod
    def _copy_task(task, new_project, user, parent_task=None):
        """Helper method to copy task and its subtasks"""
        # Create new task
        new_task = Task.objects.create(
            project=new_project,
            parent=parent_task,
            name=task.name,
            description=task.description,
            priority=task.priority,
            estimated_hours=task.estimated_hours,
            order=task.order,
            is_milestone=task.is_milestone,
            created_by=user
        )
        
        # Copy checklists
        for checklist in task.checklists.all():
            new_task.checklists.create(
                title=checklist.title,
                order=checklist.order
            )
        
        # Copy subtasks
        for subtask in task.subtasks.all():
            ProjectService._copy_task(subtask, new_project, user, new_task)
        
        return new_task

class TaskService:
    """Service for managing tasks"""
    
    @staticmethod
    def update_task_progress(task):
        """Update task progress based on subtasks and checklists"""
        # Update based on subtasks
        if task.subtasks.exists():
            total_subtasks = task.subtasks.count()
            completed_subtasks = task.subtasks.filter(status='completed').count()
            progress = int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
            
            if progress != task.progress:
                task.progress = progress
                task.save()
        
        # Update based on checklists
        if task.checklists.exists():
            total_checklists = task.checklists.count()
            completed_checklists = task.checklists.filter(is_completed=True).count()
            checklist_progress = int((completed_checklists / total_checklists) * 100) if total_checklists > 0 else 0
            
            if checklist_progress > task.progress:
                task.progress = checklist_progress
                task.save()
        
        # Update status based on progress
        if task.progress >= 100 and task.status != 'completed':
            task.status = 'completed'
            task.save()
        elif task.progress > 0 and task.status == 'not_started':
            task.status = 'in_progress'
            task.save()
    
    @staticmethod
    def check_task_conflicts(task):
        """Check for task conflicts"""
        conflicts = []
        
        # Check if assignee has overlapping tasks
        if task.assignee:
            overlapping_tasks = Task.objects.filter(
                assignee=task.assignee,
                status__in=['not_started', 'in_progress'],
                start_date__lte=task.due_date,
                due_date__gte=task.start_date
            ).exclude(id=task.id)
            
            for conflicting_task in overlapping_tasks:
                conflicts.append({
                    'type': 'assignee_overlap',
                    'task': conflicting_task,
                    'message': _('Task overlaps with another task assigned to the same person')
                })
        
        # Check if dependencies are completed
        for dependency in task.dependencies.all():
            if dependency.status != 'completed':
                conflicts.append({
                    'type': 'dependency_not_completed',
                    'task': dependency,
                    'message': _('Dependency task is not completed')
                })
        
        return conflicts
    
    @staticmethod
    def log_time(task, user, hours, date, description=''):
        """Log time for a task"""
        from .models import TaskTimeLog
        
        time_log = TaskTimeLog.objects.create(
            task=task,
            user=user,
            hours=hours,
            date=date,
            description=description
        )
        
        # Update task actual hours
        total_hours = TaskTimeLog.objects.filter(task=task).aggregate(
            total=models.Sum('hours')
        )['total'] or 0
        task.actual_hours = total_hours
        task.save()
        
        return time_log