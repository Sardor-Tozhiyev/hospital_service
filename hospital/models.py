from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='patient',
    )


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField()

    def __str__(self):
        return f"{self.name} (Floor: {self.floor})"


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]


