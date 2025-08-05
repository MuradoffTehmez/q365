from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer
from .models import (
    Lead, Customer, Contact, Opportunity, Quotation, QuotationItem,
    Campaign, EmailTemplate, EmailCampaign, SalesActivity, Commission
)


class LeadSerializer(serializers.ModelSerializer):
    """Lead serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    """Contact serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CustomerSerializer(serializers.ModelSerializer):
    """Customer serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    contacts_data = ContactSerializer(source='contacts', many=True, read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class OpportunitySerializer(serializers.ModelSerializer):
    """Opportunity serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class QuotationItemSerializer(serializers.ModelSerializer):
    """Quotation item serializer"""
    
    class Meta:
        model = QuotationItem
        fields = '__all__'
        read_only_fields = ('total',)


class QuotationSerializer(serializers.ModelSerializer):
    """Quotation serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items_data = QuotationItemSerializer(source='items', many=True, read_only=True)
    
    class Meta:
        model = Quotation
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'tax_amount', 'total')


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email template serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class CampaignSerializer(serializers.ModelSerializer):
    """Campaign serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class EmailCampaignSerializer(serializers.ModelSerializer):
    """Email campaign serializer"""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmailCampaign
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'sent_at')


class SalesActivitySerializer(serializers.ModelSerializer):
    """Sales activity serializer"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SalesActivity
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'completed_date')


class CommissionSerializer(serializers.ModelSerializer):
    """Commission serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Commission
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'approved_by', 'paid_date')


class CustomerDetailSerializer(CustomerSerializer):
    """Customer detail serializer with related data"""
    opportunities_data = OpportunitySerializer(source='opportunities', many=True, read_only=True)
    quotations_data = QuotationSerializer(source='quotations', many=True, read_only=True)
    sales_activities_data = SalesActivitySerializer(source='sales_activities', many=True, read_only=True)
    
    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + (
            'opportunities_data', 'quotations_data', 'sales_activities_data'
        )


class OpportunityDetailSerializer(OpportunitySerializer):
    """Opportunity detail serializer with related data"""
    customer_data = CustomerSerializer(source='customer', read_only=True)
    quotations_data = QuotationSerializer(source='quotations', many=True, read_only=True)
    sales_activities_data = SalesActivitySerializer(source='sales_activities', many=True, read_only=True)
    commissions_data = CommissionSerializer(source='commissions', many=True, read_only=True)
    
    class Meta(OpportunitySerializer.Meta):
        fields = OpportunitySerializer.Meta.fields + (
            'customer_data', 'quotations_data', 'sales_activities_data', 'commissions_data'
        )


class QuotationDetailSerializer(QuotationSerializer):
    """Quotation detail serializer with related data"""
    customer_data = CustomerSerializer(source='customer', read_only=True)
    opportunity_data = OpportunitySerializer(source='opportunity', read_only=True)
    items_data = QuotationItemSerializer(source='items', many=True, read_only=True)
    
    class Meta(QuotationSerializer.Meta):
        fields = QuotationSerializer.Meta.fields + (
            'customer_data', 'opportunity_data'
        )