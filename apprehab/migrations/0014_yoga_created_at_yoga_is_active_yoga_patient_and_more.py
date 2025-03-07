# Generated by Django 5.1.5 on 2025-03-02 12:55

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apprehab', '0013_yoga_yogasession'),
    ]

    operations = [
        migrations.AddField(
            model_name='yoga',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='yoga',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='yoga',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_yogas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='yoga',
            name='staff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_yogas', to='apprehab.staff'),
        ),
    ]
