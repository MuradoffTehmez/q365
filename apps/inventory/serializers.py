from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.serializers import UserSerializer
from .models import (
    ProductCategory, Product, ProductImage, Vendor, Warehouse, Stock, StockEntry,
    PurchaseOrder, PurchaseOrderLine, PurchaseReceipt, PurchaseReceiptLine,
    StockTransfer, StockTransferLine, StockCount, StockCountLine
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """Product category serializer"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_below_reorder_point = serializers.BooleanField(read_only=True)
    images_data = ProductImageSerializer(source='images', many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class VendorSerializer(serializers.ModelSerializer):
    """Vendor serializer"""
    
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class WarehouseSerializer(serializers.ModelSerializer):
    """Warehouse serializer"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockSerializer(serializers.ModelSerializer):
    """Stock serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockEntrySerializer(serializers.ModelSerializer):
    """Stock entry serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockEntry
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    """Purchase order line serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    
    class Meta:
        model = PurchaseOrderLine
        fields = '__all__'
        read_only_fields = ('total', 'received_quantity')


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Purchase order serializer"""
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    lines_data = PurchaseOrderLineSerializer(source='lines', many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'tax_amount', 'total')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for line_data in lines_data:
            PurchaseOrderLine.objects.create(purchase_order=purchase_order, **line_data)
        
        # Calculate totals
        subtotal = sum(line.total for line in purchase_order.lines.all())
        purchase_order.subtotal = subtotal
        purchase_order.save()
        
        return purchase_order
    
    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', [])
        purchase_order = super().update(instance, validated_data)
        
        # Update lines
        purchase_order.lines.all().delete()
        for line_data in lines_data:
            PurchaseOrderLine.objects.create(purchase_order=purchase_order, **line_data)
        
        # Calculate totals
        subtotal = sum(line.total for line in purchase_order.lines.all())
        purchase_order.subtotal = subtotal
        purchase_order.save()
        
        return purchase_order


class PurchaseReceiptLineSerializer(serializers.ModelSerializer):
    """Purchase receipt line serializer"""
    product_name = serializers.CharField(source='purchase_order_line.product.name', read_only=True)
    
    class Meta:
        model = PurchaseReceiptLine
        fields = '__all__'


class PurchaseReceiptSerializer(serializers.ModelSerializer):
    """Purchase receipt serializer"""
    purchase_order_number = serializers.CharField(source='purchase_order.number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    lines_data = PurchaseReceiptLineSerializer(source='lines', many=True, read_only=True)
    
    class Meta:
        model = PurchaseReceipt
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        purchase_receipt = PurchaseReceipt.objects.create(**validated_data)
        
        for line_data in lines_data:
            PurchaseReceiptLine.objects.create(purchase_receipt=purchase_receipt, **line_data)
        
        return purchase_receipt


class StockTransferLineSerializer(serializers.ModelSerializer):
    """Stock transfer line serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockTransferLine
        fields = '__all__'


class StockTransferSerializer(serializers.ModelSerializer):
    """Stock transfer serializer"""
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    lines_data = StockTransferLineSerializer(source='lines', many=True, read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        stock_transfer = StockTransfer.objects.create(**validated_data)
        
        for line_data in lines_data:
            StockTransferLine.objects.create(stock_transfer=stock_transfer, **line_data)
        
        return stock_transfer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock transfer"""
        stock_transfer = self.get_object()
        
        # Update status
        stock_transfer.status = 'completed'
        stock_transfer.save()
        
        # Create stock entries for each line
        for line in stock_transfer.lines.all():
            # Out from source warehouse
            StockEntry.objects.create(
                product=line.product,
                warehouse=stock_transfer.from_warehouse,
                type='out',
                quantity=line.quantity,
                reference=f"Stock Transfer {stock_transfer.number}",
                created_by=request.user
            )
            
            # In to destination warehouse
            StockEntry.objects.create(
                product=line.product,
                warehouse=stock_transfer.to_warehouse,
                type='in',
                quantity=line.quantity,
                reference=f"Stock Transfer {stock_transfer.number}",
                created_by=request.user
            )
        
        serializer = self.get_serializer(stock_transfer)
        return Response(serializer.data)


class StockCountLineSerializer(serializers.ModelSerializer):
    """Stock count line serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockCountLine
        fields = '__all__'
        read_only_fields = ('system_quantity', 'difference')


class StockCountSerializer(serializers.ModelSerializer):
    """Stock count serializer"""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    lines_data = StockCountLineSerializer(source='lines', many=True, read_only=True)
    
    class Meta:
        model = StockCount
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        stock_count = StockCount.objects.create(**validated_data)
        
        for line_data in lines_data:
            # Get system quantity from stock
            try:
                stock = Stock.objects.get(
                    product=line_data['product'],
                    warehouse=stock_count.warehouse
                )
                system_quantity = stock.quantity
            except Stock.DoesNotExist:
                system_quantity = 0
            
            StockCountLine.objects.create(
                stock_count=stock_count,
                system_quantity=system_quantity,
                **line_data
            )
        
        return stock_count
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock count"""
        stock_count = self.get_object()
        
        # Update status
        stock_count.status = 'completed'
        stock_count.save()
        
        # Create stock adjustments for each line with differences
        for line in stock_count.lines.all():
            if line.difference != 0:
                StockEntry.objects.create(
                    product=line.product,
                    warehouse=stock_count.warehouse,
                    type='adjustment',
                    quantity=line.counted_quantity,
                    reference=f"Stock Count {stock_count.number}",
                    created_by=request.user
                )
                
                # Update stock last count date
                try:
                    stock = Stock.objects.get(
                        product=line.product,
                        warehouse=stock_count.warehouse
                    )
                    stock.last_count_date = stock_count.date
                    stock.save()
                except Stock.DoesNotExist:
                    pass
        
        serializer = self.get_serializer(stock_count)
        return Response(serializer.data)


class ProductDetailSerializer(ProductSerializer):
    """Product detail serializer with related data"""
    category_data = ProductCategorySerializer(source='category', read_only=True)
    stocks_data = StockSerializer(source='stocks', many=True, read_only=True)
    purchase_order_lines_data = PurchaseOrderLineSerializer(source='purchase_order_lines', many=True, read_only=True)
    stock_transfer_lines_data = StockTransferLineSerializer(source='stock_transfer_lines', many=True, read_only=True)
    stock_count_lines_data = StockCountLineSerializer(source='stock_count_lines', many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + (
            'category_data', 'stocks_data', 'purchase_order_lines_data', 
            'stock_transfer_lines_data', 'stock_count_lines_data'
        )