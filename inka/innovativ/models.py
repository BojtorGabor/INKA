from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from tinymce import models as tinymce_models


# Munkakörök törzsadata
class Position(models.Model):
    name = models.CharField(max_length=150, unique=True)  # Munkakör megnevezése

    def __str__(self):
        return self.name


# Felhasználók - Munkakörhöz rendelve (egy Felhasználóhoz több Munkakör is tartozhat!)
class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Felhasználó hozzárendelése
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  # Munkakör hozzárendelése

    def __str__(self):
        return f"{self.user} - {self.position.name}"


# A Felhasználó utoljára ebben a munkakörben dolgozott
class LastPosition(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Felhasználó hozzárendelése
    last_position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)  # Utolsó Position amiben dolgozott

    def __str__(self):
        return self.last_position.name


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


# Ügyfél projektjének célja
class Target(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Ügyfél projektjének finanszírozása
class Financing(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Ügyfél egyedi adatai
class Customer(models.Model):
    surname = models.CharField(max_length=100, default='')  # Ügyfél által megadott vezetékneve
    name = models.CharField(max_length=100, default='')  # Ügyfél által megadott keresztneve
    email = models.EmailField(max_length=50, unique=True, default='')  # Ügyfél által megadott email címe
    phone = models.CharField(max_length=15, default='')  # Ügyfél által megadott telefonszáma
    address = models.CharField(max_length=150, default='')  # Ügyfél által megadott cím
    surface = models.CharField(max_length=50, default='')  # Ügyfél által magadott tetőzet

    def __str__(self):
        return f"{self.surname} {self.name} (id: {self.id})"


# Ügyfél feladatszál adatai
class CustomerProject(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True, default=None)  # Projet célja
    financing = models.ForeignKey(Financing, on_delete=models.SET_NULL, null=True, default=None)  # Finanszírozás
    installation_address = models.CharField(max_length=150, default='')  # Telepítés címe
    request = models.TextField(max_length=1000)  # Ügyfél kérése, igénye
    latitude = models.FloatField(null=True, blank=True, default=0)  # Telepítés koordinátái
    longitude = models.FloatField(null=True, blank=True, default=0)  # Telepítés koordinátái

    def __str__(self):
        return f"{self.target} (id: {self.id})"


# Feladatok
class Task(models.Model):
    TYPE_CHOICES = (
        ('0:', 'Esemény'),
        ('1:', 'Figyelmeztetés'),
        ('2:', 'Új feladat'),
        ('3:', 'Folyamatban'),
        ('4:', 'Elkészült'),
        ('5:', 'Lezárt'),
    )
    COLOR_CHOICES = (
        ('0:', 'px-2'),
        ('1:', 'bg-secondary-subtle border border-secondary rounded-2 py-1 px-2'),
        ('2:', 'bg-danger-subtle border border-danger rounded-2 py-1 px-2'),
        ('3:', 'bg-warning-subtle border border-warning rounded-2 py-1 px-2'),
        ('4:', 'bg-success-subtle border border-success rounded-2 py-1 px-2'),
        ('5:', 'bg-success-subtle border border-primary rounded-2 py-1 px-2'),
    )

    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='0:')
    type_color = models.CharField(max_length=2, choices=COLOR_CHOICES, default='0:')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, default=None)  # Projekt hozzárendelése
    customer_project = models.ForeignKey(CustomerProject, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél projekt hozzárendelése
    comment = models.TextField(max_length=1000, null=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrehozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja
    completed_at = models.DateTimeField(null=True)  # befejezés időpontja
    deadline = models.DateTimeField(null=True, blank=True)  # beállított határidő

    def __str__(self):
        return f"{self.project} {self.customer_project} (id: {self.id})"

    @property
    def days_passed(self):  # számított mező: új és folyamatban feladatoknál mióta várakozik
        difference = timezone.now() -self.created_at
        return str(difference.days) + ' napja vár'


# Árajánlatok
class PriceOffer(models.Model):
    TYPE_CHOICES = (
        ('0:', 'Előzetes árajánlat'),
        ('1:', 'Kiküldött előzetes árajánlat'),
        ('2:', 'Elfogadott előzetes árajánlat'),
        ('3:', 'Végleges árajánlat'),
        ('4:', 'Kiküldött végleges árajánlat'),
        ('5:', 'Elfogadott végleges árajánlat'),
    )

    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='0:')
    customer_project = models.ForeignKey(CustomerProject, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél hozzárendelése
    file_path = models.CharField(max_length=100, null=True)  # PDF Árajánlat fájl útvonala
    currency = models.CharField(max_length=3, default='HUF')  # Valuta
    change_rating = models.DecimalField(max_digits=8, decimal_places=2, default=1)  # Ha nem HUF, akkor az átváltás HUF-ról arány
    comment = models.TextField(max_length=1000, null=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrehozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja

    def __str__(self):
        return f"{self.customer_project} {self.file_path} (id: {self.id})"


#  Termék csoportok
class ProductGroup(models.Model):
    group_name = models.CharField(max_length=100)  ## Termék csoport neve

    def __str__(self):
        return self.group_name


# Termékek
class Product(models.Model):
    UNIT_CHOICE = (
        ('db', 'darab'),
        ('m', 'méter'),
        ('cs', 'csomag'),
        ('pár', 'pár'),
    )
    group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True)  # Termék csoportja
    name = models.CharField(max_length=150)  # Termék neve
    unit = models.CharField(max_length=3, choices=UNIT_CHOICE, default='db')  # Mértékegysége
    price = models.DecimalField(max_digits=15, decimal_places=2)  # Egységár
    comment = models.TextField(max_length=1000, blank=True)  # Megjegyzés
    output_power = models.DecimalField(max_digits=12, decimal_places=3, default=0)  # Kimeneti teljesítmény kWattban

    def __str__(self):
        return self.name


#  Árajánlat tételei
class PriceOfferItem(models.Model):
    price_offer = models.ForeignKey(PriceOffer, on_delete=models.CASCADE)  # Árajánlat
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  # Termék
    amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # Mennyiség
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Egységár

    def __str__(self):
        return self.product.name if self.product else 'N/A'

    @property
    def value(self):  # számított mező: összérték
        return self.amount * self.price


# Felmérők
class Specifyer(models.Model):
    name = models.CharField(max_length=50)  # Felmérő neve

    def __str__(self):
        return self.name


# Felmérés, pontosítás
class Specify(models.Model):
    STATUS_CHOICE = (
        ('1:', 'várakozó (új)'),
        ('2:', 'várakozó (pótlás)'),
        ('3:', 'egyeztetve'),
        ('4:', 'elmaradt'),
        ('5:', 'megtörtént'),
    )
    customer_project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE)  # Ügyfél projektje
    specifyer = models.ForeignKey(Specifyer, on_delete=models.SET_NULL, null=True)  # Felmérő
    specify_date = models.DateTimeField(null=True, blank=True)  # Felmérés időpontja
    status = models.CharField(max_length=2, choices=STATUS_CHOICE, default='1:')  # Felmérés állapota
    comment = models.TextField(max_length=1000, blank=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrehozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja

    def __str__(self):
        return f'{self.customer_project} + {self.specify_date}'


# Email sablonok
class EmailTemplate(models.Model):
    title = models.CharField(max_length=150)  # Megnevezés
    subject = models.CharField(max_length=150, default='')  # Email tárgya
    content = tinymce_models.HTMLField()  # Email szövege

    def __str__(self):
        return self.title


class StandardText(models.Model):
    title = models.CharField(max_length=150)  # Megnevezés
    content = models.TextField(max_length=1000, blank=True)  # Szöveg

    def __str__(self):
        return self.title