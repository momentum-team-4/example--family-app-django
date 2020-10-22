from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def _create_user(self, email, date_of_birth, password, **extra_fields):
        """
        Create and save a user with the given email, date of birth, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = User(email=email, date_of_birth=date_of_birth, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, date_of_birth, password, **extra_fields)

    def create_superuser(self, email, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, date_of_birth, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth', 'name']

    objects = UserManager()

    email = models.EmailField("Email address", unique=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    def get_full_name(self):
        """Replacing built-in get_full_name from AbstractUser"""
        return self.name

    def get_short_name(self):
        """Replacing built-in get_short_name from AbstractUser"""
        return self.name

class Circle(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(
        to=User,
        through='CircleMembership',
        related_name='circles'
    )

    def __str__(self):
        return self.name

class CircleRole(models.TextChoices):
    OWNER = 'OWNER', 'Owner'
    ADMIN = 'ADMIN', 'Admin'
    MEMBER = 'MEMBER', 'Member'

class CircleMembership(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='memberships')
    circle = models.ForeignKey(to=Circle, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=CircleRole.choices, default=CircleRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.circle}"

class Post(models.Model):
    body = models.TextField()
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    circle = models.ForeignKey(to=Circle, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
