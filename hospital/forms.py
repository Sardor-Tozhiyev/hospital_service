from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from django.contrib.auth.forms import UserCreationForm

from hospital.models import Specialization, Department, CustomUser, DoctorProfile, PatientProfile


class DoctorCreationForm(UserCreationForm):
    specialization = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
    )
    experience_year = forms.IntegerField(min_value=0, required=True)
    license_number = forms.CharField(max_length=50, required=True)

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "",
                "username",
                "last_name",
                "email",
                "department",
                "experience_year",
                "license_number",
                "specialization",
                "password1",
                "password2",
            )
        )
        self.helper.add_input(
            Submit("submit", "Create Doctor", css_class="btn-primary w-100")
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "doctor"
        if commit:
            user.save()
            doctor_profile = DoctorProfile.objects.create(
                user=user,
                department=self.cleaned_data["department"],
                experience_year=self.cleaned_data["experience_year"],
                license_number=self.cleaned_data["license_number"],
            )
            doctor_profile.specialization.set(self.cleaned_data["specialization"])
        return user


class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(
            Submit("submit", "Sign Up", css_class="btn-primary w-100")
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "patient"
        if commit:
            user.save()
            PatientProfile.objects.create(user=user)
        return user
