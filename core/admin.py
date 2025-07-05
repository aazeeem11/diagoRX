# Register models

from django.contrib import admin
from .models import PatientRecord

@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    """Admin interface for PatientRecord model."""
    
    list_display = [
        'patient_name', 'age', 'gender', 'blood_group', 
        'ai_diagnosis', 'confidence_score', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'gender', 'blood_group', 'created_at', 'created_by'
    ]
    
    search_fields = [
        'patient_name', 'symptoms', 'ai_diagnosis', 'contact_number', 'email'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'confidence_score'
    ]
    
    fieldsets = (
        ('Patient Information', {
            'fields': (
                'patient_name', 'age', 'gender', 'blood_group',
                'contact_number', 'email', 'address'
            )
        }),
        ('Medical Information', {
            'fields': (
                'symptoms', 'medical_history', 'current_medications', 'allergies'
            )
        }),
        ('Medical Reports', {
            'fields': (
                'ecg_report', 'lab_report', 'xray_report'
            ),
            'classes': ('collapse',)
        }),
        ('AI Diagnosis', {
            'fields': (
                'ai_diagnosis', 'confidence_score', 'recommended_tests', 'treatment_plan'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new records
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
