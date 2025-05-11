"""
    models.py
    
    Modelos para la gestiòn de dentistas e ingresos de la clinica.
    
    * Se define una clase personaizada de UserManager para la creación
    de usuarios y superusuarios, aprovechado el sistema de autenticación
    de Django.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model to handle authentication for the clinic.
    """
    username = None  # Removing username as a required field
    # Using email as the unique identifier
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_default = models.CharField(max_length=15)
    phone_alternate = models.CharField(max_length=15, blank=True, null=True)

    # Additional permissions for role-based access
    is_dentist = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class Dentist(models.Model):
    """
    Model to store dentists' details.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="dentist_profile")
    percentage = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.30)
    level = models.CharField(
        max_length=10,
        choices=[
            ('Supervisor', 'Supervisor'),
            ('Dentista A', 'Dentista A'),
            ('Dentista B', 'Dentista B')
        ],
        default='Dentista B'
    )
    birth_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Dentist: {self.user.first_name} {self.user.last_name} ({self.level})"


class Procedure(models.Model):
    """
    Model to store procedures of the clinic.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Income(models.Model):
    """
    Model to store incomes of the clinic.
    """
    id = models.AutoField(primary_key=True)
    dentist = models.ForeignKey(Dentist, on_delete=models.CASCADE)

    date = models.DateField(auto_now=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    was_paid = models.CharField(
        max_length=10,
        choices=[
            ('debit', 'Tarjeta de Débito'),
            ('credit', 'Tarjeta de Crédito'),
            ('cash', 'Efectivo'),
            ('transfer', 'Transferencia'),
            ('check', 'Cheque')
        ],
        default='cash'
    )
    is_facturable = models.BooleanField(default=False)

    def __str__(self):
        return f"Income {self.id} - {self.date} - ${self.amount}"
