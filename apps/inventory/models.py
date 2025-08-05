from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal
from core.models import User, Organization

class ProductCategory(models.Model):
    """Product category model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_code(self):
        """Get full category code including parent codes"""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code


class Product(models.Model):
    """Product model"""
    TYPE_CHOICES = (
        ('product', _('Product')),
        ('service', _('Service')),
        ('bundle', _('Bundle')),
    )
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('discontinued', _('Discontinued')),
        ('out_of_stock', _('Out of Stock')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='product'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    price = models.DecimalField(
        _('price'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    cost = models.DecimalField(
        _('cost'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    quantity = models.DecimalField(
        _('quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    reorder_point = models.DecimalField(
        _('reorder point'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    unit = models.CharField(_('unit'), max_length=20, default='pcs')
    barcode = models.CharField(_('barcode'), max_length=100, blank=True)
    sku = models.CharField(_('SKU'), max_length=100, blank=True)
    weight = models.DecimalField(
        _('weight'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Weight in kg')
    )
    dimensions = models.CharField(
        _('dimensions'),
        max_length=50,
        blank=True,
        help_text=_('Dimensions in LxWxH format')
    )
    warranty_period = models.IntegerField(
        _('warranty period'),
        null=True,
        blank=True,
        help_text=_('Warranty period in months')
    )
    notes = models.TextField(_('notes'), blank=True)
    image = models.ImageField(_('image'), upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_below_reorder_point(self):
        """Check if product quantity is below reorder point"""
        return self.quantity <= self.reorder_point


class ProductImage(models.Model):
    """Product image model"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(_('image'), upload_to='product_images/')
    alt_text = models.CharField(_('alt text'), max_length=255, blank=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    is_primary = models.BooleanField(_('is primary'), default=False)
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class Vendor(models.Model):
    """Vendor model"""
    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=50, unique=True)
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Warehouse(models.Model):
    """Warehouse model"""
    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=50, unique=True)
    address = models.TextField(_('address'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Stock(models.Model):
    """Stock model"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    quantity = models.DecimalField(
        _('quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    reserved_quantity = models.DecimalField(
        _('reserved quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    available_quantity = models.DecimalField(
        _('available quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    location = models.CharField(_('location'), max_length=100, blank=True)
    last_count_date = models.DateField(_('last count date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        unique_together = ('product', 'warehouse')
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"
    
    def save(self, *args, **kwargs):
        # Calculate available quantity
        self.available_quantity = self.quantity - self.reserved_quantity
        super().save(*args, **kwargs)
        
        # Update product quantity
        product = self.product
        total_quantity = Stock.objects.filter(product=product).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        product.quantity = total_quantity
        product.save()


class StockEntry(models.Model):
    """Stock entry model"""
    TYPE_CHOICES = (
        ('in', _('In')),
        ('out', _('Out')),
        ('adjustment', _('Adjustment')),
        ('transfer', _('Transfer')),
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_entries'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_entries'
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    quantity = models.DecimalField(
        _('quantity'),
        max_digits=10,
        decimal_places=2
    )
    reference = models.CharField(_('reference'), max_length=255, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stock_entries'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Stock Entry')
        verbose_name_plural = _('Stock Entries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.type} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update stock
        stock, created = Stock.objects.get_or_create(
            product=self.product,
            warehouse=self.warehouse,
            defaults={
                'quantity': 0,
                'reserved_quantity': 0
            }
        )
        
        if self.type == 'in':
            stock.quantity += self.quantity
        elif self.type == 'out':
            stock.quantity -= self.quantity
        elif self.type == 'adjustment':
            stock.quantity = self.quantity
        
        stock.save()


class PurchaseOrder(models.Model):
    """Purchase order model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('confirmed', _('Confirmed')),
        ('partial', _('Partially Received')),
        ('received', _('Received')),
        ('cancelled', _('Cancelled')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_rate = models.DecimalField(
        _('tax rate'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    shipping_cost = models.DecimalField(
        _('shipping cost'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_purchase_orders'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Purchase Order')
        verbose_name_plural = _('Purchase Orders')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.vendor.name}"
    
    def save(self, *args, **kwargs):
        # Calculate tax amount and total
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount + self.shipping_cost
        
        # Generate purchase order number if not provided
        if not self.number:
            last_po = PurchaseOrder.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_po and last_po.number.startswith(f"PO-{self.date.year}-"):
                try:
                    last_number = int(last_po.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"PO-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)


class PurchaseOrderLine(models.Model):
    """Purchase order line model"""
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchase_order_lines'
    )
    description = models.CharField(_('description'), max_length=255, blank=True)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=15, decimal_places=2)
    discount = models.DecimalField(_('discount'), max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=15, decimal_places=2, default=0)
    received_quantity = models.DecimalField(
        _('received quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('Purchase Order Line')
        verbose_name_plural = _('Purchase Order Lines')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.purchase_order.number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate total with discount and tax
        discount_amount = self.unit_price * (self.discount / 100)
        discounted_price = self.unit_price - discount_amount
        line_total = self.quantity * discounted_price
        tax_amount = line_total * (self.tax_rate / 100)
        self.total = line_total + tax_amount
        
        super().save(*args, **kwargs)
        
        # Update purchase order subtotal
        po = self.purchase_order
        subtotal = sum(line.total for line in po.lines.all())
        po.subtotal = subtotal
        po.save()


class PurchaseReceipt(models.Model):
    """Purchase receipt model"""
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='receipts'
    )
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_purchase_receipts'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Purchase Receipt')
        verbose_name_plural = _('Purchase Receipts')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.purchase_order.number}"
    
    def save(self, *args, **kwargs):
        # Generate purchase receipt number if not provided
        if not self.number:
            last_receipt = PurchaseReceipt.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_receipt and last_receipt.number.startswith(f"PR-{self.date.year}-"):
                try:
                    last_number = int(last_receipt.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"PR-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)


class PurchaseReceiptLine(models.Model):
    """Purchase receipt line model"""
    purchase_receipt = models.ForeignKey(
        PurchaseReceipt,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    purchase_order_line = models.ForeignKey(
        PurchaseOrderLine,
        on_delete=models.CASCADE,
        related_name='receipt_lines'
    )
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Purchase Receipt Line')
        verbose_name_plural = _('Purchase Receipt Lines')
    
    def __str__(self):
        return f"{self.purchase_receipt.number} - {self.purchase_order_line.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update purchase order line received quantity
        po_line = self.purchase_order_line
        total_received = sum(
            line.quantity for line in po_line.receipt_lines.all()
        )
        po_line.received_quantity = total_received
        po_line.save()
        
        # Update purchase order status
        po = po_line.purchase_order
        all_lines = po.lines.all()
        total_quantity = sum(line.quantity for line in all_lines)
        total_received = sum(line.received_quantity for line in all_lines)
        
        if total_received <= 0:
            po.status = 'sent'
        elif total_received < total_quantity:
            po.status = 'partial'
        else:
            po.status = 'received'
        
        po.save()
        
        # Create stock entry
        StockEntry.objects.create(
            product=po_line.product,
            warehouse=po.warehouse,
            type='in',
            quantity=self.quantity,
            reference=f"Purchase Receipt {self.purchase_receipt.number}",
            created_by=self.purchase_receipt.created_by
        )


class StockTransfer(models.Model):
    """Stock transfer model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('in_transit', _('In Transit')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_transfers_from'
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_transfers_to'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stock_transfers'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Stock Transfer')
        verbose_name_plural = _('Stock Transfers')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.from_warehouse.name} to {self.to_warehouse.name}"
    
    def save(self, *args, **kwargs):
        # Generate stock transfer number if not provided
        if not self.number:
            last_transfer = StockTransfer.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_transfer and last_transfer.number.startswith(f"ST-{self.date.year}-"):
                try:
                    last_number = int(last_transfer.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"ST-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)


class StockTransferLine(models.Model):
    """Stock transfer line model"""
    stock_transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_transfer_lines'
    )
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Stock Transfer Line')
        verbose_name_plural = _('Stock Transfer Lines')
    
    def __str__(self):
        return f"{self.stock_transfer.number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Create stock entries if transfer is completed
        if self.stock_transfer.status == 'completed':
            # Out from source warehouse
            StockEntry.objects.create(
                product=self.product,
                warehouse=self.stock_transfer.from_warehouse,
                type='out',
                quantity=self.quantity,
                reference=f"Stock Transfer {self.stock_transfer.number}",
                created_by=self.stock_transfer.created_by
            )
            
            # In to destination warehouse
            StockEntry.objects.create(
                product=self.product,
                warehouse=self.stock_transfer.to_warehouse,
                type='in',
                quantity=self.quantity,
                reference=f"Stock Transfer {self.stock_transfer.number}",
                created_by=self.stock_transfer.created_by
            )


class StockCount(models.Model):
    """Stock count model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    number = models.CharField(_('number'), max_length=50, unique=True)
    date = models.DateField(_('date'))
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_counts'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stock_counts'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Stock Count')
        verbose_name_plural = _('Stock Counts')
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.warehouse.name}"
    
    def save(self, *args, **kwargs):
        # Generate stock count number if not provided
        if not self.number:
            last_count = StockCount.objects.filter(
                date__year=self.date.year
            ).order_by('-number').first()
            
            if last_count and last_count.number.startswith(f"SC-{self.date.year}-"):
                try:
                    last_number = int(last_count.number.split('-')[-1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            self.number = f"SC-{self.date.year}-{new_number:05d}"
        
        super().save(*args, **kwargs)


class StockCountLine(models.Model):
    """Stock count line model"""
    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_count_lines'
    )
    system_quantity = models.DecimalField(
        _('system quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    counted_quantity = models.DecimalField(
        _('counted quantity'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    difference = models.DecimalField(
        _('difference'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Stock Count Line')
        verbose_name_plural = _('Stock Count Lines')
    
    def __str__(self):
        return f"{self.stock_count.number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate difference
        self.difference = self.counted_quantity - self.system_quantity
        
        super().save(*args, **kwargs)
        
        # Create stock adjustment if stock count is completed
        if self.stock_count.status == 'completed' and self.difference != 0:
            StockEntry.objects.create(
                product=self.product,
                warehouse=self.stock_count.warehouse,
                type='adjustment',
                quantity=self.counted_quantity,
                reference=f"Stock Count {self.stock_count.number}",
                created_by=self.stock_count.created_by
            )
            
            # Update stock last count date
            try:
                stock = Stock.objects.get(
                    product=self.product,
                    warehouse=self.stock_count.warehouse
                )
                stock.last_count_date = self.stock_count.date
                stock.save()
            except Stock.DoesNotExist:
                pass