from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer
from crm.serializers import CustomerSerializer, ContactSerializer
from .models import (
    ServiceTicket, TicketComment, TicketAttachment, TicketTimeLog,
    RMA, ServiceCall, ServicePlan, SLA, Region, Zone, Skill, TechnicianSkill
)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """Service ticket serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceTicket
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'resolved_at', 'closed_at')


class TicketCommentSerializer(serializers.ModelSerializer):
    """Ticket comment serializer"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Ticket attachment serializer"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.CharField(source='file.url', read_only=True)
    
    class Meta:
        model = TicketAttachment
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'uploaded_at')


class TicketTimeLogSerializer(serializers.ModelSerializer):
    """Ticket time log serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TicketTimeLog
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class RMASerializer(serializers.ModelSerializer):
    """RMA serializer"""
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = RMA
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ServiceCallSerializer(serializers.ModelSerializer):
    """Service call serializer"""
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    technician_name = serializers.CharField(source='technician.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceCall
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ServicePlanSerializer(serializers.ModelSerializer):
    """Service plan serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ServicePlan
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class SLASerializer(serializers.ModelSerializer):
    """SLA serializer"""
    
    class Meta:
        model = SLA
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer"""
    
    class Meta:
        model = Region
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ZoneSerializer(serializers.ModelSerializer):
    """Zone serializer"""
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""
    
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TechnicianSkillSerializer(serializers.ModelSerializer):
    """Technician skill serializer"""
    technician_name = serializers.CharField(source='technician.get_full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = TechnicianSkill
        fields = '__all__'
        read_only_fields = ('created_at',)


class ServiceTicketDetailSerializer(ServiceTicketSerializer):
    """Service ticket detail serializer with related data"""
    comments_data = TicketCommentSerializer(source='comments', many=True, read_only=True)
    attachments_data = TicketAttachmentSerializer(source='attachments', many=True, read_only=True)
    time_logs_data = TicketTimeLogSerializer(source='time_logs', many=True, read_only=True)
    rmas_data = RMASerializer(source='rmas', many=True, read_only=True)
    service_calls_data = ServiceCallSerializer(source='service_calls', many=True, read_only=True)
    
    class Meta(ServiceTicketSerializer.Meta):
        fields = ServiceTicketSerializer.Meta.fields + (
            'comments_data', 'attachments_data', 'time_logs_data', 'rmas_data', 'service_calls_data'
        )