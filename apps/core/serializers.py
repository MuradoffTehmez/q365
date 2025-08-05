from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Role, Permission, UserRole, Organization, 
    Department, Sector, Team, Notification, Reminder
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'department', 'department_name', 'position',
            'employee_id', 'is_active_employee', 'hire_date', 'termination_date',
            'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined'
        )
        read_only_fields = ('is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')


class UserCreateSerializer(serializers.ModelSerializer):
    """User create serializer"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone', 'department', 'position', 'employee_id', 'is_active_employee', 'hire_date'
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PermissionSerializer(serializers.ModelSerializer):
    """Permission serializer"""
    
    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """Role serializer"""
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = '__all__'
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        role = super().update(instance, validated_data)
        
        if permission_ids is not None:
            role.permissions.set(permission_ids)
        
        return role


class UserRoleSerializer(serializers.ModelSerializer):
    """User role serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'


class SectorSerializer(serializers.ModelSerializer):
    """Sector serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Sector
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer"""
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    leader_name = serializers.CharField(source='leader.get_full_name', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer"""
    departments_data = DepartmentSerializer(source='departments', many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('recipient', 'created_at', 'read_at')


class ReminderSerializer(serializers.ModelSerializer):
    """Reminder serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'completed_at')