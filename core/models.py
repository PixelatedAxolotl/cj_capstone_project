from django.db import models


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
