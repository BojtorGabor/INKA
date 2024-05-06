from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from tinymce import models as tinymce_models


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
    email = models.EmailField(max_length=50, unique=True, default='')  # Ügyfél által megadott email címe
    phone = models.CharField(max_length=15, default='')  # Ügyfél által megadott telefonszáma
    address = models.CharField(max_length=150, default='')  # Ügyfél által megadott cím
    surface = models.CharField(max_length=50, default='')  # Ügyfél által magadott tetőzet
    installation_address = models.CharField(max_length=150, blank=True, default='')  # Telepítés címe

    def __str__(self):
        return f"{self.surname} {self.name} (id: {self.id})"


# Feledatok
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
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél hozzárendelése
    comment = models.TextField(max_length=1000, null=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrehozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja
    completed_at = models.DateTimeField(null=True)  # befejezés időpontja

    def __str__(self):
        return str(self.comment)

    @property
    def days_passed(self):  # számított mező: új és folyamatban feladatoknál mióta várakozik
        difference = timezone.now() -self.created_at
        return str(difference.days) + ' napja vár'


# Email sablonok
class EmailTemplate(models.Model):
    title = models.CharField(max_length=150)
    subject = models.CharField(max_length=150, default='')
    content = tinymce_models.HTMLField()

    def __str__(self):
        return self.title


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

    CURRENCY_CHOICE = (
        ('HUF', 'Forint'),
        ('EUR', 'Euro'),
        ('USD', 'Dollár'),
    )

    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='0:')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, default=None)  # Ügyfél hozzárendelése
    file_path = models.CharField(max_length=100, null=True, blank=True)  # PDF Árajánlat fájl útvonala
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICE, default='HUF')  # Valuta
    comment = models.TextField(max_length=1000, null=True)  # Megjegyzés
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User aki létrehozta
    created_at = models.DateTimeField(default=timezone.now)  # létrehozás időpontja

    def __str__(self):
        return str(self.file_path)


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
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Egységár forintban
    comment = models.TextField(max_length=1000, null=True, blank=True)  # Megjegyzés

    def __str__(self):
        return self.name


#  Árajánlat tételei
class PriceOfferItem(models.Model):
    CURRENCY_CHOICE = (
        ('HUF', 'Forint'),
        ('EUR', 'Euro'),
        ('USD', 'Dollár'),
    )

    price_offer = models.ForeignKey(PriceOffer, on_delete=models.CASCADE)  # Árajánlat
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  # Termék
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Mennyiség
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Egységár forintban
    comment = models.CharField(max_length=150, null=True, blank=True)  # Megjegyzés

    def __str__(self):
        return self.product.name if self.product else 'N/A'

    @property
    def value(self):  # számított mező: összérték
        return self.amount * self.price
