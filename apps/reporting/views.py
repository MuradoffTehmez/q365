from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import connection
from core.permissions import HasRolePermission
from .models import Report, Dashboard, DashboardWidget, KPI, ScheduledReport
from .serializers import (
    ReportSerializer, ReportDetailSerializer, DashboardSerializer, DashboardDetailSerializer,
    DashboardWidgetSerializer, KPISerializer, ScheduledReportSerializer
)


class ReportViewSet(viewsets.ModelViewSet):
    """Report viewset"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_reports'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReportDetailSerializer
        return ReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute report query"""
        report = self.get_object()
        
        if not report.query:
            return Response(
                {'detail': _('Report query is empty')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Execute the query
            with connection.cursor() as cursor:
                cursor.execute(report.query)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return Response({
                'columns': columns,
                'data': data
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export report data"""
        report = self.get_object()
        
        if not report.query:
            return Response(
                {'detail': _('Report query is empty')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        format = request.data.get('format', 'json')
        
        try:
            # Execute the query
            with connection.cursor() as cursor:
                cursor.execute(report.query)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if format == 'csv':
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
                
                writer = csv.writer(response)
                writer.writerow(columns)
                for row in data:
                    writer.writerow([row[col] for col in columns])
                
                return response
            
            elif format == 'excel':
                import pandas as pd
                from django.http import HttpResponse
                
                df = pd.DataFrame(data)
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'attachment; filename="{report.name}.xlsx"'
                df.to_excel(response, index=False)
                
                return response
            
            else:
                return Response({
                    'columns': columns,
                    'data': data
                })
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DashboardViewSet(viewsets.ModelViewSet):
    """Dashboard viewset"""
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_dashboards'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DashboardDetailSerializer
        return DashboardSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """Dashboard widget viewset"""
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_dashboards'


class KPIViewSet(viewsets.ModelViewSet):
    """KPI viewset"""
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_kpis'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def calculate(self, request, pk=None):
        """Calculate KPI value"""
        kpi = self.get_object()
        
        try:
            # Build the query
            query = f"""
            SELECT {kpi.aggregation}({kpi.field}) as value
            FROM {kpi.model}
            """
            
            # Add filters if any
            if kpi.filters:
                conditions = []
                for field, value in kpi.filters.items():
                    if isinstance(value, list):
                        conditions.append(f"{field} IN ({', '.join([f\"'{v}'\" for v in value])})")
                    else:
                        conditions.append(f"{field} = '{value}'")
                
                if conditions:
                    query += f" WHERE {' AND '.join(conditions)}"
            
            # Execute the query
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                value = result[0] if result else 0
            
            # Calculate variance if target is set
            variance = None
            variance_percentage = None
            
            if kpi.target and kpi.target != 0:
                variance = value - kpi.target
                variance_percentage = (variance / kpi.target) * 100
            
            return Response({
                'value': value,
                'target': kpi.target,
                'variance': variance,
                'variance_percentage': variance_percentage,
                'unit': kpi.unit
            })
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ScheduledReportViewSet(viewsets.ModelViewSet):
    """Scheduled report viewset"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_scheduled_reports'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Run scheduled report now"""
        scheduled_report = self.get_object()
        
        # Update last run time
        scheduled_report.last_run = timezone.now()
        scheduled_report.save()
        
        # Here you would implement the actual report generation and sending logic
        # For now, just update the last run time
        
        serializer = self.get_serializer(scheduled_report)
        return Response(serializer.data)