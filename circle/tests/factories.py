from datetime import date

import factory
from circle.models import Circle, CircleInvitation, CircleRole, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"user{n}@example.org")
    password = "testpassword"
    date_of_birth = factory.LazyFunction(date.today)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class CircleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Circle

    name = "Test Circle"

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.add_members(CircleRole.MEMBER, extracted)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.add_members(CircleRole.OWNER, extracted)

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.add_members(CircleRole.ADMIN, extracted)


class CircleInvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CircleInvitation

    role = CircleRole.MEMBER
    invitee = factory.SubFactory(UserFactory)
    circle = factory.SubFactory(CircleFactory)
