from typing import cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from hospital.forms import DoctorSearchForm, PatientRegistrationForm, AppointmentForm
from hospital.mixins import PatientRequiredMixin
from hospital.models import DoctorProfile, PatientProfile, Appointment, CustomUser


class HomeView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors_count"] = DoctorProfile.objects.count()
        context["departments_count"] = DoctorProfile.objects.count()
        context["patients_count"] = PatientProfile.objects.count()
        return context


class DoctorListView(generic.ListView):
    model = DoctorProfile
    context_object_name = "doctor_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = DoctorProfile.objects.select_related(
            "user", "department"
        ).prefetch_related("specializations")
        specialization = self.request.GET.get("specialization")
        if specialization:
            queryset = queryset.filter(
                specialization__name__icontains=specialization
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



