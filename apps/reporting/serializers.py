from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer, RoleSerializer, OrganizationSerializer
from .models import Report, Dashboard, DashboardWidget, KPI, ScheduledReport


class ReportSerializer(serializers.ModelSerializer):
    """Report serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Dashboard widget serializer"""
    
    class Meta:
        model = DashboardWidget
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DashboardSerializer(serializers.ModelSerializer):
    """Dashboard serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    widgets_data = DashboardWidgetSerializer(source='widgets', many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class KPISerializer(serializers.ModelSerializer):
    """KPI serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = KPI
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Scheduled report serializer"""
    report_name = serializers.CharField(source='report.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    recipients_data = UserSerializer(source='recipients', many=True, read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'last_run', 'next_run')


class DashboardDetailSerializer(DashboardSerializer):
    """Dashboard detail serializer with related data"""
    organization_data = OrganizationSerializer(source='organization', read_only=True)
    
    class Meta(DashboardSerializer.Meta):
        fields = DashboardSerializer.Meta.fields + ('organization_data',)


class ReportDetailSerializer(ReportSerializer):
    """Report detail serializer with related data"""
    organization_data = OrganizationSerializer(source='organization', read_only=True)
    
    class Meta(ReportSerializer.Meta):
        fields = ReportSerializer.Meta.fields + ('organization_data',)