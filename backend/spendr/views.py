from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer
from utils.rate_limiter import rate_limit

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @rate_limit('account-list', limit=10, period=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @rate_limit('account-create', limit=5, period=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @rate_limit('account-retrieve', limit=10, period=60)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @rate_limit('account-update', limit=5, period=60)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @rate_limit('account-destroy', limit=5, period=60)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @rate_limit('category-list', limit=10, period=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @rate_limit('category-create', limit=5, period=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @rate_limit('category-retrieve', limit=10, period=60)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @rate_limit('category-update', limit=5, period=60)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @rate_limit('category-destroy', limit=5, period=60)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @rate_limit('transaction-list', limit=10, period=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @rate_limit('transaction-create', limit=5, period=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @rate_limit('transaction-retrieve', limit=10, period=60)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @rate_limit('transaction-update', limit=5, period=60)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @rate_limit('transaction-destroy', limit=5, period=60)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
