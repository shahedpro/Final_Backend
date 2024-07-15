# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView, 
    FlowerListView, FlowerDetailView, 
    OrderCreateView, OrderListView,
    AdminFlowerViewSet, AdminOrderViewSet, verify_email
)

router = DefaultRouter()
router.register(r'admin/flowers', AdminFlowerViewSet)
router.register(r'admin/orders', AdminOrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('flowers/', FlowerListView.as_view(), name='flower-list'),
    path('flowers/<int:pk>/', FlowerDetailView.as_view(), name='flower-detail'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('verify-email/<str:token>/', verify_email, name='verify-email'),
]
