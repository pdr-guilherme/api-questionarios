from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.users.models import User
from apps.users.utils import create_password


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True, allow_blank=True)


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ["id", "email", "role"]
        read_only_fields = fields


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update(
            {
                "role": User.RoleChoices.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        user = adapter.save_user(request, user, self, commit=False)
        user.role = self.cleaned_data.get("role")
        user.is_staff = self.cleaned_data.get("is_staff")
        user.is_superuser = self.cleaned_data.get("is_superuser")
        user.save()

        self.custom_signup(request, user)
        return user


class RespondentCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = User
        fields = ["id", "email", "created_by"]
        read_only_fields = ["id", "created_by"]

    def validate_created_by(self, value):
        if not value.is_staff:
            raise serializers.ValidationError(
                _("Somente administradores podem cadastrar respondentes.")
            )

        return value

    def create(self, validated_data):
        email = validated_data["email"]
        created_by = validated_data["created_by"]

        password = create_password()

        user = User(
            email=email,
            created_by=created_by,
            role=User.RoleChoices.RESPONDENT,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        message = (
            f"Sua senha é: {password}\nÉ fortemente recomendado alterar sua "
            "senha após o primeiro login."
        )

        send_mail(
            subject=_("Sua conta foi criada"),
            message=_(message),
            from_email=None,
            recipient_list=[email],
        )

        return user


class RespondentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class RespondentDetailSerializer(RespondentListSerializer):
    class Meta(RespondentListSerializer.Meta):
        fields = [
            *RespondentListSerializer.Meta.fields,
            "created_at",
            "updated_at",
            "is_active",
            "last_login",
        ]
