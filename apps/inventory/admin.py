from django.contrib import admin
from .models import (
    ProductCategory, Product, ProductImage, Vendor, Warehouse, Stock, StockEntry,
    PurchaseOrder, PurchaseOrderLine, PurchaseReceipt, PurchaseReceiptLine,
    StockTransfer, StockTransferLine, StockCount, StockCountLine
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('full_code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'type', 'status', 'price', 'quantity', 'is_below_reorder_point', 'is_active')
    list_filter = ('type', 'status', 'category', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description', 'barcode', 'sku')
    inlines = [ProductImageInline, StockInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'order', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('product__name', 'alt_text')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact_person', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'address', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'reserved_quantity', 'available_quantity', 'location', 'last_count_date')
    list_filter = ('warehouse', 'last_count_date')
    search_fields = ('product__name', 'product__code', 'warehouse__name', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'type', 'quantity', 'reference', 'created_by', 'created_at')
    list_filter = ('type', 'warehouse', 'created_at')
    search_fields = ('product__name', 'product__code', 'reference')
    readonly_fields = ('created_by', 'created_at')


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 1


class PurchaseReceiptInline(admin.TabularInline):
    model = PurchaseReceipt
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'vendor', 'warehouse', 'status', 'total', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'warehouse', 'created_at')
    search_fields = ('number', 'vendor__name', 'notes')
    inlines = [PurchaseOrderLineInline, PurchaseReceiptInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'tax_amount', 'total')


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'product', 'quantity', 'unit_price', 'discount', 'total', 'received_quantity')
    list_filter = ('purchase_order__status', 'purchase_order__date')
    search_fields = ('purchase_order__number', 'product__name', 'product__code')
    readonly_fields = ('total', 'received_quantity')


class PurchaseReceiptLineInline(admin.TabularInline):
    model = PurchaseReceiptLine
    extra = 1


@admin.register(PurchaseReceipt)
class PurchaseReceiptAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'purchase_order', 'created_by', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('number', 'purchase_order__number', 'notes')
    inlines = [PurchaseReceiptLineInline]
    readonly_fields = ('created_by', 'created_at')


@admin.register(PurchaseReceiptLine)
class PurchaseReceiptLineAdmin(admin.ModelAdmin):
    list_display = ('purchase_receipt', 'purchase_order_line', 'product', 'quantity')
    list_filter = ('purchase_receipt__date')
    search_fields = ('purchase_receipt__number', 'product__name', 'product__code')


class StockTransferLineInline(admin.TabularInline):
    model = StockTransferLine
    extra = 1


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'from_warehouse', 'to_warehouse', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'from_warehouse', 'to_warehouse', 'created_at')
    search_fields = ('number', 'notes')
    inlines = [StockTransferLineInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(StockTransferLine)
class StockTransferLineAdmin(admin.ModelAdmin):
    list_display = ('stock_transfer', 'product', 'quantity')
    list_filter = ('stock_transfer__date', 'stock_transfer__status')
    search_fields = ('stock_transfer__number', 'product__name', 'product__code')


class StockCountLineInline(admin.TabularInline):
    model = StockCountLine
    extra = 1


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'warehouse', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'warehouse', 'created_at')
    search_fields = ('number', 'notes')
    inlines = [StockCountLineInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(StockCountLine)
class StockCountLineAdmin(admin.ModelAdmin):
    list_display = ('stock_count', 'product', 'system_quantity', 'counted_quantity', 'difference')
    list_filter = ('stock_count__date', 'stock_count__status')
    search_fields = ('stock_count__number', 'product__name', 'product__code')
    readonly_fields = ('system_quantity', 'difference')