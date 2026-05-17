"""Customer and transaction ViewSets — portfolio-scoped, cursor-paginated."""

from rest_framework import mixins, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.customers.models import Customer, KYCStatus, Transaction
from apps.customers.serializers import CustomerSerializer, TransactionSerializer


class CustomerCursorPagination(CursorPagination):
    page_size = 50
    ordering = "-created_at"


class CustomerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List/retrieve customers in the authenticated RM's portfolio."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    pagination_class = CustomerCursorPagination

    def get_queryset(self):
        return (
            Customer.objects.filter(rm=self.request.user, kyc_status=KYCStatus.COMPLETE)
            .select_related("rm")
            .order_by("-created_at")
        )


class TransactionViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """List transactions for customers in the RM's portfolio."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = CustomerCursorPagination

    def get_queryset(self):
        return (
            Transaction.objects.filter(customer__rm=self.request.user)
            .select_related("customer")
            .order_by("-month")
        )
