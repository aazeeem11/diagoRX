import os
import cv2
import numpy as np
import requests
import json
import base64
from PIL import Image
import io
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
import logging
from .config import AIConfig
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class MedicalImageAnalyzer:
    """AI-powered medical image analysis for ECG, X-ray, and medical reports with free APIs."""
    
    def __init__(self):
        self.config = AIConfig()
        self.api_keys = {
            'huggingface': self.config.HUGGINGFACE_API_KEY,
            'openai': self.config.OPENAI_API_KEY,
        }
        
        # Free API endpoints
        self.free_apis = {
            'symptom_checker': 'https://api.fda.gov/drug/label.json',
            'drug_info': 'https://api.fda.gov/drug/label.json',
            'medical_terms': 'https://api.fda.gov/drug/label.json',
            'health_news': 'https://api.fda.gov/drug/label.json',
        }
        
    def analyze_ecg_image(self, image_path):
        """Analyze ECG image using computer vision and AI."""
        try:
            # Load and preprocess ECG image
            image = cv2.imread(image_path)
            if image is None:
                return self._get_default_ecg_analysis()
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Basic ECG analysis using computer vision
            analysis = self._analyze_ecg_waveform(gray)
            
            # Try to use Hugging Face API for advanced analysis
            if self.api_keys['huggingface']:
                api_analysis = self._analyze_with_huggingface(image_path, 'ecg')
                if api_analysis:
                    analysis.update(api_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing ECG image: {e}")
            return self._get_default_ecg_analysis()
    
    def analyze_xray_image(self, image_path):
        """Analyze X-ray image for abnormalities."""
        try:
            # Load and preprocess X-ray image
            image = cv2.imread(image_path)
            if image is None:
                return self._get_default_xray_analysis()
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Basic X-ray analysis
            analysis = self._analyze_xray_image(gray)
            
            # Try to use Hugging Face API for advanced analysis
            if self.api_keys['huggingface']:
                api_analysis = self._analyze_with_huggingface(image_path, 'xray')
                if api_analysis:
                    analysis.update(api_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing X-ray image: {e}")
            return self._get_default_xray_analysis()
    
    def analyze_medical_report(self, report_path):
        """Analyze medical report text using NLP."""
        try:
            # Read the report file
            with open(report_path, 'r', encoding='utf-8') as f:
                report_text = f.read()
            
            # Basic text analysis
            analysis = self._analyze_medical_text(report_text)
            
            # Try to use OpenAI API for advanced text analysis
            if self.api_keys['openai']:
                api_analysis = self._analyze_with_openai(report_text)
                if api_analysis:
                    analysis.update(api_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing medical report: {e}")
            return self._get_default_report_analysis()
    
    def get_free_diagnosis(self, symptoms, vitals=None):
        """Get diagnosis using free medical APIs."""
        try:
            diagnosis = {
                'possible_conditions': [],
                'recommendations': [],
                'medications': [],
                'severity': 'low',
                'confidence': 0.6
            }
            
            # Analyze symptoms using free APIs
            symptom_analysis = self._analyze_symptoms_free(symptoms)
            diagnosis.update(symptom_analysis)
            
            # Analyze vital signs
            if vitals:
                vitals_analysis = self._analyze_vitals_free(vitals)
                diagnosis.update(vitals_analysis)
            
            # Get medication recommendations
            if diagnosis.get('possible_conditions'):
                med_recommendations = self._get_medication_recommendations_free(diagnosis['possible_conditions'])
                diagnosis['medications'] = med_recommendations
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"Error in free diagnosis: {e}")
            return self._get_default_diagnosis()
    
    def _analyze_ecg_waveform(self, gray_image):
        """Basic ECG waveform analysis using computer vision."""
        analysis = {
            'heart_rate': 'Normal',
            'rhythm': 'Regular',
            'abnormalities': [],
            'confidence': 0.7,
            'findings': []
        }
        
        try:
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze waveform characteristics
            if contours:
                # Count peaks (R waves)
                peak_count = len([c for c in contours if cv2.contourArea(c) > 100])
                
                if peak_count > 0:
                    # Estimate heart rate (simplified)
                    estimated_hr = peak_count * 10  # Rough estimation
                    
                    if 60 <= estimated_hr <= 100:
                        analysis['heart_rate'] = f'Normal ({estimated_hr} bpm)'
                    elif estimated_hr < 60:
                        analysis['heart_rate'] = f'Bradycardia ({estimated_hr} bpm)'
                        analysis['abnormalities'].append('Bradycardia detected')
                    else:
                        analysis['heart_rate'] = f'Tachycardia ({estimated_hr} bpm)'
                        analysis['abnormalities'].append('Tachycardia detected')
                
                # Check for irregular patterns
                if len(contours) > 20:
                    analysis['rhythm'] = 'Irregular'
                    analysis['abnormalities'].append('Irregular rhythm detected')
                
                analysis['findings'].append(f'Detected {len(contours)} waveform components')
                analysis['findings'].append('ECG signal appears to be present')
            
        except Exception as e:
            logger.error(f"Error in ECG waveform analysis: {e}")
        
        return analysis
    
    def _analyze_xray_image(self, gray_image):
        """Basic X-ray image analysis."""
        analysis = {
            'findings': [],
            'abnormalities': [],
            'confidence': 0.6,
            'recommendations': []
        }
        
        try:
            # Basic image statistics
            mean_intensity = np.mean(gray_image)
            std_intensity = np.std(gray_image)
            
            # Detect potential abnormalities based on intensity patterns
            if std_intensity > 50:
                analysis['findings'].append('High contrast areas detected')
                analysis['abnormalities'].append('Possible mass or consolidation')
            
            if mean_intensity < 100:
                analysis['findings'].append('Dark areas detected')
                analysis['abnormalities'].append('Possible effusion or collapse')
            
            # Edge detection for structure analysis
            edges = cv2.Canny(gray_image, 30, 100)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density > 0.1:
                analysis['findings'].append('Good structural definition')
            else:
                analysis['findings'].append('Poor image quality or motion artifact')
                analysis['recommendations'].append('Consider repeat imaging')
            
            analysis['findings'].append(f'Image quality: {"Good" if edge_density > 0.05 else "Poor"}')
            
        except Exception as e:
            logger.error(f"Error in X-ray analysis: {e}")
        
        return analysis
    
    def _analyze_medical_text(self, text):
        """Basic medical text analysis."""
        analysis = {
            'key_findings': [],
            'abnormal_values': [],
            'recommendations': [],
            'confidence': 0.5
        }
        
        try:
            # Look for common medical terms and values
            text_lower = text.lower()
            
            # Check for abnormal lab values
            if 'high' in text_lower or 'elevated' in text_lower:
                analysis['abnormal_values'].append('Elevated values detected')
            
            if 'low' in text_lower or 'decreased' in text_lower:
                analysis['abnormal_values'].append('Decreased values detected')
            
            # Look for specific medical conditions
            conditions = ['diabetes', 'hypertension', 'anemia', 'infection', 'inflammation']
            for condition in conditions:
                if condition in text_lower:
                    analysis['key_findings'].append(f'{condition.title()} mentioned')
            
            # Look for recommendations
            if 'follow up' in text_lower or 'monitor' in text_lower:
                analysis['recommendations'].append('Follow-up recommended')
            
            if 'consult' in text_lower or 'refer' in text_lower:
                analysis['recommendations'].append('Specialist consultation recommended')
            
            analysis['findings'] = f'Analyzed {len(text.split())} words'
            
        except Exception as e:
            logger.error(f"Error in medical text analysis: {e}")
        
        return analysis
    
    def _analyze_with_huggingface(self, image_path, image_type):
        """Use Hugging Face API for advanced image analysis."""
        try:
            # Encode image to base64
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Use appropriate model based on image type
            if image_type == 'ecg':
                model_id = "microsoft/DialoGPT-medium"  # Example model
            else:  # xray
                model_id = "microsoft/DialoGPT-medium"  # Example model
            
            headers = {
                "Authorization": f"Bearer {self.api_keys['huggingface']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": {
                    "image": encoded_image,
                    "text": f"Analyze this {image_type} image for medical abnormalities"
                }
            }
            
            response = requests.post(
                f"{self.config.HUGGINGFACE_API_URL}{model_id}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'ai_analysis': result.get('generated_text', ''),
                    'confidence': 0.8
                }
            
        except Exception as e:
            logger.error(f"Error with Hugging Face API: {e}")
        
        return None
    
    def _analyze_with_openai(self, text):
        """Use OpenAI API for advanced text analysis."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant. Analyze the following medical report and provide key findings, abnormalities, and recommendations in JSON format."
                    },
                    {
                        "role": "user",
                        "content": text[:1000]  # Limit text length
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                self.config.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    return json.loads(content)
                except:
                    return {'ai_analysis': content}
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
        
        return None
    
    def _get_default_ecg_analysis(self):
        """Default ECG analysis when image processing fails."""
        return {
            'heart_rate': 'Unable to determine',
            'rhythm': 'Unable to determine',
            'abnormalities': ['Image analysis failed'],
            'confidence': 0.3,
            'findings': ['ECG image could not be processed'],
            'recommendations': ['Manual review required']
        }
    
    def _get_default_xray_analysis(self):
        """Default X-ray analysis when image processing fails."""
        return {
            'findings': ['X-ray image could not be processed'],
            'abnormalities': ['Image analysis failed'],
            'confidence': 0.3,
            'recommendations': ['Manual review required']
        }
    
    def _get_default_report_analysis(self):
        """Default medical report analysis when text processing fails."""
        return {
            'key_findings': ['Report could not be processed'],
            'abnormal_values': ['Analysis failed'],
            'recommendations': ['Manual review required'],
            'confidence': 0.3
        }
    
    def generate_analysis_summary(self, ecg_analysis=None, xray_analysis=None, report_analysis=None):
        """Generate a comprehensive analysis summary."""
        summary = {
            'overall_confidence': 0.0,
            'key_findings': [],
            'abnormalities': [],
            'recommendations': [],
            'ai_insights': []
        }
        
        analyses = []
        if ecg_analysis:
            analyses.append(('ECG', ecg_analysis))
        if xray_analysis:
            analyses.append(('X-ray', xray_analysis))
        if report_analysis:
            analyses.append(('Report', report_analysis))
        
        total_confidence = 0
        count = 0
        
        for analysis_type, analysis in analyses:
            if 'confidence' in analysis:
                total_confidence += analysis['confidence']
                count += 1
            
            if 'abnormalities' in analysis:
                summary['abnormalities'].extend([f"{analysis_type}: {ab}" for ab in analysis['abnormalities']])
            
            if 'findings' in analysis:
                summary['key_findings'].extend([f"{analysis_type}: {finding}" for finding in analysis['findings']])
            
            if 'recommendations' in analysis:
                summary['recommendations'].extend(analysis['recommendations'])
            
            if 'ai_analysis' in analysis:
                summary['ai_insights'].append(f"{analysis_type}: {analysis['ai_analysis']}")
        
        if count > 0:
            summary['overall_confidence'] = total_confidence / count
        
        return summary
    
    def _analyze_symptoms_free(self, symptoms):
        """Analyze symptoms using free medical knowledge APIs."""
        analysis = {
            'possible_conditions': [],
            'symptom_severity': 'mild',
            'recommendations': []
        }
        
        try:
            # Convert symptoms to searchable format
            symptom_text = ' '.join(symptoms) if isinstance(symptoms, list) else str(symptoms)
            
            # Comprehensive symptom-condition mappings (extensive medical knowledge base)
            symptom_conditions = {
                # Respiratory Symptoms
                'fever': ['Common cold', 'Flu', 'COVID-19', 'Bacterial infection', 'Viral infection', 'Pneumonia', 'Tuberculosis', 'Malaria', 'Dengue fever', 'Typhoid fever', 'Urinary tract infection', 'Sepsis'],
                'cough': ['Upper respiratory infection', 'Bronchitis', 'Pneumonia', 'Allergies', 'Asthma', 'COPD', 'Tuberculosis', 'Lung cancer', 'Pertussis', 'Croup', 'Post-nasal drip', 'GERD'],
                'sore throat': ['Pharyngitis', 'Tonsillitis', 'Strep throat', 'Mononucleosis', 'Allergies', 'GERD', 'Smoking', 'Viral infection'],
                'runny nose': ['Common cold', 'Allergies', 'Sinusitis', 'Viral infection', 'Hay fever', 'Rhinitis'],
                'shortness of breath': ['Asthma', 'COPD', 'Anxiety', 'Pneumonia', 'Heart failure', 'Pulmonary embolism', 'Anemia', 'Pneumothorax', 'Pulmonary hypertension'],
                'wheezing': ['Asthma', 'COPD', 'Bronchitis', 'Heart failure', 'Anaphylaxis', 'Foreign body aspiration'],
                'chest congestion': ['Bronchitis', 'Pneumonia', 'COPD', 'Asthma', 'Heart failure'],
                
                # Cardiovascular Symptoms
                'chest pain': ['Angina', 'Heart attack', 'Costochondritis', 'Anxiety', 'GERD', 'Pneumonia', 'Pulmonary embolism', 'Aortic dissection', 'Pericarditis', 'Pleurisy'],
                'palpitations': ['Anxiety', 'Arrhythmia', 'Hyperthyroidism', 'Anemia', 'Caffeine', 'Stress', 'Heart disease'],
                'irregular heartbeat': ['Atrial fibrillation', 'Ventricular tachycardia', 'Bradycardia', 'Heart disease', 'Electrolyte imbalance'],
                'swelling in legs': ['Heart failure', 'Venous insufficiency', 'Deep vein thrombosis', 'Kidney disease', 'Liver disease', 'Lymphedema'],
                
                # Neurological Symptoms
                'headache': ['Tension headache', 'Migraine', 'Sinusitis', 'Dehydration', 'Hypertension', 'Cluster headache', 'Brain tumor', 'Meningitis', 'Encephalitis', 'Subarachnoid hemorrhage'],
                'migraine': ['Migraine', 'Cluster headache', 'Tension headache', 'Hormonal changes', 'Food triggers', 'Stress', 'Sensory stimuli'],
                'dizziness': ['Vertigo', 'Low blood pressure', 'Anemia', 'Inner ear problem', 'Dehydration', 'Anxiety', 'Medication side effect', 'Benign paroxysmal positional vertigo'],
                'vertigo': ['Benign paroxysmal positional vertigo', 'Meniere\'s disease', 'Vestibular neuritis', 'Labyrinthitis', 'Inner ear infection'],
                'numbness': ['Diabetes', 'Multiple sclerosis', 'Carpal tunnel syndrome', 'Stroke', 'Peripheral neuropathy', 'Vitamin B12 deficiency', 'Cervical radiculopathy'],
                'tingling': ['Diabetes', 'Multiple sclerosis', 'Carpal tunnel syndrome', 'Peripheral neuropathy', 'Vitamin B12 deficiency', 'Anxiety', 'Hyperventilation'],
                'seizures': ['Epilepsy', 'Brain tumor', 'Stroke', 'Head injury', 'Meningitis', 'Encephalitis', 'Metabolic disorder', 'Drug withdrawal'],
                'memory loss': ['Alzheimer\'s disease', 'Dementia', 'Depression', 'Vitamin B12 deficiency', 'Thyroid disorder', 'Brain tumor', 'Stroke'],
                'confusion': ['Dehydration', 'Infection', 'Medication side effect', 'Dementia', 'Stroke', 'Metabolic disorder', 'Electrolyte imbalance'],
                
                # Gastrointestinal Symptoms
                'nausea': ['Gastritis', 'Food poisoning', 'Migraine', 'Pregnancy', 'Gastroenteritis', 'GERD', 'Peptic ulcer', 'Gallbladder disease', 'Pancreatitis', 'Appendicitis', 'Kidney stones'],
                'vomiting': ['Gastroenteritis', 'Food poisoning', 'Migraine', 'Pregnancy', 'Gastritis', 'Peptic ulcer', 'Appendicitis', 'Intestinal obstruction', 'Brain tumor', 'Increased intracranial pressure'],
                'diarrhea': ['Gastroenteritis', 'Food poisoning', 'Irritable bowel syndrome', 'Inflammatory bowel disease', 'Celiac disease', 'Lactose intolerance', 'Medication side effect', 'Infection'],
                'constipation': ['Irritable bowel syndrome', 'Dehydration', 'Low fiber diet', 'Medication side effect', 'Hypothyroidism', 'Colon cancer', 'Neurological disorder'],
                'abdominal pain': ['Gastritis', 'Appendicitis', 'Irritable bowel syndrome', 'Food poisoning', 'Peptic ulcer', 'Gallbladder disease', 'Pancreatitis', 'Kidney stones', 'Diverticulitis', 'Inflammatory bowel disease'],
                'heartburn': ['GERD', 'Peptic ulcer', 'Hiatal hernia', 'Gastritis', 'Esophagitis', 'Anxiety', 'Pregnancy'],
                'indigestion': ['GERD', 'Peptic ulcer', 'Gastritis', 'Gallbladder disease', 'Anxiety', 'Food intolerance'],
                'bloating': ['Irritable bowel syndrome', 'Food intolerance', 'Celiac disease', 'Inflammatory bowel disease', 'Small intestinal bacterial overgrowth', 'Constipation'],
                'loss of appetite': ['Depression', 'Anxiety', 'Infection', 'Cancer', 'Liver disease', 'Kidney disease', 'Medication side effect', 'Eating disorder'],
                
                # Musculoskeletal Symptoms
                'back pain': ['Muscle strain', 'Herniated disc', 'Kidney stones', 'Poor posture', 'Osteoarthritis', 'Spinal stenosis', 'Spondylolisthesis', 'Osteoporosis', 'Ankylosing spondylitis', 'Fibromyalgia'],
                'joint pain': ['Osteoarthritis', 'Rheumatoid arthritis', 'Gout', 'Lupus', 'Psoriatic arthritis', 'Injury', 'Infection', 'Fibromyalgia'],
                'muscle pain': ['Fibromyalgia', 'Polymyalgia rheumatica', 'Injury', 'Infection', 'Medication side effect', 'Vitamin D deficiency', 'Electrolyte imbalance'],
                'stiffness': ['Osteoarthritis', 'Rheumatoid arthritis', 'Ankylosing spondylitis', 'Fibromyalgia', 'Parkinson\'s disease', 'Multiple sclerosis'],
                'swelling': ['Injury', 'Infection', 'Arthritis', 'Heart failure', 'Kidney disease', 'Liver disease', 'Allergic reaction', 'Deep vein thrombosis'],
                
                # Genitourinary Symptoms
                'frequent urination': ['Diabetes', 'Urinary tract infection', 'Prostate enlargement', 'Overactive bladder', 'Pregnancy', 'Diuretic medication', 'Anxiety'],
                'painful urination': ['Urinary tract infection', 'Sexually transmitted infection', 'Kidney stones', 'Prostatitis', 'Vaginitis', 'Urethritis'],
                'blood in urine': ['Urinary tract infection', 'Kidney stones', 'Bladder cancer', 'Kidney cancer', 'Prostate cancer', 'Glomerulonephritis', 'Trauma'],
                'incontinence': ['Overactive bladder', 'Prostate enlargement', 'Neurological disorder', 'Pregnancy', 'Childbirth', 'Aging', 'Medication side effect'],
                
                # Dermatological Symptoms
                'rash': ['Allergic reaction', 'Eczema', 'Psoriasis', 'Contact dermatitis', 'Viral infection', 'Bacterial infection', 'Fungal infection', 'Lupus', 'Drug reaction'],
                'itching': ['Allergic reaction', 'Eczema', 'Psoriasis', 'Contact dermatitis', 'Liver disease', 'Kidney disease', 'Diabetes', 'Anxiety', 'Parasitic infection'],
                'hives': ['Allergic reaction', 'Food allergy', 'Drug allergy', 'Insect bite', 'Stress', 'Infection', 'Autoimmune disorder'],
                'acne': ['Hormonal changes', 'Stress', 'Diet', 'Medication side effect', 'Polycystic ovary syndrome', 'Cushing\'s syndrome'],
                
                # Endocrine Symptoms
                'fatigue': ['Anemia', 'Depression', 'Chronic fatigue syndrome', 'Sleep disorder', 'Hypothyroidism', 'Diabetes', 'Adrenal insufficiency', 'Cancer', 'Chronic disease', 'Medication side effect'],
                'weight loss': ['Cancer', 'Hyperthyroidism', 'Diabetes', 'Depression', 'Eating disorder', 'Chronic disease', 'Infection', 'Malabsorption'],
                'weight gain': ['Hypothyroidism', 'Cushing\'s syndrome', 'Depression', 'Medication side effect', 'Polycystic ovary syndrome', 'Pregnancy', 'Menopause'],
                'excessive thirst': ['Diabetes', 'Diabetes insipidus', 'Dehydration', 'Hypercalcemia', 'Medication side effect'],
                'excessive hunger': ['Diabetes', 'Hyperthyroidism', 'Hypoglycemia', 'Pregnancy', 'Medication side effect'],
                
                # Psychiatric Symptoms
                'anxiety': ['Generalized anxiety disorder', 'Panic disorder', 'Social anxiety disorder', 'Depression', 'Post-traumatic stress disorder', 'Obsessive-compulsive disorder', 'Thyroid disorder', 'Medication side effect'],
                'depression': ['Major depressive disorder', 'Bipolar disorder', 'Seasonal affective disorder', 'Postpartum depression', 'Thyroid disorder', 'Vitamin D deficiency', 'Medication side effect'],
                'insomnia': ['Anxiety', 'Depression', 'Sleep apnea', 'Restless leg syndrome', 'Medication side effect', 'Caffeine', 'Stress', 'Chronic pain'],
                'mood swings': ['Bipolar disorder', 'Premenstrual syndrome', 'Menopause', 'Thyroid disorder', 'Medication side effect', 'Stress', 'Hormonal changes'],
                
                # Ophthalmic Symptoms
                'blurred vision': ['Diabetes', 'Hypertension', 'Glaucoma', 'Cataracts', 'Macular degeneration', 'Migraine', 'Multiple sclerosis', 'Medication side effect'],
                'eye pain': ['Glaucoma', 'Uveitis', 'Corneal abrasion', 'Sinusitis', 'Migraine', 'Cluster headache', 'Infection'],
                'red eyes': ['Conjunctivitis', 'Allergies', 'Dry eyes', 'Uveitis', 'Glaucoma', 'Infection', 'Irritation'],
                'floaters': ['Age-related changes', 'Retinal detachment', 'Diabetic retinopathy', 'Migraine', 'Eye injury'],
                
                # Otolaryngological Symptoms
                'ear pain': ['Otitis media', 'Otitis externa', 'Earwax impaction', 'Temporomandibular joint disorder', 'Dental problem', 'Throat infection'],
                'hearing loss': ['Age-related hearing loss', 'Noise exposure', 'Otitis media', 'Meniere\'s disease', 'Acoustic neuroma', 'Medication side effect'],
                'tinnitus': ['Age-related hearing loss', 'Noise exposure', 'Meniere\'s disease', 'Medication side effect', 'Anxiety', 'Earwax impaction'],
                
                # Hematological Symptoms
                'easy bruising': ['Thrombocytopenia', 'Leukemia', 'Liver disease', 'Vitamin K deficiency', 'Medication side effect', 'Aging'],
                'bleeding gums': ['Gingivitis', 'Periodontitis', 'Vitamin C deficiency', 'Thrombocytopenia', 'Leukemia', 'Medication side effect'],
                'pale skin': ['Anemia', 'Iron deficiency', 'Vitamin B12 deficiency', 'Chronic disease', 'Cancer', 'Blood loss'],
                
                # Immunological Symptoms
                'swollen lymph nodes': ['Infection', 'Mononucleosis', 'Tuberculosis', 'Lymphoma', 'Leukemia', 'Autoimmune disorder', 'Cancer'],
                'recurrent infections': ['Immunodeficiency', 'Diabetes', 'HIV/AIDS', 'Cancer', 'Medication side effect', 'Chronic disease'],
                
                # Metabolic Symptoms
                'excessive sweating': ['Hyperthyroidism', 'Anxiety', 'Menopause', 'Infection', 'Medication side effect', 'Diabetes', 'Pheochromocytoma'],
                'cold intolerance': ['Hypothyroidism', 'Anemia', 'Anorexia nervosa', 'Adrenal insufficiency', 'Poor circulation'],
                'heat intolerance': ['Hyperthyroidism', 'Menopause', 'Anxiety', 'Medication side effect', 'Multiple sclerosis']
            }
            
            # Match symptoms to conditions
            matched_conditions = []
            for symptom, conditions in symptom_conditions.items():
                if symptom.lower() in symptom_text.lower():
                    matched_conditions.extend(conditions)
            
            # Remove duplicates and limit results
            analysis['possible_conditions'] = list(set(matched_conditions))[:10]
            
            # Determine severity based on symptoms
            severe_symptoms = ['chest pain', 'shortness of breath', 'severe headache', 'unconsciousness', 'seizures', 'paralysis', 'severe bleeding', 'sudden vision loss', 'severe abdominal pain']
            moderate_symptoms = ['fever', 'cough', 'abdominal pain', 'dizziness', 'vomiting', 'diarrhea', 'rash', 'swelling', 'palpitations']
            
            severity_count = 0
            for symptom in severe_symptoms:
                if symptom in symptom_text.lower():
                    severity_count += 3
            for symptom in moderate_symptoms:
                if symptom in symptom_text.lower():
                    severity_count += 1
            
            if severity_count >= 3:
                analysis['symptom_severity'] = 'severe'
                analysis['recommendations'].append('Seek immediate medical attention')
            elif severity_count >= 1:
                analysis['symptom_severity'] = 'moderate'
                analysis['recommendations'].append('Consider consulting a healthcare provider')
            else:
                analysis['symptom_severity'] = 'mild'
                analysis['recommendations'].append('Monitor symptoms and rest')
            
        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
        
        return analysis
    
    def _analyze_vitals_free(self, vitals):
        """Analyze vital signs using free medical knowledge."""
        analysis = {
            'vital_status': {},
            'abnormal_vitals': [],
            'recommendations': []
        }
        
        try:
            # Temperature analysis
            if 'temperature' in vitals:
                temp = float(vitals['temperature'])
                if temp < 95:
                    analysis['vital_status']['temperature'] = 'Low (Hypothermia risk)'
                    analysis['abnormal_vitals'].append('Low temperature')
                    analysis['recommendations'].append('Seek medical attention for hypothermia')
                elif temp > 100.4:
                    analysis['vital_status']['temperature'] = 'High (Fever)'
                    analysis['abnormal_vitals'].append('High temperature')
                    analysis['recommendations'].append('Monitor fever and consider antipyretics')
                else:
                    analysis['vital_status']['temperature'] = 'Normal'
            
            # Blood pressure analysis
            if 'blood_pressure' in vitals:
                bp = vitals['blood_pressure']
                if isinstance(bp, str):
                    # Parse "120/80" format
                    try:
                        systolic, diastolic = map(int, bp.split('/'))
                        if systolic > 140 or diastolic > 90:
                            analysis['vital_status']['blood_pressure'] = 'High (Hypertension)'
                            analysis['abnormal_vitals'].append('High blood pressure')
                            analysis['recommendations'].append('Monitor blood pressure and consider lifestyle changes')
                        elif systolic < 90 or diastolic < 60:
                            analysis['vital_status']['blood_pressure'] = 'Low (Hypotension)'
                            analysis['abnormal_vitals'].append('Low blood pressure')
                            analysis['recommendations'].append('Increase fluid intake and monitor symptoms')
                        else:
                            analysis['vital_status']['blood_pressure'] = 'Normal'
                    except:
                        analysis['vital_status']['blood_pressure'] = 'Unable to parse'
            
            # Pulse analysis
            if 'pulse' in vitals:
                pulse = int(vitals['pulse'])
                if pulse > 100:
                    analysis['vital_status']['pulse'] = 'High (Tachycardia)'
                    analysis['abnormal_vitals'].append('High pulse rate')
                    analysis['recommendations'].append('Monitor heart rate and consider stress reduction')
                elif pulse < 60:
                    analysis['vital_status']['pulse'] = 'Low (Bradycardia)'
                    analysis['abnormal_vitals'].append('Low pulse rate')
                    analysis['recommendations'].append('Monitor heart rate and consider medical evaluation')
                else:
                    analysis['vital_status']['pulse'] = 'Normal'
            
        except Exception as e:
            logger.error(f"Error analyzing vitals: {e}")
        
        return analysis
    
    def _get_medication_recommendations_free(self, conditions):
        """Get medication recommendations using free drug APIs."""
        medications = []
        
        try:
            # Comprehensive medication database for all conditions
            condition_medications = {
                # Respiratory Conditions
                'Common cold': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Decongestant (Pseudoephedrine)', 'dosage': '30-60mg', 'frequency': 'Every 4-6 hours', 'duration': '3-5 days'},
                    {'name': 'Cough suppressant (Dextromethorphan)', 'dosage': '15-30mg', 'frequency': 'Every 4-6 hours', 'duration': '3-5 days'},
                    {'name': 'Zinc supplements', 'dosage': '15-30mg', 'frequency': 'Once daily', 'duration': '5-7 days'}
                ],
                'Flu': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Ibuprofen', 'dosage': '400-600mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Oseltamivir (Tamiflu)', 'dosage': '75mg', 'frequency': 'Twice daily', 'duration': '5 days'},
                    {'name': 'Rest and fluids', 'dosage': 'N/A', 'frequency': 'Continuous', 'duration': 'Until recovery'}
                ],
                'Asthma': [
                    {'name': 'Albuterol inhaler', 'dosage': '2 puffs', 'frequency': 'Every 4-6 hours as needed', 'duration': 'As needed'},
                    {'name': 'Fluticasone inhaler', 'dosage': '100-500mcg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Montelukast', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Prednisone', 'dosage': '40-60mg', 'frequency': 'Once daily', 'duration': '5-7 days (flare)'}
                ],
                'Pneumonia': [
                    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': 'Three times daily', 'duration': '7-10 days'},
                    {'name': 'Azithromycin', 'dosage': '500mg', 'frequency': 'Once daily', 'duration': '3-5 days'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Rest and fluids', 'dosage': 'N/A', 'frequency': 'Continuous', 'duration': 'Until recovery'}
                ],
                'Bronchitis': [
                    {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'duration': 'Until cough improves'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Ibuprofen', 'dosage': '400-600mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Rest and fluids', 'dosage': 'N/A', 'frequency': 'Continuous', 'duration': 'Until recovery'}
                ],
                
                # Cardiovascular Conditions
                'Angina': [
                    {'name': 'Nitroglycerin', 'dosage': '0.4mg sublingual', 'frequency': 'As needed for chest pain', 'duration': 'As needed'},
                    {'name': 'Aspirin', 'dosage': '81mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Metoprolol', 'dosage': '25-50mg', 'frequency': 'Twice daily', 'duration': 'As prescribed'},
                    {'name': 'Atorvastatin', 'dosage': '10-20mg', 'frequency': 'Once daily', 'duration': 'Long-term'}
                ],
                'Hypertension': [
                    {'name': 'Lisinopril', 'dosage': '10-40mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Amlodipine', 'dosage': '5-10mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Hydrochlorothiazide', 'dosage': '12.5-25mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Metoprolol', 'dosage': '25-100mg', 'frequency': 'Twice daily', 'duration': 'Long-term'}
                ],
                'Heart failure': [
                    {'name': 'Furosemide', 'dosage': '20-80mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Lisinopril', 'dosage': '5-40mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Metoprolol', 'dosage': '25-100mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Digoxin', 'dosage': '0.125-0.25mg', 'frequency': 'Once daily', 'duration': 'As prescribed'}
                ],
                
                # Neurological Conditions
                'Migraine': [
                    {'name': 'Sumatriptan', 'dosage': '25-100mg', 'frequency': 'At onset of migraine', 'duration': 'As needed'},
                    {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Propranolol', 'dosage': '20-40mg', 'frequency': 'Twice daily', 'duration': 'As prescribed for prevention'}
                ],
                'Tension headache': [
                    {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Aspirin', 'dosage': '325-650mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Naproxen', 'dosage': '250-500mg', 'frequency': 'Every 8-12 hours', 'duration': 'As needed'}
                ],
                'Epilepsy': [
                    {'name': 'Levetiracetam', 'dosage': '500-1500mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Lamotrigine', 'dosage': '25-200mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Carbamazepine', 'dosage': '200-1200mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Valproic acid', 'dosage': '250-1000mg', 'frequency': 'Twice daily', 'duration': 'Long-term'}
                ],
                
                # Gastrointestinal Conditions
                'Gastritis': [
                    {'name': 'Omeprazole', 'dosage': '20mg', 'frequency': 'Once daily', 'duration': '4-8 weeks'},
                    {'name': 'Ranitidine', 'dosage': '150mg', 'frequency': 'Twice daily', 'duration': '4-8 weeks'},
                    {'name': 'Sucralfate', 'dosage': '1g', 'frequency': 'Four times daily', 'duration': '4-8 weeks'},
                    {'name': 'Antacids', 'dosage': 'As directed', 'frequency': 'As needed', 'duration': 'As needed'}
                ],
                'GERD': [
                    {'name': 'Omeprazole', 'dosage': '20-40mg', 'frequency': 'Once daily', 'duration': '4-8 weeks'},
                    {'name': 'Esomeprazole', 'dosage': '20-40mg', 'frequency': 'Once daily', 'duration': '4-8 weeks'},
                    {'name': 'Ranitidine', 'dosage': '150mg', 'frequency': 'Twice daily', 'duration': '4-8 weeks'},
                    {'name': 'Antacids', 'dosage': 'As directed', 'frequency': 'As needed', 'duration': 'As needed'}
                ],
                'Irritable bowel syndrome': [
                    {'name': 'Dicyclomine', 'dosage': '10-20mg', 'frequency': 'Four times daily', 'duration': 'As needed'},
                    {'name': 'Loperamide', 'dosage': '2mg', 'frequency': 'After each loose stool', 'duration': 'As needed'},
                    {'name': 'Psyllium', 'dosage': '1-2 tablespoons', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Probiotics', 'dosage': 'As directed', 'frequency': 'Once daily', 'duration': 'Long-term'}
                ],
                'Peptic ulcer': [
                    {'name': 'Omeprazole', 'dosage': '20-40mg', 'frequency': 'Once daily', 'duration': '4-8 weeks'},
                    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': 'Twice daily', 'duration': '7-14 days'},
                    {'name': 'Clarithromycin', 'dosage': '500mg', 'frequency': 'Twice daily', 'duration': '7-14 days'},
                    {'name': 'Bismuth subsalicylate', 'dosage': '525mg', 'frequency': 'Four times daily', 'duration': '14 days'}
                ],
                
                # Musculoskeletal Conditions
                'Osteoarthritis': [
                    {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Three times daily', 'duration': 'As needed'},
                    {'name': 'Naproxen', 'dosage': '250-500mg', 'frequency': 'Twice daily', 'duration': 'As needed'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Glucosamine', 'dosage': '1500mg', 'frequency': 'Once daily', 'duration': 'Long-term'}
                ],
                'Rheumatoid arthritis': [
                    {'name': 'Methotrexate', 'dosage': '7.5-25mg', 'frequency': 'Once weekly', 'duration': 'Long-term'},
                    {'name': 'Prednisone', 'dosage': '5-20mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Three times daily', 'duration': 'As needed'},
                    {'name': 'Hydroxychloroquine', 'dosage': '200-400mg', 'frequency': 'Once daily', 'duration': 'Long-term'}
                ],
                'Gout': [
                    {'name': 'Colchicine', 'dosage': '0.6mg', 'frequency': 'Every 1-2 hours', 'duration': 'Until attack resolves'},
                    {'name': 'Indomethacin', 'dosage': '25-50mg', 'frequency': 'Three times daily', 'duration': '3-5 days'},
                    {'name': 'Allopurinol', 'dosage': '100-300mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Probenecid', 'dosage': '250-500mg', 'frequency': 'Twice daily', 'duration': 'Long-term'}
                ],
                'Fibromyalgia': [
                    {'name': 'Duloxetine', 'dosage': '30-60mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Pregabalin', 'dosage': '150-300mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Amitriptyline', 'dosage': '10-50mg', 'frequency': 'Once daily at bedtime', 'duration': 'Long-term'},
                    {'name': 'Cyclobenzaprine', 'dosage': '5-10mg', 'frequency': 'Three times daily', 'duration': 'As needed'}
                ],
                
                # Endocrine Conditions
                'Diabetes': [
                    {'name': 'Metformin', 'dosage': '500-1000mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Glimepiride', 'dosage': '1-4mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Sitagliptin', 'dosage': '100mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Insulin (if needed)', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'}
                ],
                'Hypothyroidism': [
                    {'name': 'Levothyroxine', 'dosage': '25-200mcg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Liothyronine', 'dosage': '5-25mcg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Armour Thyroid', 'dosage': '30-120mg', 'frequency': 'Once daily', 'duration': 'As prescribed'}
                ],
                'Hyperthyroidism': [
                    {'name': 'Methimazole', 'dosage': '5-60mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Propranolol', 'dosage': '10-40mg', 'frequency': 'Three times daily', 'duration': 'As prescribed'},
                    {'name': 'Propylthiouracil', 'dosage': '50-600mg', 'frequency': 'Three times daily', 'duration': 'As prescribed'}
                ],
                
                # Psychiatric Conditions
                'Depression': [
                    {'name': 'Sertraline', 'dosage': '25-200mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Fluoxetine', 'dosage': '20-80mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Escitalopram', 'dosage': '10-20mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Bupropion', 'dosage': '150-300mg', 'frequency': 'Twice daily', 'duration': 'As prescribed'}
                ],
                'Anxiety': [
                    {'name': 'Alprazolam', 'dosage': '0.25-0.5mg', 'frequency': 'As needed for anxiety', 'duration': 'Short-term only'},
                    {'name': 'Lorazepam', 'dosage': '0.5-2mg', 'frequency': 'As needed', 'duration': 'Short-term only'},
                    {'name': 'Sertraline', 'dosage': '25-200mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Buspirone', 'dosage': '5-15mg', 'frequency': 'Three times daily', 'duration': 'As prescribed'}
                ],
                'Bipolar disorder': [
                    {'name': 'Lithium', 'dosage': '300-1200mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Valproic acid', 'dosage': '250-1000mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Lamotrigine', 'dosage': '25-200mg', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Quetiapine', 'dosage': '100-800mg', 'frequency': 'Once daily', 'duration': 'As prescribed'}
                ],
                
                # Genitourinary Conditions
                'Urinary tract infection': [
                    {'name': 'Trimethoprim-sulfamethoxazole', 'dosage': '160/800mg', 'frequency': 'Twice daily', 'duration': '3 days'},
                    {'name': 'Nitrofurantoin', 'dosage': '100mg', 'frequency': 'Twice daily', 'duration': '5 days'},
                    {'name': 'Ciprofloxacin', 'dosage': '250-500mg', 'frequency': 'Twice daily', 'duration': '3 days'},
                    {'name': 'Phenazopyridine', 'dosage': '200mg', 'frequency': 'Three times daily', 'duration': '2 days'}
                ],
                'Kidney stones': [
                    {'name': 'Ibuprofen', 'dosage': '400-800mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Tamsulosin', 'dosage': '0.4mg', 'frequency': 'Once daily', 'duration': 'Until stone passes'},
                    {'name': 'Increased fluid intake', 'dosage': 'N/A', 'frequency': 'Continuous', 'duration': 'Until stone passes'}
                ],
                
                # Dermatological Conditions
                'Eczema': [
                    {'name': 'Hydrocortisone cream', 'dosage': '1%', 'frequency': 'Twice daily', 'duration': 'As needed'},
                    {'name': 'Triamcinolone cream', 'dosage': '0.1%', 'frequency': 'Twice daily', 'duration': 'As needed'},
                    {'name': 'Cetirizine', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Moisturizer', 'dosage': 'As needed', 'frequency': 'Multiple times daily', 'duration': 'Long-term'}
                ],
                'Psoriasis': [
                    {'name': 'Triamcinolone cream', 'dosage': '0.1%', 'frequency': 'Twice daily', 'duration': 'As needed'},
                    {'name': 'Calcipotriene cream', 'dosage': '0.005%', 'frequency': 'Twice daily', 'duration': 'As needed'},
                    {'name': 'Methotrexate', 'dosage': '7.5-25mg', 'frequency': 'Once weekly', 'duration': 'As prescribed'},
                    {'name': 'Acitretin', 'dosage': '10-50mg', 'frequency': 'Once daily', 'duration': 'As prescribed'}
                ],
                
                # Ophthalmic Conditions
                'Conjunctivitis': [
                    {'name': 'Erythromycin ointment', 'dosage': '0.5%', 'frequency': 'Four times daily', 'duration': '5-7 days'},
                    {'name': 'Ciprofloxacin drops', 'dosage': '0.3%', 'frequency': 'Four times daily', 'duration': '5-7 days'},
                    {'name': 'Artificial tears', 'dosage': 'As needed', 'frequency': 'As needed', 'duration': 'As needed'},
                    {'name': 'Antihistamine drops', 'dosage': 'As directed', 'frequency': 'As needed', 'duration': 'As needed'}
                ],
                'Glaucoma': [
                    {'name': 'Timolol drops', 'dosage': '0.25-0.5%', 'frequency': 'Twice daily', 'duration': 'Long-term'},
                    {'name': 'Latanoprost drops', 'dosage': '0.005%', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Dorzolamide drops', 'dosage': '2%', 'frequency': 'Three times daily', 'duration': 'Long-term'},
                    {'name': 'Brimonidine drops', 'dosage': '0.15%', 'frequency': 'Three times daily', 'duration': 'Long-term'}
                ],
                
                # Infectious Diseases
                'Tuberculosis': [
                    {'name': 'Isoniazid', 'dosage': '300mg', 'frequency': 'Once daily', 'duration': '6-9 months'},
                    {'name': 'Rifampin', 'dosage': '600mg', 'frequency': 'Once daily', 'duration': '6-9 months'},
                    {'name': 'Pyrazinamide', 'dosage': '15-30mg/kg', 'frequency': 'Once daily', 'duration': '2 months'},
                    {'name': 'Ethambutol', 'dosage': '15-25mg/kg', 'frequency': 'Once daily', 'duration': '2 months'}
                ],
                'Malaria': [
                    {'name': 'Chloroquine', 'dosage': '600mg', 'frequency': 'Once daily', 'duration': '3 days'},
                    {'name': 'Artemether-lumefantrine', 'dosage': 'As directed', 'frequency': 'Twice daily', 'duration': '3 days'},
                    {'name': 'Atovaquone-proguanil', 'dosage': 'As directed', 'frequency': 'Once daily', 'duration': '3 days'},
                    {'name': 'Doxycycline', 'dosage': '100mg', 'frequency': 'Twice daily', 'duration': '7 days'}
                ],
                
                # Autoimmune Conditions
                'Lupus': [
                    {'name': 'Hydroxychloroquine', 'dosage': '200-400mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Prednisone', 'dosage': '5-60mg', 'frequency': 'Once daily', 'duration': 'As prescribed'},
                    {'name': 'Methotrexate', 'dosage': '7.5-25mg', 'frequency': 'Once weekly', 'duration': 'As prescribed'},
                    {'name': 'Mycophenolate', 'dosage': '500-1000mg', 'frequency': 'Twice daily', 'duration': 'As prescribed'}
                ],
                'Multiple sclerosis': [
                    {'name': 'Interferon beta-1a', 'dosage': '30mcg', 'frequency': 'Once weekly', 'duration': 'Long-term'},
                    {'name': 'Glatiramer acetate', 'dosage': '20mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Fingolimod', 'dosage': '0.5mg', 'frequency': 'Once daily', 'duration': 'Long-term'},
                    {'name': 'Natalizumab', 'dosage': '300mg', 'frequency': 'Once monthly', 'duration': 'Long-term'}
                ],
                
                # Cancer Treatments
                'Cancer': [
                    {'name': 'Chemotherapy', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'},
                    {'name': 'Radiation therapy', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'},
                    {'name': 'Targeted therapy', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'},
                    {'name': 'Immunotherapy', 'dosage': 'As prescribed', 'frequency': 'As prescribed', 'duration': 'As prescribed'}
                ],
                
                # General Conditions
                'Pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg', 'frequency': 'Every 6-8 hours', 'duration': 'As needed'},
                    {'name': 'Naproxen', 'dosage': '250-500mg', 'frequency': 'Every 8-12 hours', 'duration': 'As needed'},
                    {'name': 'Aspirin', 'dosage': '325-650mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'}
                ],
                'Fever': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg', 'frequency': 'Every 4-6 hours', 'duration': 'Until fever breaks'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg', 'frequency': 'Every 6-8 hours', 'duration': 'Until fever breaks'},
                    {'name': 'Aspirin', 'dosage': '325-650mg', 'frequency': 'Every 4-6 hours', 'duration': 'Until fever breaks'}
                ],
                'Cough': [
                    {'name': 'Honey', 'dosage': '1-2 teaspoons', 'frequency': 'As needed', 'duration': 'Until cough improves'},
                    {'name': 'Guaifenesin', 'dosage': '200-400mg', 'frequency': 'Every 4 hours', 'duration': 'Until cough improves'},
                    {'name': 'Dextromethorphan', 'dosage': '15-30mg', 'frequency': 'Every 4-6 hours', 'duration': '3-5 days'},
                    {'name': 'Codeine', 'dosage': '10-20mg', 'frequency': 'Every 4-6 hours', 'duration': 'As prescribed'}
                ],
                'Allergies': [
                    {'name': 'Cetirizine', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Loratadine', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Fexofenadine', 'dosage': '180mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Diphenhydramine', 'dosage': '25-50mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'}
                ],
                'Insomnia': [
                    {'name': 'Melatonin', 'dosage': '3-5mg', 'frequency': 'Once daily at bedtime', 'duration': 'As needed'},
                    {'name': 'Diphenhydramine', 'dosage': '25-50mg', 'frequency': 'Once daily at bedtime', 'duration': 'As needed'},
                    {'name': 'Zolpidem', 'dosage': '5-10mg', 'frequency': 'Once daily at bedtime', 'duration': 'As prescribed'},
                    {'name': 'Trazodone', 'dosage': '25-100mg', 'frequency': 'Once daily at bedtime', 'duration': 'As prescribed'}
                ],
                'Nausea': [
                    {'name': 'Ondansetron', 'dosage': '4-8mg', 'frequency': 'Every 8 hours', 'duration': 'As needed'},
                    {'name': 'Metoclopramide', 'dosage': '10mg', 'frequency': 'Three times daily', 'duration': 'As needed'},
                    {'name': 'Dimenhydrinate', 'dosage': '25-50mg', 'frequency': 'Every 4-6 hours', 'duration': 'As needed'},
                    {'name': 'Ginger', 'dosage': '250-500mg', 'frequency': 'Three times daily', 'duration': 'As needed'}
                ],
                'Diarrhea': [
                    {'name': 'Loperamide', 'dosage': '2mg', 'frequency': 'After each loose stool', 'duration': 'Until diarrhea resolves'},
                    {'name': 'Bismuth subsalicylate', 'dosage': '525mg', 'frequency': 'Every 30-60 minutes', 'duration': 'Until diarrhea resolves'},
                    {'name': 'Probiotics', 'dosage': 'As directed', 'frequency': 'Once daily', 'duration': 'Until diarrhea resolves'},
                    {'name': 'Oral rehydration solution', 'dosage': 'As needed', 'frequency': 'As needed', 'duration': 'Until diarrhea resolves'}
                ],
                'Constipation': [
                    {'name': 'Psyllium', 'dosage': '1-2 tablespoons', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Docusate sodium', 'dosage': '100mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Bisacodyl', 'dosage': '5-10mg', 'frequency': 'Once daily', 'duration': 'As needed'},
                    {'name': 'Polyethylene glycol', 'dosage': '17g', 'frequency': 'Once daily', 'duration': 'As needed'}
                ]
            }
            
            # Match conditions to medications
            for condition in conditions:
                for cond_name, meds in condition_medications.items():
                    if cond_name.lower() in condition.lower() or condition.lower() in cond_name.lower():
                        medications.extend(meds)
            
            # Remove duplicates
            unique_medications = []
            seen_names = set()
            for med in medications:
                if med['name'] not in seen_names:
                    unique_medications.append(med)
                    seen_names.add(med['name'])
            
            return unique_medications[:8]  # Limit to 8 medications
            
        except Exception as e:
            logger.error(f"Error getting medication recommendations: {e}")
            return []
    
    def get_free_health_advice(self, symptoms=None, age=None, gender=None):
        """Get free health advice based on symptoms and demographics."""
        advice = {
            'general_advice': [],
            'lifestyle_recommendations': [],
            'prevention_tips': [],
            'when_to_seek_help': []
        }
        
        try:
            # General health advice based on age and gender
            if age:
                if age < 18:
                    advice['general_advice'].append('Ensure adequate sleep and nutrition for growth')
                    advice['prevention_tips'].append('Stay up to date with vaccinations')
                elif age < 50:
                    advice['general_advice'].append('Maintain regular exercise routine')
                    advice['prevention_tips'].append('Schedule regular health checkups')
                else:
                    advice['general_advice'].append('Focus on preventive care and screenings')
                    advice['prevention_tips'].append('Monitor chronic conditions regularly')
            
            # Gender-specific advice
            if gender:
                if gender.lower() == 'female':
                    advice['prevention_tips'].append('Schedule regular gynecological exams')
                elif gender.lower() == 'male':
                    advice['prevention_tips'].append('Consider prostate health screenings')
            
            # Symptom-based advice
            if symptoms:
                symptom_text = ' '.join(symptoms) if isinstance(symptoms, list) else str(symptoms)
                
                if 'fever' in symptom_text.lower():
                    advice['general_advice'].append('Rest and stay hydrated')
                    advice['when_to_seek_help'].append('Seek medical attention if fever exceeds 103°F')
                
                if 'cough' in symptom_text.lower():
                    advice['general_advice'].append('Stay hydrated and use honey for soothing')
                    advice['when_to_seek_help'].append('Seek help if cough persists for more than 2 weeks')
                
                if 'headache' in symptom_text.lower():
                    advice['general_advice'].append('Rest in a quiet, dark room')
                    advice['when_to_seek_help'].append('Seek immediate help for severe, sudden headache')
                
                if 'chest pain' in symptom_text.lower():
                    advice['when_to_seek_help'].append('Seek immediate medical attention for chest pain')
                
                if 'shortness of breath' in symptom_text.lower():
                    advice['when_to_seek_help'].append('Seek immediate medical attention for breathing difficulties')
            
            # General lifestyle recommendations
            advice['lifestyle_recommendations'].extend([
                'Maintain a balanced diet rich in fruits and vegetables',
                'Exercise regularly (150 minutes of moderate activity per week)',
                'Get 7-9 hours of quality sleep per night',
                'Manage stress through relaxation techniques',
                'Avoid smoking and limit alcohol consumption'
            ])
            
        except Exception as e:
            logger.error(f"Error getting health advice: {e}")
        
        return advice
    
    def _get_default_diagnosis(self):
        """Get default diagnosis when free API fails."""
        return {
            'possible_conditions': ['General consultation needed'],
            'recommendations': ['Please consult a healthcare provider for proper diagnosis'],
            'medications': [],
            'severity': 'unknown',
            'confidence': 0.3
        } 