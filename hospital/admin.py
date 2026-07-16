from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hospital.models import (
    CustomUser,
    DoctorProfile,
    PatientProfile,
    Appointment,
    Specialization,
    Department,
    Symptom,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("role", )
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "department",
        "experience_years",
        "license_number"
    )
    filter_horizontal = ("specialization", )
    search_fields = (
        "user__username",
        "user__last_name",
        "license_number"
    )

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date_of_birth",
        "phone_number"
    )
    search_fields = (
        "user__username",
        "user__last_name",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "date_time",
        "status"
    )
    list_filter = ("status", "doctor")
    filter_horizontal = ("symptoms", )


admin.site.register(Specialization)
admin.site.register(Department)
admin.site.register(Symptom)
