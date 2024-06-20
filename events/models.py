from django.db import models

# Create your models here.

class Event(models.Model):
    date = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    event = models.TextField()
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.title
