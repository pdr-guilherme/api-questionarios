import pytest
from django.core import mail

from users.api.serializers import RespondentCreateSerializer
from users.models import User

data = {"email": "test@email.com"}


@pytest.mark.django_db
def test_respondent_create_serializer_valid():
    serializer = RespondentCreateSerializer(data=data)
    assert serializer.is_valid()


def test_respondent_create_serializer_invalid(db):
    data = {"email": ""}
    serializer = RespondentCreateSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_respondent_create_serializer_creates_user(db):
    serializer = RespondentCreateSerializer(data=data)
    assert serializer.is_valid()

    user = serializer.save()
    assert isinstance(user, User)

    assert user.email == data["email"]
    assert user.role == User.RoleChoices.RESPONDENT


def test_respondent_create_serializer_user_created_with_password(db):
    serializer = RespondentCreateSerializer(data=data)
    serializer.is_valid()
    user = serializer.save()

    assert user.has_usable_password()  # type:ignore


def test_respondent_create_serializer_email_sent_on_create(db):
    serializer = RespondentCreateSerializer(data=data)
    serializer.is_valid()
    serializer.save()

    assert len(mail.outbox) == 1
