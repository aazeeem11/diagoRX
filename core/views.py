# Dashboard, diagnosis logic, save to DB, PDF

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import joblib
import os
import numpy as np
from .models import PatientRecord
from .forms import PatientForm
from .utils import generate_pdf_report
from .ai_analysis import MedicalImageAnalyzer

# Initialize AI analyzer
ai_analyzer = MedicalImageAnalyzer()

# Load AI models (simulated for demo)
def load_ai_models():
    """Load AI models for diagnosis."""
    try:
        # In a real application, you would load actual trained models
        # For demo purposes, we'll simulate the models
        return {
            'symptom_classifier': None,  # joblib.load('core/ai_models/symptom_classifier.pkl')
            'ecg_model': None,  # load_model('core/ai_models/ecg_model.h5')
        }
    except Exception as e:
        print(f"Error loading AI models: {e}")
        return {}

# Initialize AI models
AI_MODELS = load_ai_models()

@login_required
def dashboard(request):
    """Main dashboard view for patient data entry."""
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient_record = form.save(commit=False)
            patient_record.created_by = request.user
            
            # Perform AI diagnosis with enhanced analysis
            diagnosis_result = perform_ai_diagnosis(patient_record)
            patient_record.ai_diagnosis = diagnosis_result['diagnosis']
            patient_record.confidence_score = diagnosis_result['confidence']
            patient_record.recommended_tests = diagnosis_result['recommended_tests']
            patient_record.treatment_plan = diagnosis_result['treatment_plan']
            
            # Format and save medications
            medications_text = ""
            for med in diagnosis_result['medications']:
                medications_text += f"• {med['name']} - {med['dosage']}\n"
                medications_text += f"  Frequency: {med['frequency']}\n"
                medications_text += f"  Duration: {med['duration']}\n\n"
            patient_record.prescribed_medications = medications_text.strip()
            
            # Add AI analysis results if files are uploaded
            if diagnosis_result.get('ai_analysis'):
                patient_record.ai_diagnosis += f"\n\nAI Analysis:\n{diagnosis_result['ai_analysis']}"
            
            patient_record.save()
            messages.success(request, 'Patient record created successfully!')
            return redirect('core:prescription', record_id=patient_record.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm()
    
    # Get recent records for quick access
    recent_records = PatientRecord.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'recent_records': recent_records,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def prescription(request, record_id):
    """Display diagnosis results and prescription."""
    patient_record = get_object_or_404(PatientRecord, id=record_id, created_by=request.user)
    
    context = {
        'patient_record': patient_record,
    }
    return render(request, 'core/prescription.html', context)

@login_required
def history(request):
    """Display patient history with search and filtering."""
    search_query = request.GET.get('search', '')
    gender_filter = request.GET.get('gender', '')
    date_filter = request.GET.get('date', '')
    
    records = PatientRecord.objects.filter(created_by=request.user)
    
    # Apply search filter
    if search_query:
        records = records.filter(
            Q(patient_name__icontains=search_query) |
            Q(symptoms__icontains=search_query) |
            Q(ai_diagnosis__icontains=search_query)
        )
    
    # Apply gender filter
    if gender_filter:
        records = records.filter(gender=gender_filter)
    
    # Apply date filter
    if date_filter:
        records = records.filter(created_at__date=date_filter)
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'gender_filter': gender_filter,
        'date_filter': date_filter,
        'gender_choices': PatientRecord.GENDER_CHOICES,
    }
    return render(request, 'core/history.html', context)

@login_required
def download_pdf(request, record_id):
    """Download PDF report for a patient record."""
    patient_record = get_object_or_404(PatientRecord, id=record_id, created_by=request.user)
    
    # Generate PDF
    pdf_content = generate_pdf_report(patient_record)
    
    # Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="patient_report_{patient_record.id}.pdf"'
    
    return response

