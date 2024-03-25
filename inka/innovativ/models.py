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
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True,
                                 default=None)  # Munkakör hozzárendelése
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Projekt hozzárendelése

    def __str__(self):
        return str(self.project)


# Ügyfelek törzsadata
class Customer(models.Model):
    surname = models.CharField(max_length=100, default='')  # Ügyfél által megadott vezetékneve
    name = models.CharField(max_length=100, default='')  # Ügyfél által megadott keresztneve
    email = models.EmailField(max_length=50, default='')  # Ügyfél által megadott email címe
    phone = models.CharField(max_length=15, default='')  # Ügyfél által megadott telefonszáma
    address = models.CharField(max_length=150, default='')  # Ügyfél által megadott cím
    rooftop = models.CharField(max_length=50, default='')  # Ügyfél által magadott tetőzet

    def __str__(self):
        return f"{self.surname} {self.name} (id: {self.id})"


class Task(models.Model):
    TYPE_CHOICES = (
        ('0:', 'Esemény'),
        ('1:', 'Figyelmeztetés'),
        ('2:', 'Új feladat'),
        ('3:', 'Folyamatban'),
        ('4:', 'Elkészült'),
    )
    COLOR_CHOICES = (
        ('0:', 'px-2'),
        ('1:', 'bg-secondary-subtle border border-secondary rounded-2 py-1 px-2'),
        ('2:', 'bg-danger-subtle border border-danger rounded-2 py-1 px-2'),
        ('3:', 'bg-warning-subtle border border-warning rounded-2 py-1 px-2'),
        ('4:', 'bg-success-subtle border border-success rounded-2 py-1 px-2'),
    )

    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='0:')
    type_color = models.CharField(max_length=2, choices=COLOR_CHOICES, default='0:')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, default=None)  # Projekt hozzárendelése
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél hozzárendelése
    comment = models.TextField(max_length=500, null=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrahozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja
    completed_at = models.DateTimeField(null=True)  # befejezés időpontja

    def __str__(self):
        return str(self.comment)

    @property
    def days_passed(self):  # számított mező: új és folyamatban feladatoknál mióta várakozik
        difference = timezone.now() -self.created_at
        return str(difference.days) + ' napja várakozik'
