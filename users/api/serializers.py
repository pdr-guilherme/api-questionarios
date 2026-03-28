from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from rest_framework import serializers

from users.models import User


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
