from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_patient = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    addiction_detail = models.TextField(null=True, blank=True)
    parent_phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions')
    contact_number = models.CharField(max_length=15, null=True, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username

class GalleryImage(models.Model):
    event_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name

class Staff(models.Model):
    POSITION_CHOICES = [
        ('Counselor', 'Counselor'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Medical Officer', 'Medical Officer'),
        ('Support Staff', 'Support Staff'),
        ('Case Manager', 'Case Manager'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    position = models.CharField(max_length=100, choices=POSITION_CHOICES, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    patient_id = models.ManyToManyField('Patient', related_name='assigned_staff', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    dob = models.DateField()
    addiction_detail = models.TextField()
    parent_name = models.CharField(max_length=100)
    parent_phone_number = models.CharField(max_length=15)
    patient_phone_number = models.CharField(max_length=15)
    date_of_join = models.DateField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='patients')

    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=100)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='activities')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='activities')
    time = models.TimeField()

    def __str__(self):
        return self.name

class AddictionDetails(models.Model):
    ADDICTION_CHOICES = [
        ('alcohol', 'Alcohol'),
        ('drugs', 'Drugs'),
        ('gambling', 'Gambling'),
        ('other', 'Other')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addiction_details', null=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    addiction_type = models.CharField(max_length=10, choices=ADDICTION_CHOICES)
    description = models.TextField()
    contact_number = models.CharField(max_length=15)
    patient_email = models.EmailField()
    guider_name = models.CharField(max_length=100, blank=True)
    guider_contact_number = models.CharField(max_length=15, blank=True)
    guider_relationship = models.CharField(max_length=50, blank=True)
    guider_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    assigned_staff = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications')
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}'s Application - {self.addiction_type}"

    @property
    def approved(self):
        return self.status == 'approved'

    @property
    def rejected(self):
        return self.status == 'rejected'

class VideoConference(models.Model):
    title = models.CharField(max_length=200, null=True)
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staff_conferences', null=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_conferences', null=True)
    scheduled_time = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True, help_text='Duration in minutes')
    notes = models.TextField(blank=True, null=True)
    room_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)
    program_day = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], help_text='Day of the 7-day program (1-7)')
    patient_join_request = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('none', 'No Request')
        ],
        default='none'
    )
    join_request_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"rehab-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    @property
    def meeting_link(self):
        return f"https://meet.jit.si/{self.room_name}"

    def request_to_join(self):
        self.patient_join_request = 'pending'
        self.join_request_time = timezone.now()
        self.save()

    def accept_patient(self):
        self.patient_join_request = 'accepted'
        self.save()

    def reject_patient(self):
        self.patient_join_request = 'rejected'
        self.save()

    def __str__(self):
        return f"{self.title} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"

class Yoga(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(default=300)  # Duration in seconds (5 minutes)
    animation_url = models.URLField(blank=True, null=True)  # URL for the yoga animation/video
    image = models.ImageField(upload_to='yoga_images/', blank=True, null=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_yogas', null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='assigned_yogas', null=True)
    program_day = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], help_text='Day of the 7-day program (1-7)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        if self.patient:
            return f"{self.name} - {self.patient.get_full_name()}"
        return self.name

class YogaSession(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='yoga_sessions')
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_yoga_sessions')
    scheduled_time = models.DateTimeField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=60)  # Duration in minutes
    program_day = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], help_text='Day of the 7-day program (1-7)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Yoga Session for {self.patient.get_full_name()} on {self.scheduled_time}"

    class Meta:
        ordering = ['-scheduled_time']

class GroupConference(models.Model):
    title = models.CharField(max_length=200, default="Daily Group Meeting")
    scheduled_time = models.TimeField(default='17:00')  # Default to 5 PM
    duration = models.IntegerField(default=60, help_text='Duration in minutes')
    room_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"rehab-group-{timezone.now().strftime('%Y%m%d')}"
        super().save(*args, **kwargs)

    @property
    def meeting_link(self):
        return f"https://meet.jit.si/{self.room_name}"

    def __str__(self):
        return f"{self.title} at {self.scheduled_time}"

class Chat(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_chats')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_chats')
    message = models.TextField()
    sent_by_patient = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"Chat between {self.patient.get_full_name()} and {self.staff.name}"

class Testimonial(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='testimonials')
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Testimonial by {self.patient.get_full_name()}"
