from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderReportListCreateView, 
    BulkUploadExcelView, 
    OrderReportDetailView,
    ColumnVisibilityView, 
    FirmViewSet, 
    LocationViewSet, 
    MerchantViewSet, 
    ProductModelViewSet,
    InvoiceShipmentViewSet, 
    fetch_order_for_shipment,
    InvoiceShipmentUploadView,
    OrderSummaryView
)

# Naye master routes ke liye router
router = DefaultRouter()
router.register(r'firms', FirmViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'merchants', MerchantViewSet)
router.register(r'models', ProductModelViewSet, basename='models')

#--------------INVOICE-SHIPMENT ROUTE --------------------
router.register(r'shipments', InvoiceShipmentViewSet, basename='shipments')

urlpatterns = [
    #  UPLOAD WALE PATHS HAMESHA UPAR RAKHNE CHAHIYE 
    path('orders/upload/', BulkUploadExcelView.as_view(), name='orders-upload'),
    
    path('orders/', OrderReportListCreateView.as_view(), name='orders-list-create'),
    path('orders/<int:pk>/', OrderReportDetailView.as_view(), name='orders-detail'),
    path('column-policy/', ColumnVisibilityView.as_view(), name='column-policy'),
    
    #--------------INVOICE-SHIPMENT ROUTE --------------------
    path('fetch-order/<str:order_id>/', fetch_order_for_shipment, name='fetch-order'),
    
    #  YAHAN FIX KIYA HAI (reports/ prefix hata diya hai) 
    path('shipments/upload/', InvoiceShipmentUploadView.as_view(), name='upload_shipments'),
    path('order-summary/<int:pk>/', OrderSummaryView.as_view(), name='order-summary'),
    
    # Ye line sabhi master APIs ko automatically add karne ke liye (/api/reports/firms/, etc.)
    path('', include(router.urls)),
]