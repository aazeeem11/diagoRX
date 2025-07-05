# PatientRecord model with FileFields

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class PatientRecord(models.Model):
    """Model for storing patient medical records and diagnosis."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    # Patient Information
    patient_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in °C")
    systolic_bp = models.IntegerField(null=True, blank=True, help_text="Systolic blood pressure (mmHg)")
    diastolic_bp = models.IntegerField(null=True, blank=True, help_text="Diastolic blood pressure (mmHg)")
    pulse_rate = models.IntegerField(null=True, blank=True, help_text="Pulse rate (beats per minute)")
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="Respiratory rate (breaths per minute)")
    oxygen_saturation = models.IntegerField(null=True, blank=True, help_text="Oxygen saturation (%)")
    
    # Medical Information
    symptoms = models.TextField()
    medical_history = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    
    # File Uploads
    ecg_report = models.FileField(upload_to='ecg_reports/', blank=True, null=True)
    lab_report = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    xray_report = models.FileField(upload_to='xray_reports/', blank=True, null=True)
    
    # Diagnosis Results
    ai_diagnosis = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    recommended_tests = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    prescribed_medications = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient Record'
        verbose_name_plural = 'Patient Records'
    
    def __str__(self):
        return f"{self.patient_name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return f'/prescription/{self.id}/'
    
    def get_blood_pressure_display(self):
        """Get formatted blood pressure display."""
        if self.systolic_bp and self.diastolic_bp:
            return f"{self.systolic_bp}/{self.diastolic_bp} mmHg"
        elif self.systolic_bp:
            return f"{self.systolic_bp}/-- mmHg"
        elif self.diastolic_bp:
            return f"--/{self.diastolic_bp} mmHg"
        return "Not recorded"
    
    def get_vital_status(self):
        """Get overall vital signs status."""
        status = []
        
        # Temperature check
        if self.temperature:
            if self.temperature < 36.0:
                status.append("Low temperature")
            elif self.temperature > 37.5:
                status.append("Fever")
        
        # Blood pressure check
        if self.systolic_bp and self.diastolic_bp:
            if self.systolic_bp < 90 or self.diastolic_bp < 60:
                status.append("Low blood pressure")
            elif self.systolic_bp > 140 or self.diastolic_bp > 90:
                status.append("High blood pressure")
        
        # Pulse rate check
        if self.pulse_rate:
            if self.pulse_rate < 60:
                status.append("Bradycardia")
            elif self.pulse_rate > 100:
                status.append("Tachycardia")
        
        # Oxygen saturation check
        if self.oxygen_saturation:
            if self.oxygen_saturation < 95:
                status.append("Low oxygen saturation")
        
        return status if status else ["Normal"]
    
    def delete(self, *args, **kwargs):
        """Override delete to clean up uploaded files."""
        # Delete uploaded files when record is deleted
        if self.ecg_report:
            if os.path.exists(self.ecg_report.path):
                os.remove(self.ecg_report.path)
        if self.lab_report:
            if os.path.exists(self.lab_report.path):
                os.remove(self.lab_report.path)
        if self.xray_report:
            if os.path.exists(self.xray_report.path):
                os.remove(self.xray_report.path)
        super().delete(*args, **kwargs)
