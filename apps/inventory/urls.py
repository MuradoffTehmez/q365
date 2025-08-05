from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ProductViewSet, ProductImageViewSet, VendorViewSet, WarehouseViewSet,
    StockViewSet, StockEntryViewSet, PurchaseOrderViewSet, PurchaseOrderLineViewSet,
    PurchaseReceiptViewSet, PurchaseReceiptLineViewSet, StockTransferViewSet, StockTransferLineViewSet,
    StockCountViewSet, StockCountLineViewSet
)

router = DefaultRouter()
router.register('product-categories', ProductCategoryViewSet)
router.register('products', ProductViewSet)
router.register('product-images', ProductImageViewSet)
router.register('vendors', VendorViewSet)
router.register('warehouses', WarehouseViewSet)
router.register('stocks', StockViewSet)
router.register('stock-entries', StockEntryViewSet)
router.register('purchase-orders', PurchaseOrderViewSet)
router.register('purchase-order-lines', PurchaseOrderLineViewSet)
router.register('purchase-receipts', PurchaseReceiptViewSet)
router.register('purchase-receipt-lines', PurchaseReceiptLineViewSet)
router.register('stock-transfers', StockTransferViewSet)
router.register('stock-transfer-lines', StockTransferLineViewSet)
router.register('stock-counts', StockCountViewSet)
router.register('stock-count-lines', StockCountLineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]