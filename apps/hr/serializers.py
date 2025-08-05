from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer
from .models import (
    Employee, Skill, EmployeeSkill, Certification, Education, Experience,
    LeaveType, Leave, LeaveBalance, Benefit, Training, TrainingParticipant,
    PerformanceReview, PerformanceGoal, Document
)


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    years_of_service = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'years_of_service')


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""
    
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EmployeeSkillSerializer(serializers.ModelSerializer):
    """Employee skill serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = EmployeeSkill
        fields = '__all__'
        read_only_fields = ('created_at',)


class CertificationSerializer(serializers.ModelSerializer):
    """Certification serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Certification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EducationSerializer(serializers.ModelSerializer):
    """Education serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ExperienceSerializer(serializers.ModelSerializer):
    """Experience serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Leave type serializer"""
    
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class LeaveSerializer(serializers.ModelSerializer):
    """Leave serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = ('approved_by', 'approved_at', 'created_at', 'updated_at', 'total_days')


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Leave balance serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'remaining_days')


class BenefitSerializer(serializers.ModelSerializer):
    """Benefit serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Benefit
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TrainingSerializer(serializers.ModelSerializer):
    """Training serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Training
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class TrainingParticipantSerializer(serializers.ModelSerializer):
    """Training participant serializer"""
    training_name = serializers.CharField(source='training.name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = TrainingParticipant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PerformanceReviewSerializer(serializers.ModelSerializer):
    """Performance review serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    
    class Meta:
        model = PerformanceReview
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PerformanceGoalSerializer(serializers.ModelSerializer):
    """Performance goal serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    performance_review_title = serializers.CharField(source='performance_review.title', read_only=True)
    
    class Meta:
        model = PerformanceGoal
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DocumentSerializer(serializers.ModelSerializer):
    """Document serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EmployeeDetailSerializer(EmployeeSerializer):
    """Employee detail serializer with related data"""
    skills_data = EmployeeSkillSerializer(source='skills', many=True, read_only=True)
    certifications_data = CertificationSerializer(source='certifications', many=True, read_only=True)
    educations_data = EducationSerializer(source='educations', many=True, read_only=True)
    experiences_data = ExperienceSerializer(source='experiences', many=True, read_only=True)
    leaves_data = LeaveSerializer(source='leaves', many=True, read_only=True)
    leave_balances_data = LeaveBalanceSerializer(source='leave_balances', many=True, read_only=True)
    benefits_data = BenefitSerializer(source='benefits', many=True, read_only=True)
    trainings_data = TrainingParticipantSerializer(source='trainings', many=True, read_only=True)
    performance_reviews_data = PerformanceReviewSerializer(source='performance_reviews', many=True, read_only=True)
    performance_goals_data = PerformanceGoalSerializer(source='performance_goals', many=True, read_only=True)
    documents_data = DocumentSerializer(source='documents', many=True, read_only=True)
    
    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + (
            'skills_data', 'certifications_data', 'educations_data', 'experiences_data',
            'leaves_data', 'leave_balances_data', 'benefits_data', 'trainings_data',
            'performance_reviews_data', 'performance_goals_data', 'documents_data'
        )


class TrainingDetailSerializer(TrainingSerializer):
    """Training detail serializer with related data"""
    participants_data = TrainingParticipantSerializer(source='participants', many=True, read_only=True)
    
    class Meta(TrainingSerializer.Meta):
        fields = TrainingSerializer.Meta.fields + ('participants_data',)