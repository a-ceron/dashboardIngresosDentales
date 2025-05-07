"""
    This file contains the models for the dental clinic application.
"""

from django.db import models


class Person(models.Model):
    """
        This model is used to store the persons of the clinic.
    """
    id = models.AutoField(primary_key=True)
    fist_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_default = models.CharField(max_length=15)
    phone_alternate = models.CharField(max_length=15)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Dentist(models.Model):
    """
        This model is used to store the dentists of the clinic.
    """
    id = models.AutoField(primary_key=True)
    id_person = models.ForeignKey(Person, on_delete=models.CASCADE)

    percentage = models.DecimalField(
        max_digits=1, decimal_places=2, default=0.30)
    level = models.CharField(max_length=100, default="common")

    def __str__(self):
        return self.first_name + " " + self.last_name


class Patient(models.Model):
    """
        This model is used to store the patients of the clinic.
    """
    id = models.AutoField(primary_key=True)
    id_person = models.ForeignKey(Person, on_delete=models.CASCADE)

    level = models.CharField(max_length=100, default="common")

    def __str__(self):
        return self.first_name + " " + self.last_name


class Procedure(models.Model):
    """
        This model is used to store the procedures of the clinic.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name + " " + str(self.price)


class Incomes(models.Model):
    """
        This model is used to store the incomes of the clinic.
    """
    id = models.AutoField(primary_key=True)
    id_dentist = models.ForeignKey(Dentist, on_delete=models.CASCADE)
    id_patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    date = models.DateField(auto_now=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    is_facturable = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " " + str(self.date) + " " + str(self.amount)
