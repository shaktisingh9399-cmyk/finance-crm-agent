"""Customer and transaction models for BankIQ CRM."""

import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import RelationshipManager


class KYCStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETE = "complete", "Complete"
    FAILED = "failed", "Failed"


class Customer(models.Model):
    """Bank customer assigned to a relationship manager."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rm = models.ForeignKey(
        RelationshipManager,
        on_delete=models.PROTECT,
        related_name="customers",
        db_index=True,
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    pan = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12)
    account_number = models.CharField(max_length=20)

    annual_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        db_index=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    credit_score = models.PositiveSmallIntegerField(
        db_index=True,
        validators=[MinValueValidator(300), MaxValueValidator(900)],
    )
    emi_ratio = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        db_index=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
    )
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)],
    )
    tenure_years = models.PositiveSmallIntegerField(default=0)
    savings_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    last_login = models.DateTimeField(null=True, blank=True, db_index=True)

    kyc_status = models.CharField(
        max_length=16,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING,
        db_index=True,
    )
    marketing_consent = models.BooleanField(default=False, db_index=True)
    do_not_contact = models.BooleanField(default=False, db_index=True)
    has_active_dispute = models.BooleanField(default=False)
    has_active_fd = models.BooleanField(default=False)
    loan_history = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=["annual_income", "credit_score"]),
            models.Index(fields=["credit_score", "emi_ratio"]),
            models.Index(fields=["kyc_status", "do_not_contact", "marketing_consent"]),
            models.Index(fields=["last_login", "tenure_years"]),
        ]

    def __str__(self) -> str:
        return f"Customer {self.id}"


class Transaction(models.Model):
    """Monthly aggregated transaction summary per customer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    month = models.DateField(db_index=True)
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    avg_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=["customer", "month"]),
        ]

    def __str__(self) -> str:
        return f"Txn {self.customer_id} — {self.month}"
