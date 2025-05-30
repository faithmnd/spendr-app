# backend/budget/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, F, Q # Import Q for complex queries
from .models import Wallet, Category, Transaction, BudgetGoal, RecurringBill
from .serializers import (
    WalletSerializer, CategorySerializer, TransactionSerializer,
    BudgetGoalSerializer, RecurringBillSerializer
)
from datetime import date, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth
from calendar import monthrange # Import monthrange for end_of_month calculations

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    Assumes the object has a 'user' attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user

# --- Wallet Views ---
class WalletListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk' # Use 'pk' to align with default DRF behavior and urls.py

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

# --- Category Views ---
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk' # Use 'pk' to align with default DRF behavior and urls.py

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

# --- Transaction Views ---
class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        wallet_id = self.request.query_params.get('wallet_id', None)
        category_id = self.request.query_params.get('category_id', None)
        transaction_type = self.request.query_params.get('type', None)
        start_date_str = self.request.query_params.get('start_date', None)
        end_date_str = self.request.query_params.get('end_date', None)

        if wallet_id:
            queryset = queryset.filter(wallet_id=wallet_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        try:
            if start_date_str:
                start_date = date.fromisoformat(start_date_str)
                queryset = queryset.filter(date__gte=start_date)
            if end_date_str:
                end_date = date.fromisoformat(end_date_str)
                queryset = queryset.filter(date__lte=end_date)
        except ValueError:
            # Handle invalid date format gracefully
            return queryset.none() # Return empty queryset if dates are invalid

        return queryset.order_by('-date', '-created_at') # Add default ordering

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        # Update wallet balance upon transaction creation
        wallet = transaction.wallet
        if transaction.transaction_type == 'income':
            wallet.balance += transaction.amount
        else: # expense
            wallet.balance -= transaction.amount
        wallet.save()

class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk' # Use 'pk'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Reverse wallet balance update on deletion
        wallet = instance.wallet
        if instance.transaction_type == 'income':
            wallet.balance -= instance.amount
        else: # expense
            wallet.balance += instance.amount
        wallet.save()
        instance.delete()

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_amount = old_instance.amount
        old_type = old_instance.transaction_type
        old_wallet = old_instance.wallet

        new_transaction = serializer.save(user=self.request.user) # Save the updated transaction

        # Revert old amount from old wallet
        if old_type == 'income':
            old_wallet.balance -= old_amount
        else: # expense
            old_wallet.balance += old_amount
        old_wallet.save() # Save the old wallet first

        # Apply new amount to new wallet (could be same wallet)
        new_wallet = new_transaction.wallet
        if new_transaction.transaction_type == 'income':
            new_wallet.balance += new_transaction.amount
        else: # expense
            new_wallet.balance -= new_transaction.amount
        new_wallet.save()

# --- BudgetGoal Views ---
class BudgetGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow filtering by month and year
        queryset = BudgetGoal.objects.filter(user=self.request.user)
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk' # Use 'pk'

    def get_queryset(self):
        return BudgetGoal.objects.filter(user=self.request.user)

# --- RecurringBill Views ---
class RecurringBillListCreateView(generics.ListCreateAPIView):
    serializer_class = RecurringBillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringBill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecurringBillDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurringBillSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk' # Use 'pk'

    def get_queryset(self):
        return RecurringBill.objects.filter(user=self.request.user)

# --- Custom API Views ---

class TransferFundsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        from_wallet_id = request.data.get('from_wallet')
        to_wallet_id = request.data.get('to_wallet')
        amount = request.data.get('amount')
        description = request.data.get('description', 'Funds Transfer')

        if not all([from_wallet_id, to_wallet_id, amount]):
            return Response({"detail": "Missing required fields: from_wallet, to_wallet, amount."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if str(from_wallet_id) == str(to_wallet_id): # Compare as strings to avoid type issues
            return Response({"detail": "Cannot transfer funds to the same wallet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_wallet = Wallet.objects.get(id=from_wallet_id, user=user)
            to_wallet = Wallet.objects.get(id=to_wallet_id, user=user)
        except Wallet.DoesNotExist:
            return Response({"detail": "One or both wallets not found or do not belong to the user."}, status=status.HTTP_404_NOT_FOUND)

        if from_wallet.balance < amount:
            return Response({"detail": "Insufficient funds in source wallet."}, status=status.HTTP_400_BAD_REQUEST)

        # Perform the transfer
        # Use F() expressions for atomic updates to prevent race conditions
        from_wallet.balance = F('balance') - amount
        to_wallet.balance = F('balance') + amount
        from_wallet.save(update_fields=['balance'])
        to_wallet.save(update_fields=['balance'])
        # Refresh from DB after atomic update if you need current balance immediately
        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()


        # Create two transactions for audit trail
        Transaction.objects.create(
            user=user,
            wallet=from_wallet,
            amount=amount,
            transaction_type='expense', # Outflow from source wallet
            description=f"Transfer to {to_wallet.name}: {description}",
            date=timezone.localdate() # Use localdate for consistency
        )
        Transaction.objects.create(
            user=user,
            wallet=to_wallet,
            amount=amount,
            transaction_type='income', # Inflow to destination wallet
            description=f"Transfer from {from_wallet.name}: {description}",
            date=timezone.localdate()
        )

        return Response({"message": "Funds transferred successfully!",
                         "from_wallet_new_balance": float(from_wallet.balance),
                         "to_wallet_new_balance": float(to_wallet.balance)},
                        status=status.HTTP_200_OK)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate()
        current_month = today.month
        current_year = today.year

        # Get start and end of the current month
        start_of_month = date(current_year, current_month, 1)
        _, num_days = monthrange(current_year, current_month)
        end_of_month = date(current_year, current_month, num_days)

        # 1. Total Wallet Balance
        total_balance = Wallet.objects.filter(user=user).aggregate(Sum('balance'))['balance__sum'] or 0.00
        total_balance = float(f"{total_balance:.2f}")

        # 2. Income/Expense this Month
        income_this_month = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__range=[start_of_month, end_of_month]
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        income_this_month = float(f"{income_this_month:.2f}")

        expense_this_month = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=[start_of_month, end_of_month]
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        expense_this_month = float(f"{expense_this_month:.2f}")

        net_balance_this_month = float(f"{(income_this_month - expense_this_month):.2f}")

        # 3. Wallets
        wallets_data = WalletSerializer(Wallet.objects.filter(user=user), many=True).data

        # 4. Spending by Category and Budget Goals Progress
        # Get all expense categories for the user
        expense_categories = Category.objects.filter(user=user, type='expense')

        spending_by_category_data = []
        budget_goals_progress_data = []

        # Overall budget goal for the current month/year from BudgetGoal model
        # Prioritize an explicit BudgetGoal for overall if it exists
        overall_budget_goal_obj = BudgetGoal.objects.filter(
            user=user,
            month=current_month,
            year=current_year,
            category__isnull=True # For overall budget
        ).first()
        overall_budget_amount = float(overall_budget_goal_obj.amount) if overall_budget_goal_obj else 0.00

        # If no explicit overall budget, sum up default monthly budgets from categories
        if overall_budget_amount == 0.00:
            # Sum up default monthly_budget from expense categories that have one
            overall_budget_amount = expense_categories.filter(monthly_budget__gt=0).aggregate(Sum('monthly_budget'))['monthly_budget__sum'] or 0.00
            overall_budget_amount = float(f"{overall_budget_amount:.2f}")


        overall_budget_progress_percent = (expense_this_month / overall_budget_amount) * 100 if overall_budget_amount > 0 else (100 if expense_this_month > 0 else 0)
        overall_budget_progress_percent = float(f"{overall_budget_progress_percent:.2f}")


        for category in expense_categories: # Iterate through expense categories
            spent_amount_for_category = Transaction.objects.filter(
                user=user,
                category=category,
                transaction_type='expense',
                date__range=[start_of_month, end_of_month]
            ).aggregate(Sum('amount'))['amount__sum'] or 0.00
            spent_amount_for_category = float(f"{spent_amount_for_category:.2f}")

            spending_by_category_data.append({
                "category_id": category.id,
                "category_name": category.name,
                "total_amount": spent_amount_for_category
            })

            # Determine the budget goal for this specific category for the current month/year
            # Check for a specific BudgetGoal override first
            specific_category_goal = BudgetGoal.objects.filter(
                user=user,
                month=current_month,
                year=current_year,
                category=category
            ).first()

            category_goal_amount = float(specific_category_goal.amount) if specific_category_goal else float(category.monthly_budget or 0.00)
            category_goal_amount = float(f"{category_goal_amount:.2f}")

            progress_percentage = (spent_amount_for_category / category_goal_amount) * 100 if category_goal_amount > 0 else (100 if spent_amount_for_category > 0 else 0)
            progress_percentage = float(f"{progress_percentage:.2f}")
            is_overbudget = spent_amount_for_category > category_goal_amount and category_goal_amount > 0

            budget_goals_progress_data.append({
                "category_id": category.id, # Use category_id for consistent naming
                "category_name": category.name,
                "goal_amount": category_goal_amount,
                "spent_amount": spent_amount_for_category,
                "progress_percentage": progress_percentage,
                "is_overbudget": is_overbudget
            })

        # 5. Recent Transactions (last 5)
        recent_transactions_data = TransactionSerializer(
            Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:5],
            many=True
        ).data

        # 6. Upcoming Bills (within the next 30 days, or current month if it's past due_day)
        upcoming_bills_data = []
        active_recurring_bills = RecurringBill.objects.filter(user=user, is_active=True).select_related('category')

        for bill in active_recurring_bills:
            # Check for current month's due date
            try:
                due_date_this_month = date(current_year, current_month, bill.due_day)
                if due_date_this_month >= today:
                    upcoming_bills_data.append({
                        "id": bill.id,
                        "name": bill.name,
                        "amount": float(bill.amount),
                        "due_date": due_date_this_month.isoformat(),
                        "category_name": bill.category.name if bill.category else None,
                    })
            except ValueError:
                # day is invalid for current month (e.g., Feb 30) - ignore this month's instance
                pass

            # Check for next month's due date (if current month's is past or invalid)
            next_month = current_month + 1 if current_month < 12 else 1
            next_year = current_year if current_month < 12 else current_year + 1
            try:
                due_date_next_month = date(next_year, next_month, bill.due_day)
                # Only add if it's within the next 30 days from today and not already added from current month
                if due_date_next_month >= today and due_date_next_month <= today + timedelta(days=30):
                    # Check if this bill (by ID and exact date) is already in upcoming_bills_data
                    is_duplicate = False
                    for existing_bill in upcoming_bills_data:
                        if existing_bill['id'] == bill.id and existing_bill['due_date'] == due_date_next_month.isoformat():
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        upcoming_bills_data.append({
                            "id": bill.id,
                            "name": bill.name,
                            "amount": float(bill.amount),
                            "due_date": due_date_next_month.isoformat(),
                            "category_name": bill.category.name if bill.category else None,
                        })
            except ValueError:
                pass # day is invalid for next month - ignore

        # Sort and limit upcoming bills
        upcoming_bills_data.sort(key=lambda x: x['due_date'])
        upcoming_bills_data = upcoming_bills_data[:5] # Limit to top 5 upcoming bills

        # 7. Alerts
        alerts = []
        if overall_budget_amount > 0 and expense_this_month > overall_budget_amount:
            alerts.append(f"Heads up! You've overspent your overall monthly budget by ₱{(expense_this_month - overall_budget_amount):.2f}.")

        for goal_progress in budget_goals_progress_data:
            if goal_progress['is_overbudget']:
                alerts.append(f"Alert! You've overspent on '{goal_progress['category_name']}' by ₱{(goal_progress['spent_amount'] - goal_progress['goal_amount']):.2f}.")
            elif goal_progress['progress_percentage'] > 80 and not goal_progress['is_overbudget']:
                alerts.append(f"You're almost at your '{goal_progress['category_name']}' budget limit ({goal_progress['progress_percentage']:.1f}% used).")

        # General usage alerts
        if not Wallet.objects.filter(user=user).exists():
            alerts.append("You haven't added any wallets yet! Add one to start tracking your money.")
        if not Category.objects.filter(user=user).exists():
            alerts.append("No categories found. Create some expense and income categories to organize your transactions.")
        if not Transaction.objects.filter(user=user, date__range=[start_of_month, end_of_month]).exists():
            alerts.append(f"No transactions recorded for {today.strftime('%B %Y')} yet. Start adding your income and expenses!")


        return Response({
            'total_balance': total_balance,
            'income_this_month': income_this_month,
            'expense_this_month': expense_this_month,
            'net_balance_this_month': net_balance_this_month,
            'spending_by_category': spending_by_category_data,
            'wallets': wallets_data,
            'recent_transactions': recent_transactions_data,
            'current_month_str': today.strftime("%B %Y"),
            'current_month_num': current_month,
            'current_year': current_year,
            'overall_budget_goal': overall_budget_amount,
            'overall_budget_progress': overall_budget_progress_percent,
            'budget_goals_progress': budget_goals_progress_data,
            'upcoming_bills': upcoming_bills_data,
            'alerts': alerts,
        }, status=status.HTTP_200_OK)


class MonthlySummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        monthly_summary = Transaction.objects.filter(user=user) \
            .annotate(month=TruncMonth('date')) \
            .values('month', 'transaction_type') \
            .annotate(total=Sum('amount')) \
            .order_by('month', 'transaction_type')

        chart_data = {}
        for entry in monthly_summary:
            month_str = entry['month'].strftime('%Y-%m') # Format for consistent key
            if month_str not in chart_data:
                chart_data[month_str] = {'income': 0.0, 'expense': 0.0}
            # Ensure amounts are floats for JSON serialization
            chart_data[month_str][entry['transaction_type']] = float(entry['total'])

        # Convert dictionary to a list of objects for frontend charting libraries
        formatted_chart_data = [
            {'month': m, 'income': d['income'], 'expense': d['expense']}
            for m, d in chart_data.items()
        ]
        # Sort by month chronologically
        formatted_chart_data.sort(key=lambda x: x['month'])

        return Response(formatted_chart_data, status=status.HTTP_200_OK)