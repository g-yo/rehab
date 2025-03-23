from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
import random
import string
from django.db import models
import uuid
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.urls import reverse
from .email_utils import (
    send_registration_email, send_application_submitted_email,
    send_application_status_update_email, send_staff_account_email
)

from .models import (
    GalleryImage, CustomUser, AddictionDetails, Staff, 
    VideoConference, YogaSession, Yoga, GroupConference, Chat, Testimonial
)
from .forms import (
    AssignPatientForm, GalleryImageForm, AddictionDetailsForm, 
    StaffForm, VideoConferenceForm, YogaForm, YogaSessionForm
)

def home(request):
    # Get approved testimonials for the home page
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')
    
    # If the user is logged in and has a testimonial, prioritize it
    user_testimonial = None
    if request.user.is_authenticated:
        user_testimonial = Testimonial.objects.filter(patient=request.user, is_approved=True).first()
    
    # If user has a testimonial, make sure it's first in the list
    if user_testimonial:
        # Create a list with user's testimonial first, followed by others (excluding the user's)
        testimonial_list = [user_testimonial]
        for testimonial in testimonials:
            if testimonial.id != user_testimonial.id:
                testimonial_list.append(testimonial)
        # Limit to 3 testimonials
        testimonial_list = testimonial_list[:3]
    else:
        # Just use the first 3 testimonials
        testimonial_list = testimonials[:3]
    
    return render(request, 'home.html', {
        'testimonials': testimonial_list
    })

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                messages.error(request, 'You are not authorized to access the admin area.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'admin_login.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def front_end(request):
    return render(request, 'front_end.html')

@login_required
def back_end(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    applications = AddictionDetails.objects.filter(status='pending')
    return render(request, 'admin/back_end.html', {
        'applications': applications
    })

@login_required
def patient_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    # Get all approved applications
    approved_applications = AddictionDetails.objects.filter(
        status='approved'
    ).select_related('assigned_staff').order_by('-created_at')
    
    return render(request, 'patient_list.html', {
        'approved_applications': approved_applications
    })

@login_required
def user_dashboard(request):
    user = request.user
    applications = AddictionDetails.objects.filter(patient=user).order_by('-created_at')
    latest_application = applications.first()
    
    context = {
        'user': user,
        'applications': applications,
        'latest_application': latest_application,
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def user_profile(request):
    user = request.user
    applications = AddictionDetails.objects.filter(patient=user).order_by('-created_at')
    latest_application = applications.first()
    
    context = {
        'user': user,
        'applications': applications,
        'latest_application': latest_application,
    }
    return render(request, 'user_profile.html', context)

@login_required
def patient_progress(request):
    try:
        # Get the latest approved addiction details for the user
        addiction = AddictionDetails.objects.filter(
            patient_email=request.user.email,
            status='approved'
        ).order_by('-created_at').first()
        
        if not addiction:
            # Check if there are any applications at all
            any_application = AddictionDetails.objects.filter(
                patient_email=request.user.email
            ).exists()
            
            if any_application:
                messages.error(request, 'Access denied. Your application has not been approved yet.')
            else:
                messages.error(request, 'No application found.')
            
            return redirect('user_dashboard')
            
        # Calculate program progress
        today = timezone.now().date()
        start_date = addiction.start_date or today
        days_passed = max(0, (today - start_date).days + 1)  # +1 to count the current day
        current_day = min(days_passed, 7)  # Cap at 7 days
        days_remaining = max(0, 7 - days_passed)
        program_completion = min(round((days_passed / 7) * 100), 100)  # Cap at 100%
        
        # Generate day progress data
        day_progress = []
        for i in range(1, 8):
            day_date = start_date + timedelta(days=i-1)
            day_progress.append({
                'number': i,
                'date': day_date,
                'active': i == current_day,
                'completed': i < current_day
            })
        
        # Mock data for activity completion (in a real app, this would come from the database)
        counseling_total = 7
        counseling_completed = min(days_passed, counseling_total)
        counseling_completion = round((counseling_completed / counseling_total) * 100)
        
        yoga_total = 7
        yoga_completed = min(days_passed, yoga_total)
        yoga_completion = round((yoga_completed / yoga_total) * 100)
        
        group_total = 3
        group_completed = min(days_passed // 2, group_total)  # Every other day
        group_completion = round((group_completed / group_total) * 100)
        
        personal_total = 14
        personal_completed = min(days_passed * 2, personal_total)  # 2 per day
        personal_completion = round((personal_completed / personal_total) * 100)
        
        # Mock data for staff notes (in a real app, this would come from the database)
        staff_notes = []
        if days_passed >= 1:
            staff_notes.append({
                'title': 'Initial Assessment',
                'content': 'Patient has shown willingness to participate in the program. Initial assessment indicates moderate addiction severity.',
                'staff_name': addiction.assigned_staff.name,
                'date': start_date
            })
        
        if days_passed >= 3:
            staff_notes.append({
                'title': 'Progress Update',
                'content': 'Patient is actively participating in all scheduled activities. Showing positive signs of engagement with the program.',
                'staff_name': addiction.assigned_staff.name,
                'date': start_date + timedelta(days=2)
            })
        
        if days_passed >= 5:
            staff_notes.append({
                'title': 'Mid-Program Review',
                'content': 'Patient has made significant progress. Reduction in withdrawal symptoms observed. Continue with the current treatment plan.',
                'staff_name': addiction.assigned_staff.name,
                'date': start_date + timedelta(days=4)
            })
            
        context = {
            'addiction': addiction,
            'current_day': current_day,
            'days_remaining': days_remaining,
            'program_completion': program_completion,
            'day_progress': day_progress,
            'counseling_completed': counseling_completed,
            'counseling_total': counseling_total,
            'counseling_completion': counseling_completion,
            'yoga_completed': yoga_completed,
            'yoga_total': yoga_total,
            'yoga_completion': yoga_completion,
            'group_completed': group_completed,
            'group_total': group_total,
            'group_completion': group_completion,
            'personal_completed': personal_completed,
            'personal_total': personal_total,
            'personal_completion': personal_completion,
            'staff_notes': staff_notes
        }
        
        return render(request, 'patient_progress.html', context)
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('user_dashboard')

@login_required
def admin_user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_user_list.html', {'users': users})

@login_required
def gallery(request):
    images = GalleryImage.objects.all()
    return render(request, 'gallery.html', {'images': images})

@login_required
def add_image(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = GalleryImageForm()
    return render(request, 'add_image.html', {'form': form})

@login_required
def edit_image(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = GalleryImageForm(instance=image)
    return render(request, 'edit_image.html', {'form': form})

@login_required
def delete_image(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        return redirect('gallery')
    return render(request, 'delete_image.html', {'image': image})

def user_gallery(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('user_gallery')
    else:
        form = GalleryImageForm()
    
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'gallery_user.html', {'form': form, 'images': images})

def user_logout(request):
    logout(request)
    return redirect('home')

@csrf_exempt
def update_field_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_name = data.get('name')
        # Here you can implement your logic to update the name in the database
        # For example:
        # field_instance = FieldModel.objects.get(id=1)
        # field_instance.name = new_name
        # field_instance.save()

        return JsonResponse({'status': 'success', 'new_name': new_name})

    return JsonResponse({'status': 'error'}, status=400)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def apply_treatment(request):
    if request.method == 'POST':
        form = AddictionDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_page')
    else:
        form = AddictionDetailsForm()
    return render(request, 'apply_treatment.html', {'form': form})

def generate_username(name):
    # Convert name to lowercase and remove spaces
    base = ''.join(name.lower().split())
    # Add random number if needed
    username = base
    if Staff.objects.filter(username=username).exists():
        username = f"{base}{random.randint(1, 999)}"
    return username

def generate_password():
    # Generate a random 8-character password
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save(commit=False)
            # Get email from form
            email = form.cleaned_data.get('email')
            staff.email = email
            
            # Generate username and password
            staff.username = generate_username(staff.name)
            password = generate_password()
            staff.password = password
            staff.save()
            
            # Send email with credentials
            try:
                from .email_utils import send_staff_account_email
                send_staff_account_email(staff, password)
                messages.success(request, f'Staff member added successfully. Login credentials have been sent to {email}.')
            except Exception as e:
                print(f"Error sending staff credentials email: {e}")
                messages.success(request, 'Staff member added successfully, but there was an error sending the email with credentials.')
            
            # Return to message redirect page
            return render(request, 'message_redirect.html', {'redirect_url': reverse('staff_list')})
    else:
        form = StaffForm()
    
    return render(request, 'add_staff.html', {'form': form})

def delete_staff(request, staff_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, f'Staff member {staff.name} has been deleted.')
    return redirect('staff_list')

def staff_list(request):
    # First, update any staff without credentials
    staff_without_credentials = Staff.objects.filter(
        models.Q(username__isnull=True) | 
        models.Q(password__isnull=True) |
        models.Q(username='') |
        models.Q(password='')
    )
    
    for staff in staff_without_credentials:
        staff.username = generate_username(staff.name)
        staff.password = generate_password()
        staff.save()
    
    staffs = Staff.objects.all().order_by('name')
    return render(request, 'staff_list.html', {'staffs': staffs})

@login_required
def assign_staff(request, application_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return render(request, 'message_redirect.html', {'redirect_url': reverse('home')})
    
    application = get_object_or_404(AddictionDetails, id=application_id)
    staff_members = Staff.objects.all()
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
                application.assigned_staff = staff
                application.save()
                messages.success(request, f'Successfully assigned {staff.name} to this application.')
                return render(request, 'message_redirect.html', {'redirect_url': reverse('addiction_list')})
            except Staff.DoesNotExist:
                messages.error(request, 'Selected staff member not found.')
        else:
            application.assigned_staff = None
            application.save()
            messages.success(request, 'Staff assignment removed.')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('addiction_list')})
    
    context = {
        'application': application,
        'staff_members': staff_members
    }
    return render(request, 'admin/assign_staff.html', context)

@login_required
def assign_patient(request, staff_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return render(request, 'message_redirect.html', {'redirect_url': reverse('home')})
    
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        form = AssignPatientForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patients successfully assigned to {staff.name}.')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('staff_list')})
    else:
        form = AssignPatientForm(instance=staff)

    return render(request, 'assign_patient.html', {'form': form, 'staff': staff})

@login_required
def addiction_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
        
    addiction_cases = AddictionDetails.objects.all().order_by('-created_at')
    staff_members = CustomUser.objects.filter(is_staff=True)
    
    # Find approved applications without a start date
    needs_start_date = addiction_cases.filter(status='approved', start_date__isnull=True)
    
    context = {
        'applications': addiction_cases,
        'staff_members': staff_members,
        'needs_start_date': needs_start_date
    }
    
    return render(request, 'admin/applications.html', context)

@login_required
def review_application(request, application_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    application = get_object_or_404(AddictionDetails, id=application_id)
    action = request.POST.get('action')
    message = ""
    
    if action == 'approve':
        start_date = request.POST.get('start_date')
        if start_date:
            # Get the user associated with the application
            user = CustomUser.objects.get(email=application.patient_email)
            # Make them a patient
            user.is_patient = True
            user.save()
            # Update application status and start date
            application.status = 'approved'
            application.start_date = start_date
            application.save()
            
            # Send approval email
            try:
                send_application_status_update_email(application)
            except Exception as e:
                print(f"Error sending application approval email: {e}")
                
            message = 'Application approved successfully. An email notification has been sent to the applicant.'
        else:
            # Just approve without setting start date
            user = CustomUser.objects.get(email=application.patient_email)
            user.is_patient = True
            user.save()
            application.status = 'approved'
            application.save()
            
            # Send approval email
            try:
                send_application_status_update_email(application)
            except Exception as e:
                print(f"Error sending application approval email: {e}")
                
            message = 'Application approved successfully. Please set a start date for the program. An email notification has been sent to the applicant.'
    elif action == 'reject':
        application.status = 'rejected'
        application.save()
        
        # Send rejection email
        try:
            send_application_status_update_email(application)
        except Exception as e:
            print(f"Error sending application rejection email: {e}")
            
        message = 'Application rejected successfully. An email notification has been sent to the applicant.'
    
    # Return to the applications list with a JavaScript alert
    return render(request, 'admin/applications.html', {
        'applications': AddictionDetails.objects.all().order_by('-created_at'),
        'alert_message': message
    })

@login_required
def set_program_start_date(request, application_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    application = get_object_or_404(AddictionDetails, id=application_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        if start_date:
            application.start_date = start_date
            application.save()
            message = 'Program start date set successfully.'
            return render(request, 'admin/applications.html', {
                'applications': AddictionDetails.objects.all().order_by('-created_at'),
                'alert_message': message
            })
    
    context = {
        'application': application
    }
    return render(request, 'admin/set_start_date.html', context)

@login_required
def schedule_conference(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        patient_id = request.POST.get('patient')
        staff_id = request.POST.get('staff')
        scheduled_time = request.POST.get('scheduled_time')
        duration = request.POST.get('duration')
        description = request.POST.get('description')
        program_day = request.POST.get('program_day', 1)

        try:
            # Create conference
            conference = VideoConference.objects.create(
                title=title,
                patient_id=patient_id,
                staff_id=staff_id,
                scheduled_time=scheduled_time,
                duration=duration,
                notes=description,
                program_day=program_day
            )
            messages.success(request, 'Conference scheduled successfully.')
            return redirect('conference_list')
        except Exception as e:
            messages.error(request, f'Error scheduling conference: {str(e)}')
            return redirect('schedule_conference')

    # Get all approved applications for patient selection
    approved_applications = AddictionDetails.objects.filter(
        status='approved'
    ).select_related('patient', 'assigned_staff').order_by('-created_at')

    return render(request, 'schedule_conference.html', {
        'approved_applications': approved_applications
    })

@login_required
def conference_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    conferences = VideoConference.objects.all().select_related(
        'patient', 'staff'
    ).order_by('-scheduled_time')
    
    return render(request, 'conference_list.html', {
        'conferences': conferences,
        'now': timezone.now()
    })

@login_required
def patient_conferences(request, patient_id):
    patient = get_object_or_404(CustomUser, id=patient_id)
    conferences = VideoConference.objects.filter(patient=patient, is_active=True).order_by('scheduled_time')
    return render(request, 'patient/conferences.html', {'conferences': conferences})

@login_required
def join_conference(request, conference_id):
    conference = get_object_or_404(VideoConference, id=conference_id)
    return render(request, 'conference_room.html', {'conference': conference})

@login_required
def patient_join_conference(request, conference_id):
    if not request.user.is_patient:
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')
    
    conference = get_object_or_404(VideoConference, id=conference_id)
    
    # Check if this patient is assigned to this conference
    if conference.patient != request.user:
        messages.error(request, 'Access denied. This conference is not assigned to you.')
        return redirect('patient_activities')
    
    # Check if conference is active
    if not conference.is_active:
        messages.error(request, 'This conference is no longer available.')
        return redirect('patient_activities')
    
    # During development, allow direct access to conference room
    return render(request, 'patient_conference_room.html', {'conference': conference})

@login_required
def conference_room(request, conference_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    conference = get_object_or_404(VideoConference, id=conference_id)
    
    # Get pending join requests
    pending_requests = VideoConference.objects.filter(
        patient_join_request='pending',
        scheduled_time__gte=timezone.now(),
        is_active=True
    ).order_by('join_request_time')
    
    # For admin users, automatically accept their own join request
    if request.user.is_superuser:
        conference.patient_join_request = 'accepted'
        conference.save()
    
    return render(request, 'conference_room.html', {
        'conference': conference,
        'pending_requests': pending_requests
    })

@login_required
def accept_patient_join(request, conference_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    conference = get_object_or_404(VideoConference, id=conference_id)
    conference.accept_patient()
    messages.success(request, f'Join request accepted for {conference.patient.get_full_name()}')
    return redirect('conference_room', conference_id=conference_id)

@login_required
def reject_patient_join(request, conference_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    conference = get_object_or_404(VideoConference, id=conference_id)
    conference.reject_patient()
    messages.success(request, f'Join request rejected for {conference.patient.get_full_name()}')
    return redirect('conference_room', conference_id=conference_id)

@login_required
def patient_activities(request):
    user = request.user
    if not user.is_patient:
        messages.error(request, 'Access denied. Patient only.')
        return redirect('home')
    
    # Get the selected day (default to day 1)
    selected_day = int(request.GET.get('day', 1))
    if selected_day < 1 or selected_day > 7:
        selected_day = 1
    
    # Get the patient's application to find the start date
    application = AddictionDetails.objects.filter(patient=user, status='approved').first()
    
    # Get all yoga sessions for this patient for the selected day
    yoga_sessions = YogaSession.objects.filter(
        patient=user,
        program_day=selected_day,
        is_active=True
    ).select_related('staff')
    
    # Get all video conferences for this patient for the selected day
    conferences = VideoConference.objects.filter(
        patient=user,
        program_day=selected_day,
        is_active=True
    ).select_related('staff')
    
    # Get the group conference (available for all days)
    group_conference = GroupConference.objects.filter(is_active=True).first()
    
    # Combine all activities into a single list with activity type
    all_activities = []
    
    # Add yoga sessions
    for session in yoga_sessions:
        all_activities.append({
            'type': 'yoga',
            'object': session,
            'scheduled_time': session.scheduled_time,
            'title': 'Yoga Session',
            'duration': session.duration,
            'staff': session.staff
        })
    
    # Add video conferences
    for conference in conferences:
        all_activities.append({
            'type': 'conference',
            'object': conference,
            'scheduled_time': conference.scheduled_time,
            'title': conference.title,
            'duration': conference.duration,
            'staff': conference.staff
        })
    
    # Add group conference if available
    if group_conference:
        # Convert time field to datetime for sorting
        now = timezone.now().date()
        group_time = timezone.make_aware(datetime.combine(now, group_conference.scheduled_time))
        
        all_activities.append({
            'type': 'group',
            'object': group_conference,
            'scheduled_time': group_time,
            'title': group_conference.title,
            'duration': group_conference.duration,
            'staff': None
        })
    
    # Sort all activities by scheduled time
    all_activities.sort(key=lambda x: x['scheduled_time'])
    
    context = {
        'user': user,
        'selected_day': selected_day,
        'application': application,
        'all_activities': all_activities,
        'days_range': range(1, 8)  # 1 to 7
    }
    
    return render(request, 'patient_activities.html', context)

@login_required
def join_group_conference(request):
    # Get today's group conference
    group_conf = GroupConference.objects.filter(is_active=True).first()
    if not group_conf:
        messages.error(request, 'No active group conference found.')
        return redirect('patient_activities')
    
    return render(request, 'group_conference_room.html', {
        'conference': group_conf
    })

@login_required
def manage_group_conference(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    if request.method == 'POST':
        # Handle form submission for creating/updating group conference
        conference_id = request.POST.get('conference_id')
        title = request.POST.get('title')
        scheduled_time = request.POST.get('scheduled_time')
        duration = request.POST.get('duration', 60)
        
        # Parse the scheduled_time - handle time-only format
        try:
            # First try the datetime format
            scheduled_datetime = datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            # If that fails, try time-only format and combine with today's date
            time_obj = datetime.strptime(scheduled_time, '%H:%M').time()
            today = datetime.now().date()
            scheduled_datetime = datetime.combine(today, time_obj)
        
        if conference_id:
            # Update existing conference
            try:
                conference = GroupConference.objects.get(id=conference_id)
                conference.title = title
                conference.scheduled_time = scheduled_datetime
                conference.duration = duration
                conference.save()
                messages.success(request, 'Group conference updated successfully.')
            except GroupConference.DoesNotExist:
                messages.error(request, 'Conference not found.')
        else:
            # Check if a group conference already exists
            existing_conference = GroupConference.objects.first()
            
            if existing_conference:
                # Update the existing conference instead of creating a new one
                existing_conference.title = title
                existing_conference.scheduled_time = scheduled_datetime
                existing_conference.duration = duration
                existing_conference.save()
                messages.success(request, 'Group conference updated successfully.')
            else:
                # Create a new conference if none exists
                try:
                    # Create a unique room name
                    room_name = f"group-{uuid.uuid4().hex[:8]}"
                    
                    GroupConference.objects.create(
                        title=title,
                        scheduled_time=scheduled_datetime,
                        duration=duration,
                        room_name=room_name
                    )
                    messages.success(request, 'Group conference created successfully.')
                except Exception as e:
                    messages.error(request, f'Error creating conference: {str(e)}')
    
    # Get all group conferences
    group_conferences = GroupConference.objects.all().order_by('-scheduled_time')
    
    # Get the first (most recent) group conference for the form
    group_conference = group_conferences.first()
    
    context = {
        'group_conferences': group_conferences,
        'group_conference': group_conference
    }
    
    return render(request, 'admin/manage_group_conference.html', context)

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            staff = Staff.objects.get(username=username, password=password)
            # Store staff info in session
            request.session['staff_id'] = staff.id
            request.session['staff_name'] = staff.name
            request.session['is_staff'] = True
            return redirect('staff_dashboard')
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('staff_login')
    
    return render(request, 'staff_login.html')

def staff_logout(request):
    # Clear staff session data
    request.session.pop('staff_name', None)
    request.session.pop('is_staff', None)
    return redirect('staff_login')

def staff_dashboard(request):
    # Check if staff is logged in
    if not request.session.get('is_staff'):
        return redirect('staff_login')
    
    staff_id = request.session.get('staff_id')
    
    try:
        # Get the staff object using ID
        staff = Staff.objects.get(id=staff_id)
        
        # Get assigned patients - only get the latest application for each patient
        patient_ids = set()
        assigned_patients = []
        
        for app in AddictionDetails.objects.filter(
            assigned_staff=staff,
            status='approved'
        ).order_by('-created_at'):
            if app.patient and app.patient.id not in patient_ids:
                patient_ids.add(app.patient.id)
                assigned_patients.append(app)
        
        # Get patients with unread messages
        patients_with_unread = []
        for application in assigned_patients:
            if application.patient:
                unread_count = Chat.objects.filter(
                    patient=application.patient,
                    staff=staff,
                    sent_by_patient=True,
                    is_read=False
                ).count()
                
                if unread_count > 0:
                    patients_with_unread.append({
                        'patient': application.patient,
                        'unread_count': unread_count
                    })
        
        # Get upcoming video conferences for this staff member's name
        # Since VideoConference uses CustomUser, we need to find the corresponding CustomUser
        now = timezone.now()
        try:
            custom_user = CustomUser.objects.get(first_name__icontains=staff.name.split()[0],
                                               last_name__icontains=staff.name.split()[-1])
            upcoming_conferences = VideoConference.objects.filter(
                staff=custom_user,
                scheduled_time__gte=now
            ).order_by('scheduled_time')
        except CustomUser.DoesNotExist:
            upcoming_conferences = VideoConference.objects.none()
        
        # Get group conferences
        group_conferences = GroupConference.objects.filter(
            scheduled_time__gte=now
        ).order_by('scheduled_time')
        
        context = {
            'staff': staff,
            'staff_name': staff.name,
            'assigned_patients': assigned_patients,
            'upcoming_conferences': upcoming_conferences,
            'group_conferences': group_conferences,
            'patients_with_unread': patients_with_unread
        }
        
        return render(request, 'staff_dashboard.html', context)
    
    except Staff.DoesNotExist:
        messages.error(request, 'Staff member not found')
        return redirect('staff_login')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2:
            try:
                # Check if email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists.')
                    return render(request, 'register.html')
                
                # Create the user
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.is_patient = True
                user.save()
                
                # Send registration confirmation email
                try:
                    send_registration_email(user)
                except Exception as e:
                    # Log the error but don't prevent registration
                    print(f"Error sending registration email: {e}")
                
                # Automatically log in the user
                login_user = authenticate(request, username=username, password=password1)
                if login_user:
                    login(request, login_user)
                    messages.success(request, 'Registration successful. A confirmation email has been sent to your email address.')
                    # Set session variable for redirect after message
                    request.session['message_redirect'] = reverse('home')
                    return render(request, 'message_redirect.html', {'redirect_url': reverse('home')})
                else:
                    # If auto-login fails, redirect to login page
                    messages.success(request, 'Registration successful. Please log in with your credentials.')
                    # Set session variable for redirect after message
                    request.session['message_redirect'] = reverse('user_login')
                    return render(request, 'message_redirect.html', {'redirect_url': reverse('user_login')})
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
                return render(request, 'register.html')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'register.html')

@login_required
def add_yoga(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return render(request, 'message_redirect.html', {'redirect_url': reverse('home')})
    
    if request.method == 'POST':
        # Create a new yoga session
        try:
            scheduled_time = request.POST.get('scheduled_time')
            duration = request.POST.get('duration')
            patient_id = request.POST.get('patient')
            staff_id = request.POST.get('staff')
            program_day = request.POST.get('program_day', 1)

            # Create the yoga session
            yoga_session = YogaSession.objects.create(
                patient_id=patient_id,
                staff_id=staff_id,
                scheduled_time=scheduled_time,
                duration=duration,
                program_day=program_day,
                is_active=True
            )
            
            messages.success(request, 'Yoga session scheduled successfully.')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('yoga_list')})
        except Exception as e:
            messages.error(request, f'Error scheduling yoga session: {str(e)}')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('add_yoga')})
    
    # Get staff and approved applications for the form
    staffs = Staff.objects.all().order_by('name')
    approved_applications = AddictionDetails.objects.filter(
        status='approved'
    ).select_related('patient', 'assigned_staff').order_by('-created_at')
    
    context = {
        'staffs': staffs,
        'approved_applications': approved_applications
    }
    
    return render(request, 'add_yoga.html', context)

@login_required
def yoga_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    # Get active yoga templates
    active_yogas = Yoga.objects.filter(is_active=True).select_related('patient', 'staff')
    
    # Get active yoga sessions
    yoga_sessions = YogaSession.objects.filter(is_active=True).select_related('patient', 'staff')
    
    return render(request, 'yoga_list.html', {
        'active_yogas': active_yogas,
        'yoga_sessions': yoga_sessions
    })

@login_required
def schedule_yoga(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    if request.method == 'POST':
        form = YogaSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yoga session scheduled successfully.')
            return redirect('yoga_list')
    
    return redirect('yoga_list')

@login_required
def cancel_yoga_session(request, session_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    yoga = get_object_or_404(Yoga, id=session_id)
    yoga.is_active = False
    yoga.save()
    messages.success(request, 'Yoga session cancelled successfully.')
    return redirect('yoga_list')

@login_required
def patient_yoga(request):
    if not request.user.is_patient:
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')
    
    # Get active yoga sessions for the current patient
    yoga_sessions = YogaSession.objects.filter(
        patient=request.user,
        is_active=True
    ).select_related('staff')

    # Example YouTube video URL (you can change this later)
    youtube_url = "https://www.youtube.com/embed/v7AYKMP6rOE"  # Sample yoga video
    
    return render(request, 'patient_yoga.html', {
        'yoga_sessions': yoga_sessions,
        'youtube_url': youtube_url
    })

@login_required
def join_yoga_session(request, session_id):
    if not request.user.is_patient:
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')
    
    yoga_session = get_object_or_404(YogaSession, id=session_id, patient=request.user, is_active=True)
    
    # Example YouTube video URL - you should replace this with your actual yoga videos
    youtube_url = "https://www.youtube.com/embed/v7AYKMP6rOE"
    
    context = {
        'yoga_session': yoga_session,
        'youtube_url': youtube_url
    }
    
    return render(request, 'group_conference_room.html', {
        'conference': group_conf
    })

@login_required
def cancel_conference(request, conference_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    conference = get_object_or_404(VideoConference, id=conference_id)
    conference.is_active = False
    conference.save()
    
    messages.success(request, 'Conference cancelled successfully.')
    return redirect('conference_list')

@login_required
def approve_application(request, application_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return render(request, 'message_redirect.html', {'redirect_url': reverse('home')})
    
    application = get_object_or_404(AddictionDetails, id=application_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        if not start_date:
            messages.error(request, 'Please select a start date for the program.')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('approve_application', kwargs={'application_id': application_id})})
            
        # Get the user associated with the application
        user = CustomUser.objects.get(email=application.patient_email)
        # Make them a patient
        user.is_patient = True
        user.save()
        # Update application status and start date
        application.status = 'approved'
        application.start_date = start_date
        application.save()
        messages.success(request, 'Application approved successfully.')
        return render(request, 'message_redirect.html', {'redirect_url': reverse('addiction_list')})
    
    context = {
        'application': application
    }
    return render(request, 'admin/approve_application.html', context)

@login_required
def patient_chat(request):
    user = request.user
    
    # Find the patient's application to get the assigned staff
    try:
        # Get the latest approved application instead of using get()
        application = AddictionDetails.objects.filter(
            patient=user, 
            status='approved'
        ).order_by('-created_at').first()
        
        if not application:
            messages.error(request, 'You do not have an approved application yet.')
            return redirect('user_dashboard')
            
        staff = application.assigned_staff
        
        if not staff:
            messages.error(request, 'You do not have an assigned staff member yet.')
            return redirect('user_dashboard')
        
        # Get chat history
        chat_history = Chat.objects.filter(patient=user, staff=staff)
        
        # Handle new message submission
        if request.method == 'POST':
            message = request.POST.get('message')
            if message:
                Chat.objects.create(
                    patient=user,
                    staff=staff,
                    message=message,
                    sent_by_patient=True
                )
                return redirect('patient_chat')
        
        context = {
            'staff': staff,
            'chat_history': chat_history
        }
        return render(request, 'patient_chat.html', context)
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('user_dashboard')

def staff_chat(request, patient_id):
    # Check if staff is logged in
    if not request.session.get('is_staff'):
        return redirect('staff_login')
    
    staff_id = request.session.get('staff_id')
    
    try:
        # Get the staff object
        staff = Staff.objects.get(id=staff_id)
        
        # Get the patient
        patient = CustomUser.objects.get(id=patient_id)
        
        # Get chat history
        chat_history = Chat.objects.filter(patient=patient, staff=staff)
        
        # Handle new message submission
        if request.method == 'POST':
            message = request.POST.get('message')
            if message:
                Chat.objects.create(
                    patient=patient,
                    staff=staff,
                    message=message,
                    sent_by_patient=False
                )
                
                # Mark all unread messages from this patient as read
                Chat.objects.filter(patient=patient, staff=staff, sent_by_patient=True, is_read=False).update(is_read=True)
                
                return redirect('staff_chat', patient_id=patient_id)
        
        # Mark all unread messages from this patient as read when viewing the chat
        Chat.objects.filter(patient=patient, staff=staff, sent_by_patient=True, is_read=False).update(is_read=True)
        
        context = {
            'staff': staff,
            'patient': patient,
            'chat_history': chat_history
        }
        return render(request, 'staff_chat.html', context)
    
    except (Staff.DoesNotExist, CustomUser.DoesNotExist):
        messages.error(request, 'Staff or patient not found')
        return redirect('staff_dashboard')

@login_required
def add_testimonial(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        
        if content and rating:
            testimonial = Testimonial.objects.create(
                patient=request.user,
                content=content,
                rating=int(rating),
                is_approved=True  # Auto-approve testimonials
            )
            messages.success(request, 'Thank you for your review! It is now visible on the home page.')
            return redirect('home')  # Redirect to home page to see the testimonial
        else:
            messages.error(request, 'Please provide both content and rating.')
    
    # Check if user already has a testimonial
    existing_testimonial = Testimonial.objects.filter(patient=request.user).first()
    
    return render(request, 'add_testimonial.html', {
        'existing_testimonial': existing_testimonial
    })

@login_required
def edit_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id, patient=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        
        if content and rating:
            testimonial.content = content
            testimonial.rating = int(rating)
            testimonial.is_approved = True  # Auto-approve edited testimonials
            testimonial.save()
            messages.success(request, 'Your review has been updated and is now visible on the home page.')
            return redirect('home')  # Redirect to home page to see the testimonial
        else:
            messages.error(request, 'Please provide both content and rating.')
    
    return render(request, 'edit_testimonial.html', {
        'testimonial': testimonial
    })

@login_required
def delete_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id, patient=request.user)
    
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('user_dashboard')
    
    return render(request, 'delete_testimonial.html', {
        'testimonial': testimonial
    })

@login_required
def admin_testimonials(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    testimonials = Testimonial.objects.all().order_by('-created_at')
    
    return render(request, 'admin_testimonials.html', {
        'testimonials': testimonials
    })

@login_required
def approve_testimonial(request, testimonial_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.is_approved = True
    testimonial.save()
    
    messages.success(request, 'Testimonial has been approved.')
    return redirect('admin_testimonials')

@login_required
def reject_testimonial(request, testimonial_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.is_approved = False
    testimonial.save()
    
    messages.success(request, 'Testimonial has been rejected.')
    return redirect('admin_testimonials')

@login_required
def generate_application_pdf(request, application_id):
    application = get_object_or_404(AddictionDetails, id=application_id)
    
    template = get_template('pdf_templates/application_pdf.html')
    context = {
        'application': application
    }
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    
    # Create a sanitized name (remove spaces and special characters)
    sanitized_name = ''.join(e for e in application.patient.get_full_name() if e.isalnum() or e == ' ').replace(' ', '_')
    
    response['Content-Disposition'] = f'attachment; filename="{sanitized_name}_application.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def generate_application_pdf_all(request):
    applications = AddictionDetails.objects.all().order_by('-created_at')
    
    template = get_template('pdf_templates/all_applications_pdf.html')
    context = {
        'applications': applications,
        'generated_date': timezone.now()
    }
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="all_applications_{timezone.now().strftime("%Y%m%d")}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def submit_addiction(request):
    if request.method == 'POST':
        form = AddictionDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            addiction = form.save(commit=False)
            addiction.patient = request.user  # Set the patient to current user
            addiction.patient_email = request.user.email
            addiction.save()
            
            # Send application submission confirmation email
            try:
                send_application_submitted_email(addiction)
            except Exception as e:
                # Log the error but don't prevent application submission
                print(f"Error sending application submission email: {e}")
                
            messages.success(request, 'Your application has been submitted successfully. A confirmation email has been sent to your email address.')
            return render(request, 'message_redirect.html', {'redirect_url': reverse('user_dashboard')})
    else:
        form = AddictionDetailsForm()
    
    return render(request, 'submit_addiction.html', {
        'form': form
    })