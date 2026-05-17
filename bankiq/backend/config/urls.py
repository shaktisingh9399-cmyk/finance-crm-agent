"""Root URL configuration for BankIQ CRM API."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import RelationshipManagerViewSet
from apps.agent.views import AgentQueryViewSet
from apps.campaigns.views import CampaignViewSet, OutreachRecordViewSet
from apps.customers.views import CustomerViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r"accounts/rms", RelationshipManagerViewSet, basename="rm")
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"outreach", OutreachRecordViewSet, basename="outreach")
router.register(r"agent/query", AgentQueryViewSet, basename="agent-query")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include(router.urls)),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
