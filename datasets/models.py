from django.db import models

# Create your models here.
class Dataset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    


    def __str__(self):
        return self.name