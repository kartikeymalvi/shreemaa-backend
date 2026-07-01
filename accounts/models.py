# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('ADMIN', 'Admin'),
#         ('USER', 'User'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

#     def __str__(self):
#         return f"{self.username} - {self.role}"

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# 🔥 NAYA MANAGER: Jo Superuser banate waqt automatic 'ADMIN' role dega
class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Yahan hum default value 'ADMIN' set kar rahe hain
        extra_fields.setdefault('role', 'ADMIN')
        
        # Uske baad Django ka jo normal superuser banane ka process hai, use chalne do
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    # 🔥 IMPORTANT: Naye manager ko apne model se jodna zaroori hai
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} - {self.role}"