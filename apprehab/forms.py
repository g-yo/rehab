from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
import uuid
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['event_name', 'image']

from django import forms
from .models import AddictionDetails, Staff, VideoConference, CustomUser


class AddictionDetailsForm(forms.ModelForm):
    RELATIONSHIP_CHOICES = [
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('spouse', 'Spouse'),
        ('friend', 'Friend'),
        ('other', 'Other')
    ]

    guider_relationship = forms.ChoiceField(
        choices=RELATIONSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    other_relationship_specification = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please specify the relationship'
        })
    )

    class Meta:
        model = AddictionDetails
        fields = ['name', 'age', 'addiction_type', 'description', 'contact_number', 
                 'patient_email', 'guider_name', 'guider_contact_number', 'guider_email',
                 'guider_relationship', 'other_relationship_specification']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'addiction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guider_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guider_contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'guider_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        guider_relationship = cleaned_data.get('guider_relationship')
        other_relationship_specification = cleaned_data.get('other_relationship_specification')
        age = cleaned_data.get('age')

        if guider_relationship == 'other' and not other_relationship_specification:
            raise forms.ValidationError({
                'other_relationship_specification': 'Please specify the relationship when selecting Other'
            })
            
        # Age validation
        if age is not None:
            if age < 14:
                raise forms.ValidationError({
                    'age': 'Our services are only available for individuals aged 14 and above.'
                })
            elif age > 22:
                raise forms.ValidationError({
                    'age': 'Our services are only available for individuals aged 22 and below.'
                })
                
        return cleaned_data

class StaffForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Staff email address for login credentials'
    )
    
    class Meta:
        model = Staff
        fields = ['name', 'email', 'photo', 'position', 'age', 'specialization']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AssignPatientForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['patient_id']

class VideoConferenceForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Select date and time for the conference'
    )
    staff = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=True).exclude(is_superuser=True),
        empty_label="Select Staff Member",
        help_text='Select staff member for the conference'
    )
    patient = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_patient=True),
        empty_label="Select Patient",
        help_text='Select patient for the conference'
    )
    
    class Meta:
        model = VideoConference
        fields = ['title', 'staff', 'patient', 'scheduled_time', 'duration', 'notes']
        widgets = {
            'duration': forms.NumberInput(attrs={'min': '15', 'max': '120', 'step': '15'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        if scheduled_time and scheduled_time < timezone.now():
            raise forms.ValidationError("Conference cannot be scheduled in the past")
        return scheduled_time

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.meeting_id = str(uuid.uuid4())
        if commit:
            instance.save()
        return instance

class YogaForm(forms.ModelForm):
    class Meta:
        model = Yoga
        fields = ['name', 'description', 'duration', 'animation_url', 'image']
        widgets = {
            'duration': forms.NumberInput(attrs={'min': '300', 'max': '1800', 'step': '300'}),
        }

class YogaSessionForm(forms.ModelForm):
    class Meta:
        model = YogaSession
        fields = ['patient', 'staff', 'scheduled_time', 'duration']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5})
    )
