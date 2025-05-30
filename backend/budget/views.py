from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, F 
from .models import Wallet, Category, Transaction, BudgetGoal, RecurringBill
from .serializers import WalletSerializer, CategorySerializer, TransactionSerializer, BudgetGoalSerializer, RecurringBillSerializer
from datetime import date, timedelta
from django.utils import timezone 
from django.db.models.functions import TruncMonth

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.user == request.user

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
    lookup_field = 'id' 

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

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
    lookup_field = 'id'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        wallet_id = self.request.query_params.get('wallet_id', None)
        category_id = self.request.query_params.get('category_id', None)
        transaction_type = self.request.query_params.get('type', None) 
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if wallet_id:
            queryset = queryset.filter(wallet_id=wallet_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'id'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class BudgetGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BudgetGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'id'

    def get_queryset(self):
        return BudgetGoal.objects.filter(user=self.request.user)

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
    lookup_field = 'id'

    def get_queryset(self):
        return RecurringBill.objects.filter(user=self.request.user)

class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate() 
        current_month = today.month
        current_year = today.year

        start_of_month = today.replace(day=1)
        if current_month == 12:
            end_of_month = date(current_year, 12, 31)
        else:
            end_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)

        total_balance = Wallet.objects.filter(user=user).aggregate(Sum('balance'))['balance__sum'] or 0

        income_this_month = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__range=[start_of_month, end_of_month]
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        expense_this_month = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=[start_of_month, end_of_month]
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        spending_by_category = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=[start_of_month, end_of_month],
            category__isnull=False 
        ).values(category_id=F('category__id'), category_name=F('category__name')).annotate(total_amount=Sum('amount')).order_by('-total_amount')

        overall_budget_goal_obj = BudgetGoal.objects.filter(
            user=user,
            month=current_month,
            year=current_year,
            category__isnull=True 
        ).first()
        overall_budget_amount = overall_budget_goal_obj.amount if overall_budget_goal_obj else 0
        overall_budget_progress_percent = 0 
        if overall_budget_amount > 0:
            overall_budget_progress_percent = (expense_this_month / overall_budget_amount) * 100

        category_budget_goals = BudgetGoal.objects.filter(
            user=user,
            month=current_month,
            year=current_year,
            category__isnull=False 
        ).select_related('category') 

        budget_goals_progress = []
        for goal in category_budget_goals:
            spent_in_category = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__range=[start_of_month, end_of_month],
                category=goal.category 
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            progress_percentage = 0
            if goal.amount > 0:
                progress_percentage = (spent_in_category / goal.amount) * 100

            budget_goals_progress.append({
                'goal_id': goal.id,
                'category_name': goal.category.name,
                'goal_amount': float(goal.amount), 
                'spent_amount': float(spent_in_category),
                'progress_percentage': float(progress_percentage),
                'is_overbudget': spent_in_category > goal.amount
            })

        upcoming_bills = []
        active_recurring_bills = RecurringBill.objects.filter(
            user=user,
            is_active=True
        ).select_related('category') 

        for bill in active_recurring_bills:
            if bill.due_day >= today.day:
                bill_date = date(current_year, current_month, bill.due_day)
                if bill_date >= today and bill_date <= today + timedelta(days=30): 
                    upcoming_bills.append({
                        'id': bill.id,
                        'name': bill.name,
                        'amount': float(bill.amount),
                        'due_date': bill_date.isoformat(),  
                        'category_name': bill.category.name if bill.category else None
                    })

            next_month_date_obj = today + timedelta(days=30) 
            next_due_date = None

            try:
                candidate_date_current_month = date(current_year, current_month, bill.due_day)
                if candidate_date_current_month >= today:
                    next_due_date = candidate_date_current_month
            except ValueError: 
                pass

            if not next_due_date or next_due_date < today: 
                if current_month == 12:
                    nm_month = 1
                    nm_year = current_year + 1
                else:
                    nm_month = current_month + 1
                    nm_year = current_year
                try:
                    candidate_date_next_month = date(nm_year, nm_month, bill.due_day)
                    if not next_due_date or candidate_date_next_month < next_due_date: 
                        next_due_date = candidate_date_next_month
                except ValueError:
                    pass

            if next_due_date and next_due_date <= today + timedelta(days=30):
                is_duplicate = False
                for existing_bill in upcoming_bills:
                    if existing_bill['id'] == bill.id and existing_bill['due_date'] == next_due_date.isoformat():
                        is_duplicate = True
                        break
                if not is_duplicate:
                    upcoming_bills.append({
                        'id': bill.id,
                        'name': bill.name,
                        'amount': float(bill.amount),
                        'due_date': next_due_date.isoformat(),
                        'category_name': bill.category.name if bill.category else None
                    })

        upcoming_bills.sort(key=lambda x: x['due_date'])
        upcoming_bills = upcoming_bills[:5] 

        alerts = []
        if overall_budget_goal_obj and expense_this_month > overall_budget_amount:
            alerts.append(f"Heads up! You've overspent your overall monthly budget by ₱{(expense_this_month - overall_budget_amount):.2f}.")

        for goal_progress in budget_goals_progress:
            if goal_progress['is_overbudget']:
                alerts.append(f"Alert! You've overspent on {goal_progress['category_name']} by ₱{(goal_progress['spent_amount'] - goal_progress['goal_amount']):.2f}.")
            elif goal_progress['progress_percentage'] > 80 and not goal_progress['is_overbudget']:
                alerts.append(f"You're almost at your {goal_progress['category_name']} budget limit ({goal_progress['progress_percentage']:.1f}% used).")

        if not Wallet.objects.filter(user=user).exists():
            alerts.append("You haven't added any wallets yet! Add one to start tracking your money.")
        if not Category.objects.filter(user=user).exists():
            alerts.append("No categories found. Create some expense and income categories to organize your transactions.")
        if not Transaction.objects.filter(user=user, date__month=current_month, date__year=current_year).exists():
            alerts.append(f"No transactions recorded for {today.strftime('%B %Y')} yet. Start adding your income and expenses!")


        return Response({
            'total_balance': float(total_balance), 
            'income_this_month': float(income_this_month),
            'expense_this_month': float(expense_this_month),
            'net_balance_this_month': float(income_this_month - expense_this_month),
            'spending_by_category': list(spending_by_category),
            'wallets': WalletSerializer(Wallet.objects.filter(user=user), many=True).data, 
            'recent_transactions': TransactionSerializer(
                Transaction.objects.filter(user=user).order_by('-date')[:5],
                many=True
            ).data,
            'current_month_str': today.strftime("%B %Y"), 
            'current_month_num': current_month,
            'current_year': current_year,
            'overall_budget_goal': float(overall_budget_amount),
            'overall_budget_progress': float(overall_budget_progress_percent), 
            'budget_goals_progress': budget_goals_progress, 
            'upcoming_bills': upcoming_bills,
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
            month_str = entry['month'].strftime('%Y-%m') 
            if month_str not in chart_data:
                chart_data[month_str] = {'income': 0.0, 'expense': 0.0} 
            chart_data[month_str][entry['transaction_type']] = float(entry['total']) 

        formatted_chart_data = [
            {'month': m, 'income': d['income'], 'expense': d['expense']}
            for m, d in chart_data.items()
        ]
        formatted_chart_data.sort(key=lambda x: x['month']) 

        return Response(formatted_chart_data, status=status.HTTP_200_OK)