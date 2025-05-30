from rest_framework import serializers
from .models import Wallet, Category, Transaction, BudgetGoal, RecurringBill

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'balance', 'currency', 'description', 'user', 'created_at', 'updated_at']

        read_only_fields = ['user', 'balance', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'error_messages': {'unique': 'A category with this name and type already exists for this user.'}}
        }

class TransactionSerializer(serializers.ModelSerializer):
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True) 

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'transaction_type', 'description', 'date',
            'wallet', 'wallet_name', 
            'category', 'category_name', 'category_type', 
            'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'wallet_name', 'category_name', 'category_type']

    def validate(self, data):
        if 'category' in data and data['category'] and data['category'].type != data['transaction_type']:
            raise serializers.ValidationError({
                'category': f"The selected category type ('{data['category'].type}') does not match the transaction type ('{data['transaction_type']}')."
            })
        return data

class BudgetGoalSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BudgetGoal
        fields = ['id', 'month', 'year', 'category', 'category_name', 'amount', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at', 'category_name']

    def validate(self, data):
        if not (1 <= data['month'] <= 12):
            raise serializers.ValidationError({"month": "Month must be between 1 and 12."})
        if not (2000 <= data['year'] <= 2100): 
            raise serializers.ValidationError({"year": "Year is out of a reasonable range."})

        if 'category' in data and data['category'] and data['category'].type != 'expense':
            raise serializers.ValidationError({
                'category': 'Budget goals can only be set for expense categories.'
            })
        return data

class RecurringBillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = RecurringBill
        fields = ['id', 'name', 'amount', 'due_day', 'category', 'category_name', 'is_active', 'notes', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at', 'category_name']

    def validate(self, data):
        if not (1 <= data['due_day'] <= 31):
            raise serializers.ValidationError({"due_day": "Due day must be between 1 and 31."})

        if 'category' in data and data['category'] and data['category'].type != 'expense':
            raise serializers.ValidationError({
                'category': 'Recurring bills should typically be associated with expense categories.'
            })
        return data