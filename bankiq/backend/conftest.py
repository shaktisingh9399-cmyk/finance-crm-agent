"""Pytest configuration for BankIQ backend tests."""

import pytest


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """Allow database access in tests."""
    with django_db_blocker.unblock():
        pass
