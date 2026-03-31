import pytest

from users.models import UUIDPrimaryKeyModel
from users.tests.factories import UserFactory


class FakeModel(UUIDPrimaryKeyModel):
    class Meta:
        app_label = "users_tests"


@pytest.mark.django_db
def test_uuid_primary_key_model_to_str():
    instance = FakeModel()
    assert str(instance) == str(instance.id)


@pytest.mark.django_db
def test_user_factory_to_str():
    user = UserFactory()
    assert str(user) == str(user.email)
