from django.urls import include, path
from . import views 
from .views import update_field_name, schedule_conference, conference_list, patient_conferences, join_conference, user_dashboard, patient_progress, review_application, user_profile, patient_chat, staff_chat
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('admin-login/', views.admin_login, name='admin_login' ),   
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('front-end/', views.front_end, name='front_end'),
    path('back-end/', views.back_end, name='back_end'),
    path('register/', views.register, name='user_register'), 

    path('register/', views.register, name='register'),  

    path('login/', views.user_login, name='user_login'),  # URL for user login
    path('admin-user-list/', views.admin_user_list, name='admin_user_list'), 
    path('gallery/', views.gallery, name='gallery'),  # URL for gallery
    path('gallery/add/', views.add_image, name='add_image'),  # URL for adding an image
    path('gallery/edit/<int:pk>/', views.edit_image, name='edit_image'),  # URL for editing an image
    path('gallery/delete/<int:pk>/', views.delete_image, name='delete_image'),  # URL for deleting an image
    path('user_gallery/', views.user_gallery, name='user_gallery'),  # URL for user gallery view
    path('logout/', views.user_logout, name='logout'),  # URL for logout
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('update_field_name/', update_field_name, name='update_field_name'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('apply/', views.submit_addiction, name='apply_treatment'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('staff_list/', views.staff_list, name='staff_list'),
    path('assign_patient/<int:staff_id>/', views.assign_patient, name='assign_patient'),
    path('submit_addiction/', views.submit_addiction, name='submit_addiction'),
    path('addiction_list/', views.addiction_list, name='addiction_list'),
    path('manage/conference/schedule/', schedule_conference, name='schedule_conference'),
    path('manage/conferences/', conference_list, name='conference_list'),
    path('patient/<int:patient_id>/conferences/', patient_conferences, name='patient_conferences'),
    path('conference/<int:conference_id>/join/', join_conference, name='join_conference'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('user/progress/', patient_progress, name='patient_progress'),
    path('user/profile/', user_profile, name='user_profile'),
    path('applications/', views.addiction_list, name='addiction_list'),
    path('application/<int:application_id>/review/', views.review_application, name='review_application'),
    path('application/<int:application_id>/set-start-date/', views.set_program_start_date, name='set_program_start_date'),
    path('application/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('application/<int:application_id>/assign/', views.assign_staff, name='assign_staff'),
    path('conference/schedule/', views.schedule_conference, name='schedule_conference'),
    path('conference/list/', views.conference_list, name='conference_list'),
    path('conference/<int:conference_id>/room/', views.conference_room, name='conference_room'),
    path('conference/<int:conference_id>/cancel/', views.cancel_conference, name='cancel_conference'),
    path('conference/<int:conference_id>/accept-patient/', views.accept_patient_join, name='accept_patient_join'),
    path('conference/<int:conference_id>/reject-patient/', views.reject_patient_join, name='reject_patient_join'),
    path('patient/activities/', views.patient_activities, name='patient_activities'),
    path('patient/join-conference/<int:conference_id>/', views.patient_join_conference, name='patient_join_conference'),
    path('patients/', views.patient_list, name='patients'),
    path('patient_list/', views.patient_list, name='patient_list'),
    
    # Yoga URLs - Single set of paths
    path('yoga/add/', views.add_yoga, name='add_yoga'),
    path('yoga/list/', views.yoga_list, name='yoga_list'),
    path('yoga/schedule/', views.schedule_yoga, name='schedule_yoga'),
    path('yoga/cancel/<int:session_id>/', views.cancel_yoga_session, name='cancel_yoga_session'),
    path('yoga/patient/', views.patient_yoga, name='patient_yoga'),
    
    path('manage-group-conference/', views.manage_group_conference, name='manage_group_conference'),
    path('group-conference/', views.join_group_conference, name='join_group_conference'),
    path('patient/activities/', views.patient_activities, name='patient_activities'),

    # Staff URLs
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    
    # Chat URLs
    path('patient/chat/', views.patient_chat, name='patient_chat'),
    path('staff/chat/<int:patient_id>/', views.staff_chat, name='staff_chat'),
    
    # Testimonial URLs
    path('testimonial/add/', views.add_testimonial, name='add_testimonial'),
    path('testimonial/edit/<int:testimonial_id>/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonial/delete/<int:testimonial_id>/', views.delete_testimonial, name='delete_testimonial'),
    
    # Admin Testimonial Management
    path('admin/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    path('admin/testimonial/<int:testimonial_id>/approve/', views.approve_testimonial, name='approve_testimonial'),
    path('admin/testimonial/<int:testimonial_id>/reject/', views.reject_testimonial, name='reject_testimonial'),
    
    # PDF Generation
    path('application/<int:application_id>/pdf/', views.generate_application_pdf, name='generate_application_pdf'),
    path('applications/pdf/all/', views.generate_application_pdf_all, name='generate_application_pdf_all'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
