from django.db import models
from django.conf import settings
from datetime import date, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

class BaseModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)ss')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class Wallet(BaseModel):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='PHP')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.currency} {self.balance})"

class Category(BaseModel):
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=7,
        choices=[('income', 'Income'), ('expense', 'Expense')],
        default='expense'
    )
    description = models.TextField(blank=True, null=True)
    # ADD THIS LINE: monthly_budget field
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                        help_text="Monthly budget goal for this category (for expense categories)")


    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('user', 'name', 'type')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(BaseModel):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(
        max_length=7,
        choices=[('income', 'Income'), ('expense', 'Expense')],
        default='expense'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_transactions')
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=date.today)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        sign = '+' if self.transaction_type == 'income' else '-'
        return f"{sign}{self.amount} ({self.category.name if self.category else 'No Category'}) - {self.wallet.name} on {self.date}"

@receiver(post_save, sender=Transaction)
def update_wallet_on_transaction_save(sender, instance, created, **kwargs):
    wallet = Wallet.objects.get(pk=instance.wallet.pk)

    if created:
        if instance.transaction_type == 'income':
            wallet.balance += instance.amount
        else:
            wallet.balance -= instance.amount
    else:
        try:
            # Need to get the old instance from the database before it's updated
            old_instance = sender.objects.get(pk=instance.pk)

            # Revert old amount from wallet
            if old_instance.transaction_type == 'income':
                wallet.balance -= old_instance.amount
            else:
                wallet.balance += old_instance.amount

            # Apply new amount to wallet
            if instance.transaction_type == 'income':
                wallet.balance += instance.amount
            else:
                wallet.balance -= instance.amount
        except sender.DoesNotExist:
            pass # Should not happen during an update
    wallet.save()

@receiver(post_delete, sender=Transaction)
def update_wallet_on_transaction_delete(sender, instance, **kwargs):
    wallet = Wallet.objects.get(pk=instance.wallet.pk)
    if instance.transaction_type == 'income':
        wallet.balance -= instance.amount
    else:
        wallet.balance += instance.amount
    wallet.save()

class BudgetGoal(BaseModel):
    month = models.PositiveSmallIntegerField(help_text="Month (1-12)")
    year = models.PositiveSmallIntegerField(help_text="Year (e.g., 2024)")
    # Note: While you have monthly_budget on Category, this BudgetGoal model
    # can be used for *overriding* a category's monthly budget for a specific month/year,
    # or for an overall monthly budget if category is null.
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='budget_goals',
        # limit_choices_to={'type': 'expense'} # Consider if you need budget goals for income categories
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'month', 'year', 'category')
        ordering = ['-year', '-month', 'category__name']

    def __str__(self):
        category_name = self.category.name if self.category else "Overall Monthly Budget"
        return f"{self.user.username}'s Goal: {category_name} for {self.month}/{self.year} - {self.amount}"

class RecurringBill(BaseModel):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_day = models.PositiveSmallIntegerField(help_text="Day of the month the bill is due (e.g., 1, 15, 30)")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recurring_bills',
        limit_choices_to={'type': 'expense'}
    )
    is_active = models.BooleanField(default=True, help_text="Is this recurring bill currently active?")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['due_day', 'name']
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} (₱{self.amount} due on day {self.due_day} of each month)"