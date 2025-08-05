from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.permissions import HasRolePermission
from .models import (
    Lead, Customer, Contact, Opportunity, Quotation, QuotationItem,
    Campaign, EmailTemplate, EmailCampaign, SalesActivity, Commission
)
from .serializers import (
    LeadSerializer, CustomerSerializer, CustomerDetailSerializer, ContactSerializer,
    OpportunitySerializer, OpportunityDetailSerializer, QuotationSerializer, QuotationDetailSerializer,
    QuotationItemSerializer, CampaignSerializer, EmailTemplateSerializer, EmailCampaignSerializer,
    SalesActivitySerializer, CommissionSerializer
)


class LeadViewSet(viewsets.ModelViewSet):
    """Lead viewset"""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_leads'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def convert_to_customer(self, request, pk=None):
        """Convert lead to customer"""
        lead = self.get_object()
        
        # Create customer from lead
        customer_data = {
            'type': 'individual',
            'first_name': lead.first_name,
            'last_name': lead.last_name,
            'email': lead.email,
            'phone': lead.phone,
            'company': lead.company,
            'assigned_to': lead.assigned_to,
            'notes': lead.description,
            'created_by': request.user
        }
        
        customer = Customer.objects.create(**customer_data)
        
        # Update lead status
        lead.status = 'converted'
        lead.save()
        
        # Create opportunity from lead if needed
        if request.data.get('create_opportunity', False):
            opportunity_data = {
                'customer': customer,
                'name': f"Opportunity from {lead.full_name}",
                'stage': 'qualification',
                'assigned_to': lead.assigned_to,
                'created_by': request.user
            }
            opportunity = Opportunity.objects.create(**opportunity_data)
            
            return Response({
                'customer': CustomerSerializer(customer).data,
                'opportunity': OpportunitySerializer(opportunity).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'customer': CustomerSerializer(customer).data
        }, status=status.HTTP_201_CREATED)


class CustomerViewSet(viewsets.ModelViewSet):
    """Customer viewset"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_customers'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def opportunities(self, request, pk=None):
        """Get customer opportunities"""
        customer = self.get_object()
        opportunities = customer.opportunities.all()
        serializer = OpportunitySerializer(opportunities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def quotations(self, request, pk=None):
        """Get customer quotations"""
        customer = self.get_object()
        quotations = customer.quotations.all()
        serializer = QuotationSerializer(quotations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get customer activities"""
        customer = self.get_object()
        activities = customer.sales_activities.all()
        serializer = SalesActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    """Contact viewset"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_customers'


class OpportunityViewSet(viewsets.ModelViewSet):
    """Opportunity viewset"""
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_opportunities'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OpportunityDetailSerializer
        return OpportunitySerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_quotation(self, request, pk=None):
        """Create quotation from opportunity"""
        opportunity = self.get_object()
        
        # Get quotation data from request
        title = request.data.get('title', f"Quotation for {opportunity.name}")
        description = request.data.get('description', '')
        valid_until = request.data.get('valid_until')
        items = request.data.get('items', [])
        
        # Create quotation
        quotation = Quotation.objects.create(
            opportunity=opportunity,
            customer=opportunity.customer,
            title=title,
            description=description,
            valid_until=valid_until,
            assigned_to=opportunity.assigned_to,
            created_by=request.user
        )
        
        # Create quotation items
        for item_data in items:
            QuotationItem.objects.create(
                quotation=quotation,
                product_name=item_data.get('product_name', ''),
                description=item_data.get('description', ''),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                discount=item_data.get('discount', 0),
                order=item_data.get('order', 0)
            )
        
        # Recalculate quotation totals
        quotation.save()
        
        serializer = QuotationDetailSerializer(quotation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def close_won(self, request, pk=None):
        """Close opportunity as won"""
        opportunity = self.get_object()
        opportunity.stage = 'closed_won'
        opportunity.actual_close_date = timezone.now()
        opportunity.save()
        
        # Create commission if percentage is provided
        commission_percentage = request.data.get('commission_percentage')
        if commission_percentage and opportunity.amount:
            Commission.objects.create(
                user=opportunity.assigned_to,
                opportunity=opportunity,
                amount=opportunity.amount * (commission_percentage / 100),
                percentage=commission_percentage,
                status='pending'
            )
        
        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close_lost(self, request, pk=None):
        """Close opportunity as lost"""
        opportunity = self.get_object()
        opportunity.stage = 'closed_lost'
        opportunity.actual_close_date = timezone.now()
        opportunity.save()
        
        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)


class QuotationViewSet(viewsets.ModelViewSet):
    """Quotation viewset"""
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_quotations'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuotationDetailSerializer
        return QuotationSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_quotation(self, request, pk=None):
        """Send quotation to customer"""
        quotation = self.get_object()
        quotation.status = 'sent'
        quotation.save()
        
        # Here you would implement the actual email sending logic
        # For now, just update the status
        
        serializer = self.get_serializer(quotation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept quotation"""
        quotation = self.get_object()
        quotation.status = 'accepted'
        quotation.save()
        
        # If quotation is linked to an opportunity, update opportunity stage
        if quotation.opportunity:
            quotation.opportunity.stage = 'negotiation'
            quotation.opportunity.save()
        
        serializer = self.get_serializer(quotation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject quotation"""
        quotation = self.get_object()
        quotation.status = 'rejected'
        quotation.save()
        
        serializer = self.get_serializer(quotation)
        return Response(serializer.data)


class QuotationItemViewSet(viewsets.ModelViewSet):
    """Quotation item viewset"""
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_quotations'


class CampaignViewSet(viewsets.ModelViewSet):
    """Campaign viewset"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_campaigns'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Email template viewset"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_email_templates'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """Email campaign viewset"""
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_email_campaigns'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_test(self, request, pk=None):
        """Send test email"""
        email_campaign = self.get_object()
        
        # Get test email from request
        test_email = request.data.get('test_email')
        if not test_email:
            return Response(
                {'detail': _('Test email is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would implement the actual test email sending logic
        # For now, just return success
        
        return Response({'detail': _('Test email sent successfully')})
    
    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        """Send email campaign"""
        email_campaign = self.get_object()
        email_campaign.status = 'sending'
        email_campaign.save()
        
        # Here you would implement the actual email campaign sending logic
        # This would typically be a background task
        
        # For now, just update the status
        email_campaign.status = 'sent'
        email_campaign.sent_at = timezone.now()
        email_campaign.save()
        
        serializer = self.get_serializer(email_campaign)
        return Response(serializer.data)


class SalesActivityViewSet(viewsets.ModelViewSet):
    """Sales activity viewset"""
    queryset = SalesActivity.objects.all()
    serializer_class = SalesActivitySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_sales_activities'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete sales activity"""
        activity = self.get_object()
        activity.status = 'completed'
        activity.completed_date = timezone.now()
        activity.save()
        
        serializer = self.get_serializer(activity)
        return Response(serializer.data)


class CommissionViewSet(viewsets.ModelViewSet):
    """Commission viewset"""
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_commissions'
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve commission"""
        commission = self.get_object()
        commission.status = 'approved'
        commission.approved_by = request.user
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark commission as paid"""
        commission = self.get_object()
        commission.status = 'paid'
        commission.paid_date = timezone.now().date()
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel commission"""
        commission = self.get_object()
        commission.status = 'cancelled'
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)