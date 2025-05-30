from rest_framework import serializers
from .models import Wallet, Category, Transaction, BudgetGoal, RecurringBill
from decimal import Decimal
from datetime import date

class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.00'), required=False)
    
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'balance', 'currency', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'balance', 'created_at', 'updated_at']

    def validate_currency(self, value):
        valid_currencies = ['PHP', 'USD', 'EUR', 'GBP', 'JPY']
        if value not in valid_currencies:
            raise serializers.ValidationError(f"Invalid currency. Must be one of: {', '.join(valid_currencies)}")
        return value

class CategorySerializer(serializers.ModelSerializer):
    monthly_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.00'),
        required=False,
        default=Decimal('0.00')
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'description', 'monthly_budget', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'error_messages': {'unique': 'A category with this name and type already exists for this user.'}}
        }

    def validate(self, data):
        if 'type' in data and data['type'] == 'income' and data.get('monthly_budget', 0) > 0:
            raise serializers.ValidationError({
                'monthly_budget': 'Income categories cannot have a budget.'
            })
        return data

class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
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

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        return value

    def validate(self, data):
        # Ensure category type matches transaction type if a category is provided
        if 'category' in data and data['category'] and data['category'].type != data['transaction_type']:
            raise serializers.ValidationError({
                'category': f"The selected category type ('{data['category'].type}') does not match the transaction type ('{data['transaction_type']}')."
            })
        return data

class BudgetGoalSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BudgetGoal
        fields = ['id', 'month', 'year', 'category', 'category_name', 'amount', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at', 'category_name']

    def validate_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate_year(self, value):
        if not (2000 <= value <= 2100):
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return value

    def validate(self, data):
        if 'category' in data and data['category'] and data['category'].type != 'expense':
            raise serializers.ValidationError({
                'category': 'Budget goals can only be set for expense categories.'
            })

        # Check for duplicate budget goals
        if self.instance is None:  # Only check on creation
            existing = BudgetGoal.objects.filter(
                user=self.context['request'].user,
                month=data['month'],
                year=data['year'],
                category=data.get('category')
            ).exists()
            if existing:
                raise serializers.ValidationError(
                    "A budget goal already exists for this category and period."
                )
        return data

class RecurringBillSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    category_name = serializers.CharField(source='category.name', read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)

    class Meta:
        model = RecurringBill
        fields = [
            'id', 'name', 'amount', 'due_day', 'category', 'category_name',
            'wallet', 'wallet_name', 'description', 'is_active',
            'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'category_name', 'wallet_name']

    def validate_due_day(self, value):
        if not (1 <= value <= 31):
            raise serializers.ValidationError("Due day must be between 1 and 31.")
        return value