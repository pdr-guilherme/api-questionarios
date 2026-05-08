import pytest

from apps.core.models import UUIDPrimaryKeyModel


class FakeModel(UUIDPrimaryKeyModel):
    class Meta:
        app_label = "users_tests"


@pytest.mark.django_db
def test_uuid_primary_key_model_to_str():
    instance = FakeModel()
    assert str(instance) == str(instance.id)
