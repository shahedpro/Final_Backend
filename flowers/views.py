# views.py

from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .serializers import RegisterSerializer, LoginSerializer, FlowerSerializer, OrderSerializer
from .models import Flower, Order
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse

def flowers(request):
    flowers = [
        {'name': 'Rose', 'price': 10.50, 'image': 'path/to/rose.jpg'},
        {'name': 'Tulip', 'price': 8.75, 'image': 'path/to/tulip.jpg'},
        # Add more flowers as needed
    ]
    return JsonResponse(flowers, safe=False)

# Admin Views
class AdminFlowerViewSet(viewsets.ModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
    permission_classes = [IsAdminUser]

class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        order = serializer.save()
        send_mail(
            'Order Status Update',
            f'Your order status has been updated to {order.status}.',
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
        )

# Order Views
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.flower.quantity -= 1
        order.flower.save()
        send_mail(
            'Order Confirmation',
            'Your order has been placed successfully.',
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
        )

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        verification_url = request.build_absolute_uri(
            reverse('verify-email', args=[token.key])
        )
        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"message": "User registered. Check your email to verify your account."})

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})

# Flower Views
class FlowerListView(generics.ListCreateAPIView):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer

class FlowerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer

# Email Verification View
def verify_email(request, token):
    user = get_object_or_404(User, auth_token__key=token)
    user.is_active = True
    user.save()
    return HttpResponse('Email verified successfully. You can now log in.')
