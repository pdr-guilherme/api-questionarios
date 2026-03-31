import pytest
from django.core import mail

from users.api.serializers import CustomRegisterSerializer, RespondentCreateSerializer
from users.models import User
from users.utils import create_password

data = {"email": "test@email.com"}
password = create_password()


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


@pytest.mark.django_db
def test_register_serializer_valid():
    data = {
        "email": "admin@email.com",
        "password1": password,
        "password2": password,
    }
    serializer = CustomRegisterSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_register_serializer_password_mismatch():
    password2 = create_password()
    data = {
        "email": "admin@email.com",
        "password1": password,
        "password2": password2,
    }
    serializer = CustomRegisterSerializer(data=data)

    assert not serializer.is_valid()


@pytest.mark.django_db
def test_register_serializer_creates_admin_user():
    data = {
        "email": "admin@email.com",
        "password1": password,
        "password2": password,
    }
    serializer = CustomRegisterSerializer(data=data)
    assert serializer.is_valid()

    user = serializer.save(request=None)
    assert isinstance(user, User)

    assert user.email == "admin@email.com"
    assert user.check_password(password)

    assert user.role == User.RoleChoices.ADMIN
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_get_cleaned_data_adds_admin_fields():
    serializer = CustomRegisterSerializer(
        data={
            "email": "admin@email.com",
            "password1": password,
            "password2": password,
        }
    )
    assert serializer.is_valid()

    data = serializer.get_cleaned_data()  # type:ignore

    assert data["role"] == User.RoleChoices.ADMIN
    assert data["is_staff"] is True
    assert data["is_superuser"] is True
