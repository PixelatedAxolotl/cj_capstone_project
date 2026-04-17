from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import School


# AbstractUser to keep default functions of pass hashing, permissions, and admin interface
# TODO: add warning message when user selects internal role saying this will give them admin access 
class User(AbstractUser):
    ROLE_CHOICES = [
        ('internal', 'Career Jam Admin'),
        ('school_admin', 'School Administrator'),
        ('sponsor', 'Sponsor'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='administrators'
    )

    def save(self, *args, **kwargs):
        self.is_staff = (self.role == 'internal')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username