import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from hospital.models import (
    CustomUser,
    Specialization,
    Department,
    Symptom,
    DoctorProfile,
    PatientProfile,
    Appointment,
    MedicalRecord,
)

DEFAULT_PASSWORD = "Test12345!"

SPECIALIZATIONS = [
    "Cardiology",
    "Neurology",
    "Pediatrics",
    "Dermatology",
    "Orthopedics",
    "Oncology",
    "Ophthalmology",
    "Gastroenterology",
    "Psychiatry",
    "Otolaryngology",
]

DEPARTMENTS = [
    ("Cardiology Department", 1),
    ("Neurology Department", 2),
    ("Pediatrics Department", 3),
    ("Dermatology Department", 1),
    ("Orthopedics Department", 4),
    ("Oncology Department", 5),
    ("Ophthalmology Department", 2),
    ("Gastroenterology Department", 3),
    ("Psychiatry Department", 6),
    ("ENT Department", 2),
]

SYMPTOMS = [
    "Fever",
    "Headache",
    "Cough",
    "Fatigue",
    "Nausea",
    "Chest pain",
    "Shortness of breath",
    "Joint pain",
    "Skin rash",
    "Dizziness",
]

DOCTORS = [
    ("James", "Anderson", 12),
    ("Olivia", "Martinez", 8),
    ("William", "Thompson", 15),
    ("Sophia", "Clark", 5),
    ("Benjamin", "Rodriguez", 20),
    ("Emma", "Lewis", 9),
    ("Lucas", "Walker", 11),
    ("Mia", "Hall", 6),
    ("Henry", "Young", 17),
    ("Charlotte", "King", 3),
]

PATIENT_FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas",
    "Henry", "Alexander", "Emma", "Ava", "Sophia", "Isabella", "Mia", "Amelia",
    "Charlotte", "Evelyn", "Harper", "Ella", "Daniel", "Matthew", "Jack",
    "Sebastian", "Owen", "Grace", "Chloe", "Victoria", "Aria", "Scarlett",
]

PATIENT_LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Robinson",
    "Lewis", "Walker", "Hall", "Young", "Allen", "King", "Wright", "Scott",
    "Green", "Baker", "Adams", "Nelson", "Carter", "Mitchell", "Perez",
]

CITIES = [
    "12 Maple St, Springfield", "45 Oak Ave, Riverside", "8 Elm Rd, Fairview",
    "23 Pine St, Greenville", "67 Cedar Ln, Lakeside", "5 Birch Dr, Hillcrest",
    "34 Willow Way, Brookfield", "19 Aspen Ct, Clearwater",
]

REASONS = [
    "Annual check-up", "Follow-up consultation", "Persistent symptoms",
    "Routine screening", "Second opinion", "Post-treatment review",
]