@login_required
def delete_record(request, record_id):
    """Delete a patient record."""
    patient_record = get_object_or_404(PatientRecord, id=record_id, created_by=request.user)
    
    if request.method == 'POST':
        patient_name = patient_record.patient_name
        patient_record.delete()
        messages.success(request, f'Patient record for {patient_name} has been deleted successfully.')
        return redirect('core:history')
    
    context = {
        'patient_record': patient_record,
    }
    return render(request, 'core/delete_confirm.html', context)

def perform_ai_diagnosis(patient_record):
    """Perform AI-based diagnosis using symptoms, vital signs, and uploaded files with free APIs."""
    
    symptoms = patient_record.symptoms.lower()
    diagnosis_result = {
        'diagnosis': '',
        'confidence': 0.0,
        'recommended_tests': '',
        'treatment_plan': '',
        'medications': [],
        'ai_analysis': ''
    }
    
    # Get vital signs for free API analysis
    vitals = {}
    if patient_record.temperature:
        vitals['temperature'] = patient_record.temperature
    if patient_record.systolic_bp and patient_record.diastolic_bp:
        vitals['blood_pressure'] = f"{patient_record.systolic_bp}/{patient_record.diastolic_bp}"
    if patient_record.pulse_rate:
        vitals['pulse'] = patient_record.pulse_rate
    
    # Use free diagnosis API
    try:
        free_diagnosis = ai_analyzer.get_free_diagnosis(symptoms, vitals)
        
        # Update diagnosis result with free API data
        if free_diagnosis.get('possible_conditions'):
            diagnosis_result['diagnosis'] = ', '.join(free_diagnosis['possible_conditions'])
        else:
            diagnosis_result['diagnosis'] = 'General consultation required'
        
        diagnosis_result['confidence'] = free_diagnosis.get('confidence', 0.5)
        
        # Add recommendations from free API
        if free_diagnosis.get('recommendations'):
            diagnosis_result['treatment_plan'] = '; '.join(free_diagnosis['recommendations'])
        
        # Add medications from free API
        if free_diagnosis.get('medications'):
            diagnosis_result['medications'] = free_diagnosis['medications']
        
        # Add vital signs analysis from free API
        if free_diagnosis.get('vital_status'):
            vital_analysis = []
            for vital, status in free_diagnosis['vital_status'].items():
                vital_analysis.append(f"{vital.title()}: {status}")
            if vital_analysis:
                diagnosis_result['ai_analysis'] = f"Vital Signs Analysis:\n" + '\n'.join([f"• {vital}" for vital in vital_analysis])
        
    except Exception as e:
        print(f"Free diagnosis API failed: {e}")
        # Fall back to original diagnosis logic
    
    # Enhanced symptom-based diagnosis with medication recommendations
    if any(word in symptoms for word in ['chest pain', 'shortness of breath', 'heart', 'angina']):
        diagnosis_result['diagnosis'] = 'Possible cardiovascular issue (Angina/Coronary Artery Disease)'
        diagnosis_result['confidence'] = 0.75
        diagnosis_result['recommended_tests'] = 'ECG, Blood pressure monitoring, Cardiac enzymes, Stress test'
        diagnosis_result['treatment_plan'] = 'Consult cardiologist, Monitor vital signs, Avoid strenuous activity, Low-sodium diet'
        diagnosis_result['medications'] = [
            {'name': 'Nitroglycerin', 'dosage': '0.4mg sublingual', 'frequency': 'As needed for chest pain', 'duration': 'Until symptoms resolve'},
            {'name': 'Aspirin', 'dosage': '81mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
            {'name': 'Metoprolol', 'dosage': '25-50mg', 'frequency': 'Twice daily', 'duration': 'As prescribed by cardiologist'},
            {'name': 'Atorvastatin', 'dosage': '10-20mg', 'frequency': 'Once daily', 'duration': 'Long-term'}
        ]
    
    elif any(word in symptoms for word in ['fever', 'cough', 'cold', 'sore throat', 'runny nose']):
        diagnosis_result['diagnosis'] = 'Upper respiratory infection (Common Cold/Flu)'
        diagnosis_result['confidence'] = 0.85
        diagnosis_result['recommended_tests'] = 'Chest X-ray, Blood count, Sputum culture, COVID-19 test'
        diagnosis_result['treatment_plan'] = 'Rest, Hydration, Over-the-counter medications, Steam inhalation'
        diagnosis_result['medications'] = [
            {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': '3-5 days'},
            {'name': 'Ibuprofen', 'dosage': '400-600mg', 'frequency': 'Every 6-8 hours', 'duration': '3-5 days'},
            {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'duration': 'Until cough improves'},
            {'name': 'Pseudoephedrine', 'dosage': '30-60mg', 'frequency': 'Every 4-6 hours', 'duration': '3-5 days'},
            {'name': 'Zinc supplements', 'dosage': '15-30mg', 'frequency': 'Once daily', 'duration': '5-7 days'}
        ]
    
    elif any(word in symptoms for word in ['headache', 'migraine', 'dizziness', 'tension']):
        diagnosis_result['diagnosis'] = 'Tension headache or migraine'
        diagnosis_result['confidence'] = 0.70
        diagnosis_result['recommended_tests'] = 'Neurological examination, Blood pressure, Eye examination, CT scan if severe'
        diagnosis_result['treatment_plan'] = 'Pain management, Stress reduction, Regular sleep pattern, Avoid triggers'
        diagnosis_result['medications'] = [
            {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
            {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
            {'name': 'Sumatriptan', 'dosage': '25-100mg', 'frequency': 'At onset of migraine', 'duration': 'As needed'},
            {'name': 'Propranolol', 'dosage': '20-40mg', 'frequency': 'Twice daily', 'duration': 'As prescribed for prevention'}
        ]
    
    elif any(word in symptoms for word in ['stomach', 'abdominal', 'nausea', 'vomiting', 'diarrhea', 'acid reflux']):
        diagnosis_result['diagnosis'] = 'Gastrointestinal issue (Gastritis/GERD)'
        diagnosis_result['confidence'] = 0.80
        diagnosis_result['recommended_tests'] = 'Blood tests, Ultrasound, Endoscopy if needed, H. pylori test'
        diagnosis_result['treatment_plan'] = 'Diet modification, Hydration, Consult gastroenterologist, Avoid spicy foods'
        diagnosis_result['medications'] = [
            {'name': 'Omeprazole', 'dosage': '20mg', 'frequency': 'Once daily', 'duration': '4-8 weeks'},
            {'name': 'Ranitidine', 'dosage': '150mg', 'frequency': 'Twice daily', 'duration': '4-8 weeks'},
            {'name': 'Metoclopramide', 'dosage': '10mg', 'frequency': 'Three times daily', 'duration': 'As needed for nausea'},
            {'name': 'Loperamide', 'dosage': '2mg', 'frequency': 'After each loose stool', 'duration': 'Until diarrhea resolves'}
        ]
    
    elif any(word in symptoms for word in ['joint pain', 'arthritis', 'swelling', 'stiffness']):
        diagnosis_result['diagnosis'] = 'Osteoarthritis or inflammatory arthritis'
        diagnosis_result['confidence'] = 0.75
        diagnosis_result['recommended_tests'] = 'X-rays, Blood tests (ESR, CRP), Joint fluid analysis'
        diagnosis_result['treatment_plan'] = 'Physical therapy, Weight management, Joint protection, Regular exercise'
        diagnosis_result['medications'] = [
            {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Three times daily', 'duration': 'As needed'},
            {'name': 'Naproxen', 'dosage': '250-500mg', 'frequency': 'Twice daily', 'duration': 'As needed'},
            {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
            {'name': 'Glucosamine', 'dosage': '1500mg', 'frequency': 'Once daily', 'duration': 'Long-term'}
        ]
    
    elif any(word in symptoms for word in ['anxiety', 'depression', 'stress', 'insomnia', 'mood']):
        diagnosis_result['diagnosis'] = 'Anxiety or depressive disorder'
        diagnosis_result['confidence'] = 0.70
        diagnosis_result['recommended_tests'] = 'Psychological evaluation, Blood tests (thyroid, B12), Depression screening'
        diagnosis_result['treatment_plan'] = 'Counseling, Stress management, Regular exercise, Sleep hygiene'
        diagnosis_result['medications'] = [
            {'name': 'Sertraline', 'dosage': '25-50mg', 'frequency': 'Once daily', 'duration': 'As prescribed by psychiatrist'},
            {'name': 'Alprazolam', 'dosage': '0.25-0.5mg', 'frequency': 'As needed for anxiety', 'duration': 'Short-term only'},
            {'name': 'Melatonin', 'dosage': '3-5mg', 'frequency': 'Once daily at bedtime', 'duration': 'As needed for sleep'},
            {'name': 'Lavender supplements', 'dosage': '80mg', 'frequency': 'Once daily', 'duration': '4-6 weeks'}
        ]
    
    elif any(word in symptoms for word in ['diabetes', 'high blood sugar', 'frequent urination', 'thirst']):
        diagnosis_result['diagnosis'] = 'Diabetes mellitus (Type 2)'
        diagnosis_result['confidence'] = 0.80
        diagnosis_result['recommended_tests'] = 'Fasting blood glucose, HbA1c, Lipid profile, Kidney function tests'
        diagnosis_result['treatment_plan'] = 'Diet modification, Regular exercise, Blood sugar monitoring, Weight management'
        diagnosis_result['medications'] = [
            {'name': 'Metformin', 'dosage': '500-1000mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
            {'name': 'Glimepiride', 'dosage': '1-4mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
            {'name': 'Sitagliptin', 'dosage': '100mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
            {'name': 'Insulin (if needed)', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'}
        ]
    
    else:
        diagnosis_result['diagnosis'] = 'General consultation required'
        diagnosis_result['confidence'] = 0.50
        diagnosis_result['recommended_tests'] = 'Complete blood count, Basic metabolic panel, Physical examination'
        diagnosis_result['treatment_plan'] = 'Follow up with primary care physician, Maintain healthy lifestyle'
        diagnosis_result['medications'] = [
            {'name': 'Multivitamin', 'dosage': 'As directed', 'frequency': 'Once daily', 'duration': 'Long-term'},
            {'name': 'Vitamin D', 'dosage': '1000-2000 IU', 'frequency': 'Once daily', 'duration': 'Long-term'}
        ]
    
    # Enhanced AI analysis considering vital signs
    vital_signs_analysis = []
    
    # Analyze vital signs and adjust diagnosis
    if patient_record.temperature:
        if patient_record.temperature > 37.5:
            vital_signs_analysis.append("Fever detected - may indicate infection")
            diagnosis_result['confidence'] += 0.05
        elif patient_record.temperature < 36.0:
            vital_signs_analysis.append("Low temperature - may indicate hypothermia or shock")
            diagnosis_result['confidence'] += 0.05
    
    if patient_record.systolic_bp and patient_record.diastolic_bp:
        if patient_record.systolic_bp > 140 or patient_record.diastolic_bp > 90:
            vital_signs_analysis.append("Hypertension detected - cardiovascular risk factor")
            diagnosis_result['confidence'] += 0.05
        elif patient_record.systolic_bp < 90 or patient_record.diastolic_bp < 60:
            vital_signs_analysis.append("Hypotension detected - may indicate shock or dehydration")
            diagnosis_result['confidence'] += 0.05
    
    if patient_record.pulse_rate:
        if patient_record.pulse_rate > 100:
            vital_signs_analysis.append("Tachycardia detected - may indicate stress, fever, or cardiac issue")
            diagnosis_result['confidence'] += 0.05
        elif patient_record.pulse_rate < 60:
            vital_signs_analysis.append("Bradycardia detected - may indicate cardiac conduction issue")
            diagnosis_result['confidence'] += 0.05
    
    if patient_record.oxygen_saturation:
        if patient_record.oxygen_saturation < 95:
            vital_signs_analysis.append("Low oxygen saturation - may indicate respiratory or cardiac issue")
            diagnosis_result['confidence'] += 0.10
    
    if patient_record.respiratory_rate:
        if patient_record.respiratory_rate > 20:
            vital_signs_analysis.append("Tachypnea detected - may indicate respiratory distress")
            diagnosis_result['confidence'] += 0.05
        elif patient_record.respiratory_rate < 12:
            vital_signs_analysis.append("Bradypnea detected - may indicate respiratory depression")
            diagnosis_result['confidence'] += 0.05
    
    # Enhanced AI analysis of uploaded files
    ai_analysis_results = []
    
    # Add vital signs analysis to AI results
    if vital_signs_analysis:
        ai_analysis_results.append("Vital Signs Analysis:")
        ai_analysis_results.extend([f"• {finding}" for finding in vital_signs_analysis])
    
    # Analyze ECG report if uploaded
    if patient_record.ecg_report:
        try:
            ecg_analysis = ai_analyzer.analyze_ecg_image(patient_record.ecg_report.path)
            if ecg_analysis:
                ai_analysis_results.append(f"ECG Analysis: Heart Rate - {ecg_analysis.get('heart_rate', 'Unknown')}, "
                                        f"Rhythm - {ecg_analysis.get('rhythm', 'Unknown')}")
                if ecg_analysis.get('abnormalities'):
                    ai_analysis_results.append(f"ECG Abnormalities: {', '.join(ecg_analysis['abnormalities'])}")
                diagnosis_result['confidence'] += 0.10
        except Exception as e:
            ai_analysis_results.append("ECG analysis failed")
    
    # Analyze X-ray report if uploaded
    if patient_record.xray_report:
        try:
            xray_analysis = ai_analyzer.analyze_xray_image(patient_record.xray_report.path)
            if xray_analysis:
                ai_analysis_results.append(f"X-ray Analysis: {', '.join(xray_analysis.get('findings', []))}")
                if xray_analysis.get('abnormalities'):
                    ai_analysis_results.append(f"X-ray Abnormalities: {', '.join(xray_analysis['abnormalities'])}")
                diagnosis_result['confidence'] += 0.05
        except Exception as e:
            ai_analysis_results.append("X-ray analysis failed")
    
    # Analyze lab report if uploaded
    if patient_record.lab_report:
        try:
            report_analysis = ai_analyzer.analyze_medical_report(patient_record.lab_report.path)
            if report_analysis:
                if report_analysis.get('key_findings'):
                    ai_analysis_results.append(f"Lab Report Findings: {', '.join(report_analysis['key_findings'])}")
                if report_analysis.get('abnormal_values'):
                    ai_analysis_results.append(f"Lab Abnormalities: {', '.join(report_analysis['abnormal_values'])}")
                diagnosis_result['confidence'] += 0.05
        except Exception as e:
            ai_analysis_results.append("Lab report analysis failed")
    
    # Combine AI analysis results
    if ai_analysis_results:
        diagnosis_result['ai_analysis'] = '\n'.join(ai_analysis_results)
    
    # Ensure confidence doesn't exceed 1.0
    diagnosis_result['confidence'] = min(diagnosis_result['confidence'], 1.0)
    
    return diagnosis_result

@login_required
def health_advice(request):
    """Get free health advice based on symptoms and demographics."""
    advice = {}
    
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '')
        age = request.POST.get('age')
        gender = request.POST.get('gender', '')
        
        try:
            age = int(age) if age else None
        except:
            age = None
        
        # Get free health advice
        advice = ai_analyzer.get_free_health_advice(symptoms, age, gender)
        
        context = {
            'advice': advice,
            'symptoms': symptoms,
            'age': age,
            'gender': gender,
        }
        return render(request, 'core/health_advice.html', context)
    
    return render(request, 'core/health_advice.html', {'advice': advice})
