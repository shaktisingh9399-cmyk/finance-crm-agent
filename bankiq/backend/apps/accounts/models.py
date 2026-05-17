"""Relationship Manager user model — JWT-authenticated CRM users."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class RelationshipManager(AbstractUser):
    """Bank RM with portfolio-scoped customer access."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=32, unique=True, db_index=True)
    branch_code = models.CharField(max_length=16, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "Relationship Manager"
        verbose_name_plural = "Relationship Managers"

    def __str__(self) -> str:
        return f"{self.username} ({self.employee_id})"
