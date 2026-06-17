from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderReportListCreateView, BulkUploadExcelView, OrderReportDetailView, 
    ColumnVisibilityView, FirmViewSet, LocationViewSet, MerchantViewSet
)

# Naye master routes ke liye router
router = DefaultRouter()
router.register(r'firms', FirmViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'merchants', MerchantViewSet)

urlpatterns = [
    path('orders/', OrderReportListCreateView.as_view(), name='orders-list-create'),
    path('orders/upload/', BulkUploadExcelView.as_view(), name='orders-upload'),
    path('orders/<int:pk>/', OrderReportDetailView.as_view(), name='orders-detail'),
    path('column-policy/', ColumnVisibilityView.as_view(), name='column-policy'),
    
    # Ye line sabhi master APIs ko automatically add karne ke liye (/api/reports/firms/, etc.)
    path('', include(router.urls)),
]   