import pytest

from apps.surveys.api.serializers import GrantAccessSerializer
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_grant_access_serializer_valid_user():
    user = UserFactory()
    data = {"user_id": str(user.id)}
    serializer = GrantAccessSerializer(data=data)
    assert serializer.is_valid()


def test_grant_access_serializer_invalid_user():
    data = {"user_id": ""}
    serializer = GrantAccessSerializer(data=data)
    assert not serializer.is_valid()
    assert "user_id" in serializer.errors
