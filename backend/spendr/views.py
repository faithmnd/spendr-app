from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle 
from django.db import models, transaction as db_transaction 
from django.db.models import Q 
from .models import Account, Category, Transaction, Budget
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        with db_transaction.atomic(): 
            transaction_instance = serializer.save(user=self.request.user)

            if transaction_instance.type == 'transfer':
                target_account_id = self.request.data.get('target_account') 
                if not target_account_id:
                    raise serializers.ValidationError("Transfer transactions require a 'target_account'.")

                try:
                    target_account = Account.objects.get(pk=target_account_id, user=self.request.user)
                except Account.DoesNotExist:
                    raise serializers.ValidationError("Target account not found or does not belong to the user.")

                paired_transaction = Transaction.objects.create(
                    user=self.request.user,
                    account=target_account,
                    category=None, 
                    amount=transaction_instance.amount,
                    type='transfer',
                    description=f"Transfer from {transaction_instance.account.name}. {transaction_instance.description}",
                    transaction_date=transaction_instance.transaction_date,
                )
                transaction_instance.related_transaction = paired_transaction
                paired_transaction.related_transaction = transaction_instance
                transaction_instance.save()
                paired_transaction.save()

                transaction_instance.account.current_balance -= transaction_instance.amount
                target_account.current_balance += transaction_instance.amount
                transaction_instance.account.save(update_fields=['current_balance'])
                target_account.save(update_fields=['current_balance'])


    def perform_update(self, serializer):
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        with db_transaction.atomic():
            if instance.type == 'transfer' and instance.related_transaction:
                paired_instance = instance.related_transaction
                paired_instance.related_transaction = None
                paired_instance.save() 
                paired_instance.delete() 
            super().perform_destroy(instance)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)