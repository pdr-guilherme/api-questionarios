from typing import cast

import pytest
from rest_framework.test import APIClient, APIRequestFactory

from apps.users.models import User
from apps.users.tests.factories import AdminFactory, UserFactory


@pytest.fixture(autouse=True)
def fast_hasher(settings):
    """
    Sets the default PASSWORD_HASHERS settings to use MD5, speeding up
    the registration time in tests
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def request_factory():
    """Creates an `rest_framework.test.APIRequestFactory` instance"""
    return APIRequestFactory()


@pytest.fixture
def admin_user():
    """Creates an admin user (role=`User.RoleChoices.ADMIN`)"""
    return cast(User, AdminFactory())


@pytest.fixture
def respondent_user():
    """Creates an respondent user (role=`User.RoleChoices.RESPONDENT`)"""
    return cast(User, UserFactory())


@pytest.fixture
def api_client():
    """Creates a `rest_framework.test.APIClient` instance for general use"""
    return APIClient()


@pytest.fixture
def admin_api_client(admin_user):
    """
    Creates a `rest_framework.test.APIClient` instance authenticated with `admin_user`
    """
    client = APIClient()
    client.force_authenticate(admin_user)
    return client


@pytest.fixture
def respondent_api_client(respondent_user):
    """
    Creates a `rest_framework.test.APIClient` instance authenticated
    with `respondent_user`
    """
    client = APIClient()
    client.force_authenticate(respondent_user)
    return client
