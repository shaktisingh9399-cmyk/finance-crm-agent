"""Customer serializers with mandatory PII masking."""

from rest_framework import serializers

from agent_core.enums import PIIField
from agent_core.tools.pii_masker import PIIMasker
from apps.customers.models import Customer, Transaction

_masker = PIIMasker()


class CustomerSerializer(serializers.ModelSerializer):
    """Customer list/detail — all PII fields returned masked."""

    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    aadhaar = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "pan",
            "aadhaar",
            "account_number",
            "annual_income",
            "credit_score",
            "emi_ratio",
            "age",
            "tenure_years",
            "savings_balance",
            "last_login",
            "kyc_status",
            "marketing_consent",
            "do_not_contact",
            "has_active_fd",
            "created_at",
        )
        read_only_fields = fields

    def _masked(self, obj: Customer, field: PIIField) -> str:
        field_name = field.value
        return _masker.mask_record({field_name: getattr(obj, field_name)}).get(field_name, "")

    def get_name(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.NAME)

    def get_phone(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.PHONE)

    def get_email(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.EMAIL)

    def get_pan(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.PAN)

    def get_aadhaar(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.AADHAAR)

    def get_account_number(self, obj: Customer) -> str:
        return self._masked(obj, PIIField.ACCOUNT_NUMBER)

    def validate_credit_score(self, value: int) -> int:
        if not 300 <= value <= 900:
            raise serializers.ValidationError("Credit score must be between 300 and 900.")
        return value

    def validate_emi_ratio(self, value) -> object:
        if value < 0 or value > 1:
            raise serializers.ValidationError("EMI ratio must be between 0.0 and 1.0.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction summary serializer."""

    class Meta:
        model = Transaction
        fields = (
            "id",
            "customer",
            "month",
            "total_debit",
            "total_credit",
            "avg_balance",
            "created_at",
        )
        read_only_fields = fields