class Command(BaseCommand):
    help = "Populates the database with demo data (departments, specializations, symptoms, doctors, patients, appointments, medical records)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing demo data (all non-superuser users and related records) before seeding.",
        )
        parser.add_argument(
            "--flush-only",
            action="store_true",
            help="Delete existing demo data and exit, without creating new demo data.",
        )

    def handle(self, *args, **options):
        if options["flush"] or options["flush_only"]:
            self._flush()

        if options["flush_only"]:
            self.stdout.write(self.style.SUCCESS("Demo data removed."))
            return

        specializations = self._create_specializations()
        departments = self._create_departments()
        symptoms = self._create_symptoms()
        doctors = self._create_doctors(specializations, departments)
        patients = self._create_patients()
        appointments = self._create_appointments(doctors, patients, symptoms)
        self._create_medical_records(appointments)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {len(specializations)} specializations, "
            f"{len(departments)} departments, {len(symptoms)} symptoms, "
            f"{len(doctors)} doctors, {len(patients)} patients, "
            f"{len(appointments)} appointments seeded."
        ))
        self.stdout.write(
            f"All accounts use the password: {DEFAULT_PASSWORD}"
        )

    def _flush(self):
        self.stdout.write("Removing existing demo data...")
        deleted_users = CustomUser.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        Specialization.objects.all().delete()
        Symptom.objects.all().delete()
        self.stdout.write(f"Removed {deleted_users[0]} related objects "
                           f"(users, profiles, appointments, medical records) "
                           f"plus all departments, specializations and symptoms.")

    def _create_specializations(self):
        objs = []
        for name in SPECIALIZATIONS:
            obj, _ = Specialization.objects.get_or_create(name=name)
            objs.append(obj)
        return objs

    def _create_departments(self):
        objs = []
        for name, floor in DEPARTMENTS:
            obj, _ = Department.objects.get_or_create(name=name, defaults={"floor": floor})
            objs.append(obj)
        return objs

    def _create_symptoms(self):
        objs = []
        for name in SYMPTOMS:
            obj, _ = Symptom.objects.get_or_create(name=name)
            objs.append(obj)
        return objs

    def _create_doctors(self, specializations, departments):
        doctors = []
        for i, (first, last, exp) in enumerate(DOCTORS, start=1):
            username = f"dr.{first.lower()}.{last.lower()}"
            if CustomUser.objects.filter(username=username).exists():
                user = CustomUser.objects.get(username=username)
            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f"{username}@hospital.example",
                    password=DEFAULT_PASSWORD,
                    first_name=first,
                    last_name=last,
                    role="doctor",
                )
            profile, created = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "department": departments[i % len(departments)],
                    "experience_years": exp,
                    "license_number": f"LIC-{1000 + i}",
                },
            )
            if created:
                profile.specialization.set(
                    random.sample(specializations, k=random.choice([1, 2]))
                )
            doctors.append(profile)
        return doctors

    def _create_patients(self):
        patients = []
        used_names = set()
        for i in range(1, 31):
            first = random.choice(PATIENT_FIRST_NAMES)
            last = random.choice(PATIENT_LAST_NAMES)
            key = (first, last)
            while key in used_names:
                first = random.choice(PATIENT_FIRST_NAMES)
                last = random.choice(PATIENT_LAST_NAMES)
                key = (first, last)
            used_names.add(key)

            username = f"{first.lower()}.{last.lower()}{i}"
            if CustomUser.objects.filter(username=username).exists():
                user = CustomUser.objects.get(username=username)
            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password=DEFAULT_PASSWORD,
                    first_name=first,
                    last_name=last,
                    role="patient",
                )
            birth_year = random.randint(1955, 2005)
            profile, _ = PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "date_of_birth": date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                    "phone_number": f"+1-555-{random.randint(1000, 9999)}",
                    "address": random.choice(CITIES),
                },
            )
            patients.append(profile)
        return patients

    def _create_appointments(self, doctors, patients, symptoms):
        statuses = ["pending", "confirmed", "completed", "cancelled"]
        appointments = []
        now = timezone.now()
        for i in range(40):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            status = random.choices(
                statuses, weights=[2, 2, 4, 1], k=1
            )[0]
            offset_days = random.randint(-20, 20)
            appt_time = now + timedelta(days=offset_days, hours=random.randint(8, 17))
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date_time=appt_time,
                status=status,
                reason=random.choice(REASONS),
            )
            appointment.symptoms.set(random.sample(symptoms, k=random.randint(1, 3)))
            appointments.append(appointment)
        return appointments

    def _create_medical_records(self, appointments):
        diagnoses = [
            "Seasonal viral infection, prescribed rest and fluids.",
            "Mild hypertension, recommended lifestyle changes and follow-up in 3 months.",
            "Tension headache, no acute findings.",
            "Minor joint inflammation, prescribed anti-inflammatory course.",
            "Routine check-up, no abnormalities detected.",
            "Allergic reaction, prescribed antihistamines.",
            "Gastritis symptoms, dietary recommendations given.",
            "Upper respiratory tract infection, prescribed antibiotics.",
        ]
        prescriptions = [
            "Paracetamol 500mg, twice daily for 5 days.",
            "Ibuprofen 200mg, as needed for pain.",
            "Loratadine 10mg, once daily for 7 days.",
            "Omeprazole 20mg, once daily before breakfast.",
            "Amoxicillin 500mg, three times daily for 7 days.",
            "No medication required, follow-up in 2 weeks.",
        ]
        count = 0
        for appointment in appointments:
            if appointment.status == "completed":
                MedicalRecord.objects.get_or_create(
                    appointment=appointment,
                    defaults={
                        "patient": appointment.patient,
                        "doctor": appointment.doctor,
                        "diagnosis": random.choice(diagnoses),
                        "prescription": random.choice(prescriptions),
                    },
                )
                count += 1
        return count