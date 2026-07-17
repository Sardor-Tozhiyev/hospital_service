from django.test import TestCase

from hospital.models import (
    CustomUser,
    Department,
    DoctorProfile,
    PatientProfile,
    Specialization,
)


class DoctorProfileModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Cardiology", floor=2)
        self.specialization = Specialization.objects.create(
            name="Cardiologist"
        )
        self.user = CustomUser.objects.create_user(
            username="doc1", password="pass12345", role="doctor"
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.user,
            department=self.department,
            experience_years=5,
            license_number="LIC-001",
        )
        self.doctor.specialization.add(self.specialization)

    def test_doctor_str(self):
        self.assertIn("Dr.", str(self.doctor))

    def test_doctor_has_specialization(self):
        self.assertEqual(self.doctor.specialization.count(), 1)
        self.assertEqual(
            self.doctor.specialization.first().name,
            "Cardiologist"
        )


class PatientProfileModelTests(TestCase):
    def test_patient_str(self):
        user = CustomUser.objects.create_user(
            username="pat1", password="pass12345", role="patient"
        )
        patient = PatientProfile.objects.create(user=user)
        self.assertEqual(str(patient), "pat1")
