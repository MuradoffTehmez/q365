from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from core.permissions import HasRolePermission
from .models import (
    ProductCategory, Product, ProductImage, Vendor, Warehouse, Stock, StockEntry,
    PurchaseOrder, PurchaseOrderLine, PurchaseReceipt, PurchaseReceiptLine,
    StockTransfer, StockTransferLine, StockCount, StockCountLine
)
from .serializers import (
    ProductCategorySerializer, ProductSerializer, ProductDetailSerializer, ProductImageSerializer,
    VendorSerializer, WarehouseSerializer, StockSerializer, StockEntrySerializer,
    PurchaseOrderSerializer, PurchaseOrderLineSerializer, PurchaseReceiptSerializer, PurchaseReceiptLineSerializer,
    StockTransferSerializer, StockTransferLineSerializer, StockCountSerializer, StockCountLineSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """Product category viewset"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_product_categories'
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree"""
        categories = ProductCategory.objects.filter(parent=None)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """Product viewset"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_products'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = Product.objects.filter(is_below_reorder_point=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock"""
        product = self.get_object()
        
        # Get stock data
        warehouse_id = request.data.get('warehouse_id')
        quantity = request.data.get('quantity')
        type = request.data.get('type', 'adjustment')
        notes = request.data.get('notes', '')
        
        if not warehouse_id or quantity is None:
            return Response(
                {'detail': _('Warehouse ID and quantity are required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            return Response(
                {'detail': _('Warehouse not found')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create stock entry
        StockEntry.objects.create(
            product=product,
            warehouse=warehouse,
            type=type,
            quantity=quantity,
            notes=notes,
            created_by=request.user
        )
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """Product image viewset"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_products'


class VendorViewSet(viewsets.ModelViewSet):
    """Vendor viewset"""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_vendors'


class WarehouseViewSet(viewsets.ModelViewSet):
    """Warehouse viewset"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_warehouses'


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """Stock viewset (read-only)"""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_stock'
    
    @action(detail=False, methods=['get'])
    def by_warehouse(self, request):
        """Get stock by warehouse"""
        warehouse_id = request.query_params.get('warehouse_id')
        
        if not warehouse_id:
            return Response(
                {'detail': _('Warehouse ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stocks = Stock.objects.filter(warehouse_id=warehouse_id)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Get stock by product"""
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'detail': _('Product ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stocks = Stock.objects.filter(product_id=product_id)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class StockEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Stock entry viewset (read-only)"""
    queryset = StockEntry.objects.all()
    serializer_class = StockEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'view_stock_entries'


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Purchase order viewset"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_purchase_orders'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send purchase order to vendor"""
        purchase_order = self.get_object()
        
        # Update status
        if purchase_order.status == 'draft':
            purchase_order.status = 'sent'
            purchase_order.save()
        
        # Here you would implement the actual email sending logic
        # For now, just update the status
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm purchase order"""
        purchase_order = self.get_object()
        
        # Update status
        if purchase_order.status == 'sent':
            purchase_order.status = 'confirmed'
            purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_receipt(self, request, pk=None):
        """Create purchase receipt for purchase order"""
        purchase_order = self.get_object()
        
        # Get receipt data
        date = request.data.get('date', timezone.now().date())
        notes = request.data.get('notes', '')
        lines = request.data.get('lines', [])
        
        with transaction.atomic():
            # Create purchase receipt
            receipt = PurchaseReceipt.objects.create(
                purchase_order=purchase_order,
                date=date,
                notes=notes,
                created_by=request.user
            )
            
            # Create receipt lines
            for line_data in lines:
                po_line_id = line_data.get('purchase_order_line_id')
                quantity = line_data.get('quantity')
                line_notes = line_data.get('notes', '')
                
                if not po_line_id or quantity is None:
                    transaction.set_rollback(True)
                    return Response(
                        {'detail': _('Purchase order line ID and quantity are required for each line')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    po_line = PurchaseOrderLine.objects.get(id=po_line_id)
                except PurchaseOrderLine.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response(
                        {'detail': _('Purchase order line not found')},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                PurchaseReceiptLine.objects.create(
                    purchase_receipt=receipt,
                    purchase_order_line=po_line,
                    quantity=quantity,
                    notes=line_notes
                )
        
        serializer = PurchaseReceiptSerializer(receipt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PurchaseOrderLineViewSet(viewsets.ModelViewSet):
    """Purchase order line viewset"""
    queryset = PurchaseOrderLine.objects.all()
    serializer_class = PurchaseOrderLineSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_purchase_orders'


class PurchaseReceiptViewSet(viewsets.ModelViewSet):
    """Purchase receipt viewset"""
    queryset = PurchaseReceipt.objects.all()
    serializer_class = PurchaseReceiptSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_purchase_receipts'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PurchaseReceiptLineViewSet(viewsets.ModelViewSet):
    """Purchase receipt line viewset"""
    queryset = PurchaseReceiptLine.objects.all()
    serializer_class = PurchaseReceiptLineSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_purchase_receipts'


class StockTransferViewSet(viewsets.ModelViewSet):
    """Stock transfer viewset"""
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_stock_transfers'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def in_transit(self, request, pk=None):
        """Mark stock transfer as in transit"""
        stock_transfer = self.get_object()
        
        # Update status
        if stock_transfer.status == 'draft':
            stock_transfer.status = 'in_transit'
            stock_transfer.save()
        
        serializer = self.get_serializer(stock_transfer)
        return Response(serializer.data)
    
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


class StockTransferLineViewSet(viewsets.ModelViewSet):
    """Stock transfer line viewset"""
    queryset = StockTransferLine.objects.all()
    serializer_class = StockTransferLineSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_stock_transfers'


class StockCountViewSet(viewsets.ModelViewSet):
    """Stock count viewset"""
    queryset = StockCount.objects.all()
    serializer_class = StockCountSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_stock_counts'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start stock count"""
        stock_count = self.get_object()
        
        # Update status
        if stock_count.status == 'draft':
            stock_count.status = 'in_progress'
            stock_count.save()
        
        serializer = self.get_serializer(stock_count)
        return Response(serializer.data)
    
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


class StockCountLineViewSet(viewsets.ModelViewSet):
    """Stock count line viewset"""
    queryset = StockCountLine.objects.all()
    serializer_class = StockCountLineSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_stock_counts'
    
    def perform_create(self, serializer):
        # Get system quantity from stock
        product = serializer.validated_data.get('product')
        stock_count = serializer.validated_data.get('stock_count')
        
        try:
            stock = Stock.objects.get(
                product=product,
                warehouse=stock_count.warehouse
            )
            system_quantity = stock.quantity
        except Stock.DoesNotExist:
            system_quantity = 0
        
        serializer.save(system_quantity=system_quantity)