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
    SellerViewSet,
    InvoiceShipmentViewSet, 
    fetch_order_for_shipment,
    InvoiceShipmentUploadView,
    OrderSummaryView,
    ExportOrderReportsExcelView,
    ExportInvoiceShipmentExcelView,
    bulk_delete_orders,
    bulk_delete_invoices,
    upload_models_excel,
    ApprovalViewSet,
    GRPORecordViewSet,
    DownloadApprovalPDF,
    TicketViewSet,
    RefundRecordViewSet,
    cancel_order_to_refund
)

# Naye master routes ke liye router
router = DefaultRouter()
router.register(r'firms', FirmViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'merchants', MerchantViewSet)
router.register(r'models', ProductModelViewSet, basename='productmodel')
router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'grpo', GRPORecordViewSet, basename='grpo')
# Jahan aapne baaki router register kiye hain, wahi par add karein:
router.register(r'tickets', TicketViewSet, basename='ticket')

#approval path -----------
router.register(r'approvals', ApprovalViewSet, basename='approval')

#--------------INVOICE-SHIPMENT ROUTE --------------------
router.register(r'shipments', InvoiceShipmentViewSet, basename='shipments')
router.register(r'refunds', RefundRecordViewSet, basename='refund')

urlpatterns = [
    # bulk -delete path ---
    path('orders/bulk-delete/', bulk_delete_orders, name='bulk-delete-orders'),
    path('invoices/bulk-delete/', bulk_delete_invoices, name='bulk-delete-invoices'),
    path('models/upload/', upload_models_excel, name='upload_models_excel'),
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

    #excel download krne ke liye url path
    path('export/orders/', ExportOrderReportsExcelView.as_view(), name='export-orders'),
    path('export/invoices/', ExportInvoiceShipmentExcelView.as_view(), name='export-invoices'),
    path('approvals/<int:pk>/pdf/', DownloadApprovalPDF.as_view(), name='download-approval-pdf'),

    path('orders/<int:pk>/cancel/', cancel_order_to_refund, name='cancel-order'),

    
    # Ye line sabhi master APIs ko automatically add karne ke liye (/api/reports/firms/, etc.)
    path('', include(router.urls)),
]