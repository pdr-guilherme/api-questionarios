import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKeyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.id


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("edited at"), auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_("the email must be set"))
        email = self.normalize_email(email)
        other_fields.setdefault("role", User.RoleChoices.RESPONDENT)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("role", User.RoleChoices.ADMIN)

        if other_fields.get("is_staff") is not True:
            raise ValueError(_("superuser must have is_staff=True."))
        if other_fields.get("is_superuser") is not True:
            raise ValueError(_("superuser must have is_superuser=True."))
        if other_fields.get("role") != User.RoleChoices.ADMIN:
            raise ValueError(_("superuser must have role=User.RoleChoices.ADMIN."))
        return self.create_user(email, password, **other_fields)


class User(AbstractUser, UUIDPrimaryKeyModel, TimeStampedModel):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin", _("admin")
        RESPONDENT = "respondent", _("respondent")

    username = None
    first_name = None
    last_name = None

    email = models.EmailField(_("email"), max_length=255, unique=True)
    role = models.CharField(
        _("role"), max_length=10, choices=RoleChoices, default=RoleChoices.RESPONDENT
    )
    objects = CustomUserManager()  # type:ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("usuário")
        verbose_name_plural = _("usuários")
        ordering = ["email", "-created_at"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.role == self.RoleChoices.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)
