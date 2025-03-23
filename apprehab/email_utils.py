from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_registration_email(user):
    """
    Send a welcome email to newly registered users
    """
    subject = 'Welcome to Rehab Center - Registration Successful'
    html_message = render_to_string('email/registration_email.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_application_submitted_email(application):
    """
    Send an email notification when an application is submitted
    """
    subject = 'Rehab Center - Application Submitted Successfully'
    html_message = render_to_string('email/application_submitted_email.html', {
        'application': application,
    })
    plain_message = strip_tags(html_message)
    
    # Send to patient
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [application.patient_email],
        html_message=html_message,
        fail_silently=False,
    )
    
    # Send to guide/parent if email is provided
    if application.guider_email:
        guide_subject = 'Rehab Center - Application Submitted for Your Dependent'
        guide_html_message = render_to_string('email/guide_application_submitted_email.html', {
            'application': application,
        })
        guide_plain_message = strip_tags(guide_html_message)
        
        send_mail(
            guide_subject,
            guide_plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [application.guider_email],
            html_message=guide_html_message,
            fail_silently=False,
        )

def send_application_status_update_email(application):
    """
    Send an email notification when an application status is updated (approved/rejected)
    """
    status = application.get_status_display()
    subject = f'Rehab Center - Application {status}'
    
    template = 'email/application_approved_email.html' if application.status == 'approved' else 'email/application_rejected_email.html'
    html_message = render_to_string(template, {
        'application': application,
    })
    plain_message = strip_tags(html_message)
    
    # Send to patient
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [application.patient_email],
        html_message=html_message,
        fail_silently=False,
    )
    
    # Send to guide/parent if email is provided
    if application.guider_email:
        guide_subject = f'Rehab Center - Dependent\'s Application {status}'
        guide_template = 'email/guide_application_approved_email.html' if application.status == 'approved' else 'email/guide_application_rejected_email.html'
        guide_html_message = render_to_string(guide_template, {
            'application': application,
        })
        guide_plain_message = strip_tags(guide_html_message)
        
        send_mail(
            guide_subject,
            guide_plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [application.guider_email],
            html_message=guide_html_message,
            fail_silently=False,
        )

def send_staff_account_email(staff, password):
    """
    Send an email to newly created staff members with their login credentials
    """
    subject = 'Rehab Center - Staff Account Created'
    html_message = render_to_string('email/staff_account_email.html', {
        'staff': staff,
        'username': staff.email,
        'password': password,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [staff.email],
        html_message=html_message,
        fail_silently=False,
    )
