"""Campaign and outreach ViewSets."""

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.campaigns.models import Campaign, OutreachRecord
from apps.campaigns.serializers import CampaignSerializer, OutreachRecordSerializer


class CampaignViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD campaigns owned by the authenticated RM."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        return Campaign.objects.filter(created_by=self.request.user).order_by("-created_at")

    def perform_create(self, serializer) -> None:
        serializer.save(created_by=self.request.user)


class OutreachRecordViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List outreach records for campaigns owned by the authenticated RM."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OutreachRecordSerializer

    def get_queryset(self):
        return (
            OutreachRecord.objects.filter(campaign__created_by=self.request.user)
            .select_related("campaign", "customer")
            .order_by("-created_at")
        )
