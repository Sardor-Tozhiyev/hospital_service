from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("patient", "Patient"),
        ("doctor", "Doctor"),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="patient",
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

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    specialization = models.ManyToManyField(
        Specialization,
        related_name="doctors",
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="doctors",
    )
    experience_years = models.PositiveIntegerField(default=0)
    license_number =  models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Dr.{self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse("hospital:doctor_detail", kwargs={"pk": self.pk})


class PatientProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


