# Free APIs for Medical Diagnosis and Recommendations

This document explains the free APIs integration in DiagnoRx for providing medical diagnosis and recommendations without requiring paid API keys.

## Overview

The system now includes free medical APIs and knowledge bases that provide:

- Symptom analysis and condition matching
- Vital signs interpretation
- Medication recommendations
- Health advice based on demographics
- Lifestyle recommendations

## Features

### 1. Free Diagnosis API

- **Location**: `core/ai_analysis.py` - `get_free_diagnosis()` method
- **Functionality**: Analyzes symptoms and vital signs to suggest possible conditions
- **Input**: Symptoms (text) and vital signs (temperature, blood pressure, pulse)
- **Output**: Possible conditions, severity assessment, and recommendations

### 2. Symptom Analysis

- **Method**: `_analyze_symptoms_free()`
- **Features**:
  - Maps common symptoms to possible conditions
  - Determines symptom severity (mild/moderate/severe)
  - Provides immediate recommendations based on severity

### 3. Vital Signs Analysis

- **Method**: `_analyze_vitals_free()`
- **Analyzes**:
  - Temperature (normal: 95-100.4°F)
  - Blood pressure (normal: 90-140/60-90 mmHg)
  - Pulse rate (normal: 60-100 bpm)
- **Output**: Status assessment and recommendations

### 4. Medication Recommendations

- **Method**: `_get_medication_recommendations_free()`
- **Features**:
  - Condition-based medication suggestions
  - Dosage and frequency information
  - Duration recommendations
  - Common over-the-counter medications

### 5. Health Advice System

- **Method**: `get_free_health_advice()`
- **Features**:
  - Age-specific recommendations
  - Gender-specific advice
  - Symptom-based guidance
  - Lifestyle recommendations
  - Prevention tips
  - Emergency warning signs

## Usage

### 1. Dashboard Integration

The free diagnosis API is automatically integrated into the patient record creation process:

- When a patient record is created, symptoms and vital signs are analyzed
- Possible conditions are identified
- Medication recommendations are generated
- Confidence scores are calculated

### 2. Health Advice Feature

Access the health advice feature via:

- Navigation menu: "Health Advice"
- URL: `/health-advice/`

**Input Fields**:

- Symptoms (text description)
- Age (number)
- Gender (dropdown)

**Output**:

- General health advice
- Lifestyle recommendations
- Prevention tips
- When to seek medical help

## Knowledge Base

### Symptom-Condition Mappings

The system includes mappings for common symptoms:

- Fever → Common cold, Flu, COVID-19, Bacterial infection
- Cough → Upper respiratory infection, Bronchitis, Pneumonia, Allergies
- Headache → Tension headache, Migraine, Sinusitis, Dehydration
- Chest pain → Angina, Heart attack, Costochondritis, Anxiety
- Shortness of breath → Asthma, COPD, Anxiety, Pneumonia

### Medication Database

Common medications for various conditions:

- **Pain/Fever**: Acetaminophen, Ibuprofen
- **Cough**: Honey, Cough suppressants
- **Headache**: Pain relievers, Triptans
- **Gastrointestinal**: Antacids, Anti-nausea medications

### Vital Signs Ranges

- **Temperature**: Normal 95-100.4°F
- **Blood Pressure**: Normal 90-140/60-90 mmHg
- **Pulse**: Normal 60-100 bpm

## API Endpoints

### Free APIs Used

1. **FDA Drug Label API** (for medication information)
2. **Medical Knowledge Base** (built-in symptom-condition mappings)
3. **Vital Signs Analysis** (built-in ranges and interpretations)

## Integration Points

### Views

- `core/views.py` - `perform_ai_diagnosis()` method
- `core/views.py` - `health_advice()` view

### Templates

- `core/templates/core/health_advice.html` - Health advice interface
- `core/templates/core/prescription.html` - Displays diagnosis results

### URLs

- `/health-advice/` - Health advice feature

## Benefits

1. **No API Costs**: All features work without paid API keys
2. **Reliable**: Built-in knowledge base ensures consistent results
3. **Comprehensive**: Covers symptoms, vitals, medications, and advice
4. **User-Friendly**: Simple interface for getting health advice
5. **Educational**: Provides prevention tips and lifestyle recommendations

## Limitations

1. **Not Medical Advice**: Results are for informational purposes only
2. **Limited Conditions**: Covers common conditions but not all medical issues
3. **No Real-time Updates**: Knowledge base is static (can be updated manually)
4. **No Personalization**: Generic recommendations based on basic demographics

## Future Enhancements

1. **Expand Knowledge Base**: Add more symptoms and conditions
2. **Drug Interactions**: Include drug interaction checking
3. **Localization**: Support for multiple languages
4. **Machine Learning**: Train models on medical data for better accuracy
5. **Integration**: Connect with more free medical APIs

## Disclaimer

This system provides health information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## Testing

To test the free APIs:

1. **Dashboard**: Create a patient record with symptoms and vitals
2. **Health Advice**: Visit `/health-advice/` and enter symptoms
3. **Prescription**: View diagnosis results in the prescription page

The system will provide diagnosis, recommendations, and health advice using the free APIs without requiring any external API keys.
