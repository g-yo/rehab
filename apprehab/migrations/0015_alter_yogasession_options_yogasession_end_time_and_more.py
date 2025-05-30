# Generated by Django 5.1.5 on 2025-03-02 13:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apprehab', '0014_yoga_created_at_yoga_is_active_yoga_patient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='yogasession',
            options={'ordering': ['-scheduled_time']},
        ),
        migrations.AddField(
            model_name='yogasession',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='yogasession',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='yogasession',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='yogasession',
            name='duration',
            field=models.IntegerField(default=60),
        ),
        migrations.AlterField(
            model_name='yogasession',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_yoga_sessions', to=settings.AUTH_USER_MODEL),
        ),
    ]
