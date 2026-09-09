import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    """Return a fresh API client with support for JSON requests and sessions."""
    return APIClient()
