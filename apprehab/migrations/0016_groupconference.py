# Generated by Django 5.1.5 on 2025-03-02 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apprehab', '0015_alter_yogasession_options_yogasession_end_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupConference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Daily Group Meeting', max_length=200)),
                ('scheduled_time', models.TimeField(default='17:00')),
                ('duration', models.IntegerField(default=60, help_text='Duration in minutes')),
                ('room_name', models.CharField(blank=True, max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
