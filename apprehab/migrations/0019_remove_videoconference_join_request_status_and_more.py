# Generated by Django 5.1.5 on 2025-03-02 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apprehab', '0018_videoconference_join_request_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videoconference',
            name='join_request_status',
        ),
        migrations.RemoveField(
            model_name='videoconference',
            name='join_request_time',
        ),
    ]
