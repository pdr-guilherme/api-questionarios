import pytest

from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_user_to_str():
    user = UserFactory()
    assert str(user) == str(user.email)
