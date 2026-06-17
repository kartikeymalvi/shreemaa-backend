from django.contrib import admin
from django.urls import path
from .views import CustomTokenObtainPairView, CreateUserByAdminView, UserListView, UserDeleteView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
]