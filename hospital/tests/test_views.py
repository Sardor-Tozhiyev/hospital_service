from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from hospital.models import CustomUser, Department, DoctorProfile
from hospital_service import settings


class DoctorListViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Neurology", floor=3)
        self.user = CustomUser.objects.create_user(
            username="doc2", password="pass12345", role="doctor"
        )
        DoctorProfile.objects.create(
            user=self.user,
            department=self.department,
            experience_years=3,
            license_number="LIC-002",
        )

    def test_doctor_list_status_code(self):
        response = self.client.get(reverse("hospital:doctor-list"))
        self.assertEqual(response.status_code, 200)

    def test_doctor_list_contains_doctor(self):
        response = self.client.get(reverse("hospital:doctor-list"))
        self.assertContains(response, "doc2")


class MyAppointmentsAccessTests(TestCase):
    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("hospital:my-appointments"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), settings.LOGIN_URL)

    def test_doctor_role_redirected_from_patient_only_page(self):
        user = CustomUser.objects.create_user(
            username="doc3", password="pass12345", role="doctor"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("hospital:my-appointments"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("hospital:home"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("available only for patients"
                            in str(m) for m in messages))
