# PDF generation utility

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from django.utils import timezone

def generate_pdf_report(patient_record):
    """Generate PDF report for patient record."""
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Add title
    story.append(Paragraph("PATIENT MEDICAL REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Add report metadata
    story.append(Paragraph(f"Report Date: {timezone.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph(f"Report ID: {patient_record.id}", normal_style))
    story.append(Spacer(1, 20))
    
    # Patient Information Section
    story.append(Paragraph("PATIENT INFORMATION", heading_style))
    
    patient_info = [
        ['Name:', patient_record.patient_name],
        ['Age:', str(patient_record.age)],
        ['Gender:', patient_record.get_gender_display()],
        ['Blood Group:', patient_record.blood_group or 'Not specified'],
        ['Contact:', patient_record.contact_number or 'Not provided'],
        ['Email:', patient_record.email or 'Not provided'],
    ]
    
    patient_table = Table(patient_info, colWidths=[1.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 20))
    
    # Medical Information Section
    story.append(Paragraph("MEDICAL INFORMATION", heading_style))
    
    # Symptoms
    story.append(Paragraph("Symptoms:", normal_style))
    story.append(Paragraph(patient_record.symptoms, normal_style))
    story.append(Spacer(1, 12))
    
    # Medical History
    if patient_record.medical_history:
        story.append(Paragraph("Medical History:", normal_style))
        story.append(Paragraph(patient_record.medical_history, normal_style))
        story.append(Spacer(1, 12))
    
    # Current Medications
    if patient_record.current_medications:
        story.append(Paragraph("Current Medications:", normal_style))
        story.append(Paragraph(patient_record.current_medications, normal_style))
        story.append(Spacer(1, 12))
    
    # Allergies
    if patient_record.allergies:
        story.append(Paragraph("Allergies:", normal_style))
        story.append(Paragraph(patient_record.allergies, normal_style))
        story.append(Spacer(1, 12))
    
    # Address
    if patient_record.address:
        story.append(Paragraph("Address:", normal_style))
        story.append(Paragraph(patient_record.address, normal_style))
        story.append(Spacer(1, 20))
    
    # AI Diagnosis Section
    story.append(Paragraph("AI DIAGNOSIS RESULTS", heading_style))
    
    diagnosis_info = [
        ['Diagnosis:', patient_record.ai_diagnosis or 'No diagnosis available'],
        ['Confidence Score:', f"{patient_record.confidence_score:.2%}" if patient_record.confidence_score else 'N/A'],
    ]
    
    diagnosis_table = Table(diagnosis_info, colWidths=[1.5*inch, 4*inch])
    diagnosis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(diagnosis_table)
    story.append(Spacer(1, 20))
    
    # Recommended Tests
    if patient_record.recommended_tests:
        story.append(Paragraph("RECOMMENDED TESTS", heading_style))
        story.append(Paragraph(patient_record.recommended_tests, normal_style))
        story.append(Spacer(1, 20))
    
    # Treatment Plan
    if patient_record.treatment_plan:
        story.append(Paragraph("TREATMENT PLAN", heading_style))
        story.append(Paragraph(patient_record.treatment_plan, normal_style))
        story.append(Spacer(1, 20))
    
    # Prescribed Medications
    if patient_record.prescribed_medications:
        story.append(Paragraph("PRESCRIBED MEDICATIONS", heading_style))
        story.append(Paragraph("IMPORTANT: These medications are AI-recommended. Please consult with a healthcare professional before taking any medication.", normal_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(patient_record.prescribed_medications, normal_style))
        story.append(Spacer(1, 20))
    
    # Uploaded Reports Section
    story.append(Paragraph("UPLOADED REPORTS", heading_style))
    
    reports_info = []
    if patient_record.ecg_report:
        reports_info.append(['ECG Report:', 'Available'])
    else:
        reports_info.append(['ECG Report:', 'Not uploaded'])
    
    if patient_record.lab_report:
        reports_info.append(['Lab Report:', 'Available'])
    else:
        reports_info.append(['Lab Report:', 'Not uploaded'])
    
    if patient_record.xray_report:
        reports_info.append(['X-ray Report:', 'Available'])
    else:
        reports_info.append(['X-ray Report:', 'Not uploaded'])
    
    if reports_info:
        reports_table = Table(reports_info, colWidths=[1.5*inch, 4*inch])
        reports_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(reports_table)
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by DiagnoRx AI Medical System", normal_style))
    story.append(Paragraph(f"Report generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    
    # Build PDF
    doc.build(story)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
