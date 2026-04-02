import factory
from faker import Faker

from users.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for respondent `User` instances"""

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.email())
    role = User.RoleChoices.RESPONDENT
    password = "123456"


class AdminFactory(UserFactory):
    """Factory for admin `User` instances"""

    role = User.RoleChoices.ADMIN
