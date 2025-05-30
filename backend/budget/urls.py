from django.urls import path
from .views import (
    WalletListCreateView, WalletDetailView,
    CategoryListCreateView, CategoryDetailView,
    TransactionListCreateView, TransactionDetailView,
    BudgetGoalListCreateView, BudgetGoalDetailView,
    RecurringBillListCreateView, RecurringBillDetailView,
    DashboardSummaryView, MonthlySummaryView
)

urlpatterns = [
    path('wallets/', WalletListCreateView.as_view(), name='wallet-list-create'),
    path('wallets/<int:id>/', WalletDetailView.as_view(), name='wallet-detail'),

    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),

    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),

    path('budget-goals/', BudgetGoalListCreateView.as_view(), name='budgetgoal-list-create'),
    path('budget-goals/<int:id>/', BudgetGoalDetailView.as_view(), name='budgetgoal-detail'),

    path('recurring-bills/', RecurringBillListCreateView.as_view(), name='recurringbill-list-create'),
    path('recurring-bills/<int:id>/', RecurringBillDetailView.as_view(), name='recurringbill-detail'),

    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('monthly-summary/', MonthlySummaryView.as_view(), name='monthly-summary'),
]