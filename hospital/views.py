from typing import cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from hospital.forms import (
    DoctorSearchForm,
    PatientRegistrationForm,
    AppointmentForm,
    AppointmentSearchForm,
    MedicalRecordSearchForm,
    MedicalRecordForm
)
from hospital.mixins import (PatientRequiredMixin,
                             DoctorRequiredMixin)
from hospital.models import (
    DoctorProfile,
    PatientProfile,
    Appointment,
    CustomUser,
    MedicalRecord, Department
)


class HomeView(generic.TemplateView):
    template_name = "hospital/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors_count"] = DoctorProfile.objects.count()
        context["departments_count"] = Department.objects.count()
        context["patients_count"] = PatientProfile.objects.count()
        return context


class DoctorListView(generic.ListView):
    model = DoctorProfile
    template_name = "hospital/doctor_list.html"
    context_object_name = "doctor_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = DoctorProfile.objects.select_related(
            "user", "department"
        ).prefetch_related("specialization")
        specialization = self.request.GET.get("specialization")
        if specialization:
            queryset = queryset.filter(
                specializations__name__icontains=specialization
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = DoctorSearchForm(
            initial={"specialization": self.request.GET.get("specialization", "")}
        )
        return context


class DoctorDetailView(generic.DetailView):
    model = DoctorProfile
    template_name = "hospital/doctor_detail.html"
    context_object_name = "doctor"


class PatientRegisterView(generic.CreateView):
    form_class = PatientRegistrationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created. You can now log in.")
        return response


class AppointmentCreateView(LoginRequiredMixin, PatientRequiredMixin, generic.CreateView):
    model = Appointment
    form_class = AppointmentForm
    success_url = reverse_lazy("hospital:my-appointments")

    def get_initial(self):
        initial = super().get_initial()
        initial["doctor"] = self.kwargs["pk"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = get_object_or_404(DoctorProfile, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        user = cast(CustomUser, self.request.user)
        form.instance.doctor = get_object_or_404(DoctorProfile, pk=self.kwargs["pk"])
        form.instance.patient = user.patient_profile
        response = super().form_valid(form)
        messages.success(self.request, "Appointment booked successfully.")
        return response


class MyAppointmentsListView(LoginRequiredMixin, PatientRequiredMixin, generic.ListView):
    model = Appointment
    context_object_name = "appointments_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            patient=self.request.user.patient_profile
        ).select_related("doctor__user").prefetch_related("symptoms")
        doctor_name = self.request.GET.get("doctor_name")
        if doctor_name:
            queryset = queryset.filter(doctor__user__last_name__icontains=doctor_name)
        return queryset

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = AppointmentSearchForm(
            initial={"doctor_name": self.request.GET.get("doctor_name", "")}
        )
        return context


class AppointmentCancelView(LoginRequiredMixin, PatientRequiredMixin, generic.View):
    def get(self, request, pk):
        appointment = get_object_or_404(
            Appointment,
            pk=pk,
            patient=request.user.patient_profile
        )
        appointment.status = "cancelled"
        appointment.save()
        messages.info(request, "Appointment canceled.")
        return redirect("hospital:my-appointments")


class AppointmentConfirmView(LoginRequiredMixin, DoctorRequiredMixin, generic.View):
    def get(self, request, pk):
        appointment = get_object_or_404(
            Appointment,
            pk=pk,
            doctor=request.user.doctor_profile
        )
        appointment.status = "confirmed"
        appointment.save()
        messages.success(request, "Appointment confirmed.")
        return redirect("hospital:doctor-schedule")


class DoctorScheduleView(LoginRequiredMixin, DoctorRequiredMixin, generic.ListView):
    model = Appointment
    context_object_name = "appointments_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Appointment.objects.filter(
            doctor=self.request.user.doctor_profile
        ).select_related("patient__user")
        patient_name = self.request.GET.get("patient_name")
        if patient_name:
            queryset = queryset.filter(patient__user__last_name__icontains=patient_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = AppointmentSearchForm(
            initial={"patient_name": self.request.GET.get("patient_name", "")}
        )
        return context


class MedicalRecordCreateView(LoginRequiredMixin, DoctorRequiredMixin, generic.CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    success_url = reverse_lazy("hospital:doctor-schedule")

    def form_valid(self, form):
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs["pk"],
            doctor=self.request.user.doctor_profile
        )
        form.instance.appointment = appointment
        form.instance.doctor = appointment.doctor
        form.instance.patient = appointment.patient
        appointment.status = "completed"
        appointment.save()
        response = super().form_valid(form)
        messages.success(self.request, "Medical record created successfully.")
        return response


class MedicalRecordListView(LoginRequiredMixin, PatientRequiredMixin, generic.ListView):
    model = MedicalRecord
    context_object_name = "record_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = MedicalRecord.objects.filter(
            patient=self.request.user.patient_profile
        ).select_related("doctor__user")
        query =self.request.GET.get("query")
        if query:
            queryset = queryset.filter(diagnosis__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context ["search_form"] = MedicalRecordSearchForm(
            initial={"query": self.request.GET.get("query", "")}
        )
        return context

