from django.db import models
from django.conf import settings 
from django.utils import timezone 
from django.core.exceptions import ValidationError 
from django.db.models.signals import post_save, post_delete 
from django.dispatch import receiver 
from django.db.models import Sum 


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    ACCOUNT_TYPES = [
        ('Cash', 'Cash Wallet'),
        ('Bank', 'Bank Account'),
        ('Credit Card', 'Credit Card'),
        ('Investment', 'Investment Account'),
        ('Other', 'Other'),
    ]
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default='Bank')
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ['name'] 

    def __str__(self):
        return f"{self.user.username}'s {self.name} ({self.account_type})"


class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=100)

    CATEGORY_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    icon_name = models.CharField(max_length=50, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name', 'type')
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['type', 'name'] 

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2) 

    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'), 
    ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='expense')
    description = models.TextField(blank=True, null=True) 
    transaction_date = models.DateField(default=timezone.now) 

    related_transaction = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_pair'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.type.capitalize()}: {self.amount} from/to {self.account.name} on {self.transaction_date}"

    def clean(self):
        if self.type == 'transfer':
            if not self.related_transaction:
                raise ValidationError("Transfer transactions must have a related transaction.")
            if self.related_transaction and (self.related_transaction.type != 'transfer' or self.related_transaction.related_transaction != self):
                raise ValidationError("Related transaction for a transfer must also be a transfer and correctly linked.")
            if self.related_transaction == self:
                raise ValidationError("A transfer cannot be related to itself.")
        else:
            if self.related_transaction:
                raise ValidationError("Only transfer transactions can have a related transaction.")

        if self.type == 'income' or self.type == 'expense':
            if not self.category:
                raise ValidationError("Income and expense transactions must have a category.")
            if self.category and self.category.type != self.type:
                 raise ValidationError(f"Category type ('{self.category.type}') must match transaction type ('{self.type}').")
        elif self.type == 'transfer':
            if self.category:
                raise ValidationError("Transfer transactions should not have a category.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    if created: 
        if instance.type == 'income':
            instance.account.current_balance += instance.amount
        elif instance.type == 'expense':
            instance.account.current_balance -= instance.amount
        instance.account.save(update_fields=['current_balance'])

@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    if instance.type == 'income':
        instance.account.current_balance -= instance.amount
    elif instance.type == 'expense':
        instance.account.current_balance += instance.amount
    instance.account.save(update_fields=['current_balance'])


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category', 'start_date', 'end_date')
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        ordering = ['start_date', 'category__name']

    def __str__(self):
        return f"Budget for {self.category.name} from {self.start_date} to {self.end_date}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
        if self.category and self.category.type != 'expense':
            raise ValidationError("Budgets can only be set for expense categories.")

    @property
    def spent_amount(self):
        spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense', 
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date
        ).aggregate(total_spent=Sum('amount'))['total_spent']
        return spent if spent is not None else 0.00

    @property
    def remaining_amount(self):
        return self.budget_amount - self.spent_amount

    @property
    def is_over_budget(self):
        return self.spent_amount > self.budget_amount