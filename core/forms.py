# PatientForm with uploads

from django import forms
from .models import PatientRecord

class PatientForm(forms.ModelForm):
    """Form for patient record creation and editing."""
    
    class Meta:
        model = PatientRecord
        fields = [
            'patient_name', 'age', 'gender', 'blood_group', 'contact_number', 'email', 'address',
            'temperature', 'systolic_bp', 'diastolic_bp', 'pulse_rate', 'respiratory_rate', 'oxygen_saturation',
            'symptoms', 'medical_history', 'current_medications', 'allergies',
            'ecg_report', 'lab_report', 'xray_report'
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age in years',
                'min': '0',
                'max': '150'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Patient address'
            }),
            # Vital Signs
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Temperature in °C',
                'step': '0.1',
                'min': '30.0',
                'max': '45.0'
            }),
            'systolic_bp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Systolic BP (mmHg)',
                'min': '50',
                'max': '250'
            }),
            'diastolic_bp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Diastolic BP (mmHg)',
                'min': '30',
                'max': '150'
            }),
            'pulse_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pulse rate (bpm)',
                'min': '30',
                'max': '200'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Respiratory rate (breaths/min)',
                'min': '8',
                'max': '50'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Oxygen saturation (%)',
                'min': '70',
                'max': '100'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Describe patient symptoms in detail'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Previous medical conditions, surgeries, etc.'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Current medications and dosages'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '2',
                'placeholder': 'Known allergies (drugs, food, etc.)'
            }),
            'ecg_report': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
            'lab_report': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.txt,.doc,.docx'
            }),
            'xray_report': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate blood pressure
        systolic = cleaned_data.get('systolic_bp')
        diastolic = cleaned_data.get('diastolic_bp')
        
        if systolic and diastolic:
            if systolic <= diastolic:
                raise forms.ValidationError(
                    "Systolic blood pressure must be higher than diastolic blood pressure."
                )
        
        # Validate temperature
        temperature = cleaned_data.get('temperature')
        if temperature:
            if temperature < 30.0 or temperature > 45.0:
                raise forms.ValidationError(
                    "Temperature must be between 30.0°C and 45.0°C."
                )
        
        # Validate pulse rate
        pulse_rate = cleaned_data.get('pulse_rate')
        if pulse_rate:
            if pulse_rate < 30 or pulse_rate > 200:
                raise forms.ValidationError(
                    "Pulse rate must be between 30 and 200 beats per minute."
                )
        
        # Validate respiratory rate
        respiratory_rate = cleaned_data.get('respiratory_rate')
        if respiratory_rate:
            if respiratory_rate < 8 or respiratory_rate > 50:
                raise forms.ValidationError(
                    "Respiratory rate must be between 8 and 50 breaths per minute."
                )
        
        # Validate oxygen saturation
        oxygen_saturation = cleaned_data.get('oxygen_saturation')
        if oxygen_saturation:
            if oxygen_saturation < 70 or oxygen_saturation > 100:
                raise forms.ValidationError(
                    "Oxygen saturation must be between 70% and 100%."
                )
        
        return cleaned_data
