"""Admin registration for customers and transactions."""

from django.contrib import admin

from apps.customers.models import Customer, Transaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "rm", "credit_score", "kyc_status", "do_not_contact")
    list_filter = ("kyc_status", "marketing_consent", "do_not_contact")
    search_fields = ("id", "rm__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "month", "avg_balance")
    list_filter = ("month",)
