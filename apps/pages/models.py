from django.db import models


class Person(models.Model):
    """
    Base model to store persons in the clinic.
    """
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_default = models.CharField(max_length=15)
    phone_alternate = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Dentist(Person):
    """
    Model to store dentists of the clinic.
    """
    percentage = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.30)
    level = models.CharField(max_length=100, default="common")

    def __str__(self):
        return f"Dentist: {self.first_name} {self.last_name} ({self.level})"


class Patient(Person):
    """
    Model to store patients of the clinic.
    """
    level = models.CharField(max_length=100, default="common")

    def __str__(self):
        return f"Patient: {self.first_name} {self.last_name}"


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
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

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
