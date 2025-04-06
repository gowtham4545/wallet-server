from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.db import transaction as db_transaction
import datetime

class AccountType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    type = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type} - {self.name}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES,default=TRANSACTION_TYPES[0])
    amount = models.DecimalField(max_digits=15, decimal_places=2,default=0)
    time=models.TimeField(default=datetime.datetime.now)

    from_account = models.ForeignKey(
        'Account', on_delete=models.CASCADE, related_name='transactions_out', null=True, blank=True
    )
    to_account = models.ForeignKey(
        'Account', on_delete=models.CASCADE, related_name='transactions_in', null=True, blank=True
    )
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.time}"

    def save(self, *args, **kwargs):
        if self.transaction_type == 'income':
            if not self.to_account or self.from_account:
                raise ValueError("Income must have only a to_account")
            self.to_account.balance += self.amount
            self.to_account.save()
            
        elif self.transaction_type == 'expense':
            if not self.from_account or self.to_account:
                raise ValueError("Expense must have only a from_account")
            if self.amount > self.from_account.balance:
                raise ValueError("Expense > account balance")
            self.from_account.balance -= self.amount
            self.from_account.save()
            
        elif self.transaction_type == 'transfer':
            if not self.from_account or not self.to_account:
                raise ValueError("Transfer must have both from_account and to_account")
            if self.from_account == self.to_account:
                raise ValueError("Transfer accounts must be different")
            if self.amount > self.from_account.balance:
                raise ValueError("Transfer amt > account balance")
            self.from_account.balance -= self.amount
            self.from_account.save()
            self.to_account.balance += self.amount
            self.to_account.save()

        super().save(*args, **kwargs)
    
class RecurringTransaction(models.Model):
    INTERVAL_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2,default=0)
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='recurring_from')
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring_to')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)

    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    next_due = models.DateField(default=now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} every {self.interval}"

    def get_next_due(self):
        if self.interval == 'DAILY':
            return self.next_due + timedelta(days=1)
        elif self.interval == 'WEEKLY':
            return self.next_due + timedelta(weeks=1)
        elif self.interval == 'MONTHLY':
            return self.next_due + timedelta(days=30)
        elif self.interval == 'YEARLY':
            return self.next_due + timedelta(days=365)
        return self.next_due
    
class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Owner of the record
    person_name = models.CharField(max_length=100)  # To/From whom the money is lent/taken
    amount = models.DecimalField(max_digits=12, decimal_places=2,default=0)  # Positive = lent, Negative = borrowed
    note = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        status = "Lent" if self.amount > 0 else "Borrowed"
        return f"{self.user.username} {status} {abs(self.amount)} to/from {self.person_name}"
    

@receiver(pre_delete, sender=Transaction)
def rollback_transaction_balances(sender, instance, **kwargs):
    with db_transaction.atomic():
        if instance.transaction_type == "income" and instance.to_account:
            instance.to_account.balance -= instance.amount
            instance.to_account.save()
        elif instance.transaction_type == "expense" and instance.from_account:
            instance.from_account.balance += instance.amount
            instance.from_account.save()
        elif instance.transaction_type == "transfer":
            if instance.from_account:
                instance.from_account.balance += instance.amount
                instance.from_account.save()
            if instance.to_account:
                instance.to_account.balance -= instance.amount
                instance.to_account.save()
