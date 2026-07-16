from typing import TYPE_CHECKING

from django.contrib.auth.mixins import UserPassesTestMixin

if TYPE_CHECKING:
    from django.http import HttpRequest


class PatientRequiredMixin(UserPassesTestMixin):
    request: "HttpRequest"

    """Allow access only to authenticated users with role == 'patient'."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == "patient"


class DoctorRequiredMixin(UserPassesTestMixin):
    request: "HttpRequest"

    """Allow access only to authenticated users with role == 'doctor'."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == "doctor"