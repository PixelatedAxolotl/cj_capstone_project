from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User_Group(models.Model):
    GROUP_TYPE_CHOICES = [
        ('region', 'Region'),
        ('demographic', 'Demographic Group'),
    ]

    name = models.CharField(max_length=255, unique=True)
    date_added = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    date_added = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    groups = models.ManyToManyField(User_Group, blank=True, related_name='schools')
    survey_index = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.name

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