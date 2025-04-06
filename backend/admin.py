from django.contrib import admin
from .models import *

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'type', 'balance', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'user__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'time', 'from_account', 'to_account', 'category')
    list_filter = ('time', 'category__type')
    search_fields = ('user__username', 'description')

@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'interval', 'next_due', 'active')
    list_filter = ('interval', 'active')
    search_fields = ('user__username', 'description')

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('person_name', 'amount')
    search_fields = ('person_name',)

# @admin.register(InvestmentType)
# class InvestmentTypeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     search_fields = ('name',)

# @admin.register(Investment)
# class InvestmentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'name', 'investment_type', 'amount_invested', 'current_value')
#     list_filter = ('investment_type',)
#     search_fields = ('name', 'user__username')

# @admin.register(InvestmentTransaction)
# class InvestmentTransactionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'investment', 'transaction_type', 'amount', 'date')
#     list_filter = ('transaction_type',)
#     search_fields = ('investment__name',)
