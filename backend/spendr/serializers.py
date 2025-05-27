from rest_framework import serializers
from .models import Account, Category, Transaction, Budget 


class AccountSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username') 

    class Meta:
        model = Account
        fields = [
            'id', 'user', 'name', 'current_balance', 'account_type',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'created_at', 'updated_at'] # These are system-managed


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Display username as read-only

    class Meta:
        model = Category
        fields = [
            'id', 'user', 'name', 'type', 'icon_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Display username as read-only

    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'account', 'account_name', 'category', 'category_name',
            'amount', 'type', 'description', 'transaction_date',
            'related_transaction', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at'] # System-managed fields


class BudgetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') 
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)


    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_name', 'category_type',
            'budget_amount', 'start_date', 'end_date',
            'spent_amount', 'remaining_amount', 'is_over_budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 