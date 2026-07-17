from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


if TYPE_CHECKING:
    from django.http import HttpRequest


class PatientRequiredMixin(UserPassesTestMixin):
    request: "HttpRequest"

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role == "patient"
            and hasattr(self.request.user, "patient_profile")
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            "This page is available only for patients."
        )
        return redirect("hospital:home")


class DoctorRequiredMixin(UserPassesTestMixin):
    request: "HttpRequest"

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role == "doctor"
            and hasattr(self.request.user, "doctor_profile")
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            "This page is available only for doctors."
        )
        return redirect("hospital:home")
