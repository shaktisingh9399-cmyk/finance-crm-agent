"""ViewSets for Relationship Manager accounts."""

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import RelationshipManager
from apps.accounts.serializers import RelationshipManagerSerializer


class RelationshipManagerViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """List/retrieve RM profiles — scoped to authenticated user for retrieve."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RelationshipManagerSerializer
    pagination_class = None

    def get_queryset(self):
        return RelationshipManager.objects.filter(pk=self.request.user.pk)
