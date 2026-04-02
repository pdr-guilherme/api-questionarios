from typing import cast

import pytest
from rest_framework.test import APIClient, APIRequestFactory

from users.models import User
from users.tests.factories import AdminFactory, UserFactory


@pytest.fixture(autouse=True)
def fast_hasher(settings):
    """
    Sets the default PASSWORD_HASHERS settings to use MD5, speeding up
    the registration time in tests
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def api_client():
    """Creates an `rest_framework.test.APIClient` instance"""
    return APIClient()


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
