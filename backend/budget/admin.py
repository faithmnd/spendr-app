from django.contrib import admin
from .models import Wallet, Category, Transaction, BudgetGoal, RecurringBill

admin.site.register(Wallet)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(BudgetGoal)
admin.site.register(RecurringBill) 