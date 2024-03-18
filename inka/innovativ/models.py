from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Munkakörök törzsadata
class Position(models.Model):
    name = models.CharField(max_length=150, unique=True)  # Munkakör megnevezése

    def __str__(self):
        return self.name


# Felhasználók - Munkakörhöz rendelve (egy Felhasználóhoz csak egy Munkakör tartozhat!)
class Job(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Felhasználó hozzárendelése
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  # Munkakör hozzárendelése

    def __str__(self):
        return str(self.user)


# Projektek törzsadata (egy Projekthez több Munkakör is tartozhat!)
class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Projekt megnevezése
    view_name = models.CharField(max_length=50, unique=True)  # Projekthez tartozó view definíció megnevezése


    def __str__(self):
        return self.name


# Munkakörökhöz tartozó Projektek (egy Munkakörhöz több Projekt is tartozhat!)
class PositionProject(models.Model):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, default=None)  # Munkakör hozzárendelése
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Projekt hozzárendelése

    def __str__(self):
        return str(self.project)


# Feladatok - Projethez rendelve
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, default=None)  # Projekt hozzárendelése
    comment = models.TextField(max_length=500, null=True)  # Megjegyzés
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja

    def __str__(self):
        return str(self.comment)


# Ügyfelek törzsadata
class Customer(models.Model):
    name = models.CharField(max_length=100)  # Ügyfél neve
    email = models.EmailField(max_length=50)  # Ügyfél email címe
    phone = models.CharField(max_length=15)  # Ügyfél telefonszáma

    def __str__(self):
        return self.name
