import pytest

from users.models import User


@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(email="test@email.com", password="123456")  # type:ignore

    assert user.email == "test@email.com"
    assert user.role == User.RoleChoices.RESPONDENT
    assert user.check_password("123456")
    assert user.is_active is True


@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError, match="the email must be set"):
        User.objects.create_user(email=None, password="123456")  # type:ignore


@pytest.mark.django_db
def test_create_user_normalizes_email():
    user = User.objects.create_user(email="TEST@EMAIL.COM", password="123456")  # type:ignore

    assert user.email == "TEST@email.com" or user.email.lower() == "test@email.com"


@pytest.mark.django_db
def test_create_user_default_role():
    user = User.objects.create_user(email="test@email.com", password="123456")  # type:ignore

    assert user.role == User.RoleChoices.RESPONDENT


@pytest.mark.django_db
def test_create_superuser_success():
    user = User.objects.create_superuser(email="admin@email.com", password="123456")  # type:ignore

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.role == User.RoleChoices.ADMIN
    assert user.is_active is True


@pytest.mark.django_db
def test_create_superuser_without_staff():
    with pytest.raises(ValueError, match="is_staff=True"):
        User.objects.create_superuser(
            email="admin@email.com", password="123456", is_staff=False
        )  # type:ignore


@pytest.mark.django_db
def test_create_superuser_without_superuser():
    with pytest.raises(ValueError, match="is_superuser=True"):
        User.objects.create_superuser(
            email="admin@email.com", password="123456", is_superuser=False
        )  # type:ignore


@pytest.mark.django_db
def test_create_superuser_with_wrong_role():
    with pytest.raises(ValueError, match="role=User.RoleChoices.ADMIN"):
        User.objects.create_superuser(
            email="admin@email.com", password="123456", role=User.RoleChoices.RESPONDENT
        )  # type:ignore
