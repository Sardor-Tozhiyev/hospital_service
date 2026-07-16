from django.urls import path

from hospital import views

app_name = "hospital"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.PatientRegisterView.as_view(), name="register"),
    path("doctors/", views.DoctorListView.as_view(), name="doctor-list"),
    path("doctor/<int:pk>/", views.DoctorDetailView.as_view(), name="doctor-detail"),
    path("doctor/<int:pk>/book/", views.AppointmentCreateView.as_view(), name="appointment-create"),
    path("appointments/my/", views.MyAppointmentsListView.as_view(), name="my-appointments"),
    path("appointment/<int:pk>/cancel/", views.AppointmentCancelView.as_view(), name="appointment-cancel"),
    path("appointments/<int:pk>/confirm/", views.AppointmentConfirmView.as_view(), name="appointment-confirm"),
    path("appointments/<int:pk>/record/", views.MedicalRecordCreateView.as_view(), name="record-create"),
    path("schedule/", views.DoctorScheduleView.as_view(), name="doctor-schedule"),
    path("records/my/", views.MedicalRecordListView.as_view(), name="my-records"),
]