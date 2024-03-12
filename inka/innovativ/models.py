from django.db import models
from django.contrib.auth.models import User


class Position(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Job(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.position)


class customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name
