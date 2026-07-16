from django.db.models.sql import query
from django.shortcuts import render
from django.views import generic

from hospital.forms import DoctorSearchForm
from hospital.models import DoctorProfile, PatientProfile


class HomeView(generic.TemplateView):
    template_name = "hospital/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors_count"] = DoctorProfile.objects.count()
        context["departments_count"] = DoctorProfile.objects.count()
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
    template_name = "hospital/doctor_detail.html"
    context_object_name = "doctor"

