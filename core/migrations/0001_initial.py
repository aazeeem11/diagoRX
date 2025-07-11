# Generated by Django 5.2.4 on 2025-07-05 09:20

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('blood_group', models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3)),
                ('contact_number', models.CharField(blank=True, max_length=15)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.TextField(blank=True)),
                ('symptoms', models.TextField()),
                ('medical_history', models.TextField(blank=True)),
                ('current_medications', models.TextField(blank=True)),
                ('allergies', models.TextField(blank=True)),
                ('ecg_report', models.FileField(blank=True, null=True, upload_to='ecg_reports/')),
                ('lab_report', models.FileField(blank=True, null=True, upload_to='lab_reports/')),
                ('xray_report', models.FileField(blank=True, null=True, upload_to='xray_reports/')),
                ('ai_diagnosis', models.TextField(blank=True)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('recommended_tests', models.TextField(blank=True)),
                ('treatment_plan', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Patient Record',
                'verbose_name_plural': 'Patient Records',
                'ordering': ['-created_at'],
            },
        ),
    ]
