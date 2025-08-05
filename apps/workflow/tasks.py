from celery import shared_task
from django.utils import timezone
from .models import ScheduledWorkflow


@shared_task
def run_scheduled_workflows():
    """Run scheduled workflows that are due"""
    now = timezone.now()
    
    # Get scheduled workflows that are due
    scheduled_workflows = ScheduledWorkflow.objects.filter(
        status='pending',
        scheduled_date__lte=now
    )
    
    # Run each scheduled workflow
    for scheduled_workflow in scheduled_workflows:
        try:
            scheduled_workflow.run()
        except Exception as e:
            # Log the error
            print(f"Error running scheduled workflow {scheduled_workflow.id}: {str(e)}")
    
    return f"Ran {scheduled_workflows.count()} scheduled workflows"


@shared_task
def check_and_run_recurring_workflows():
    """Check and run recurring workflows"""
    now = timezone.now()
    
    # Get daily scheduled workflows that need to run
    daily_workflows = ScheduledWorkflow.objects.filter(
        schedule_type='daily',
        status='pending',
        next_run__lte=now
    )
    
    # Get weekly scheduled workflows that need to run
    weekly_workflows = ScheduledWorkflow.objects.filter(
        schedule_type='weekly',
        status='pending',
        next_run__lte=now
    )
    
    # Get monthly scheduled workflows that need to run
    monthly_workflows = ScheduledWorkflow.objects.filter(
        schedule_type='monthly',
        status='pending',
        next_run__lte=now
    )
    
    # Run all scheduled workflows
    all_workflows = list(daily_workflows) + list(weekly_workflows) + list(monthly_workflows)
    
    for scheduled_workflow in all_workflows:
        try:
            scheduled_workflow.run()
        except Exception as e:
            # Log the error
            print(f"Error running scheduled workflow {scheduled_workflow.id}: {str(e)}")
    
    return f"Ran {len(all_workflows)} recurring scheduled workflows"