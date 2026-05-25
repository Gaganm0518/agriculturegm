"""
PDF Report Generation Routes.
"""

import os
import time
import json
from datetime import datetime, timedelta
from flask import Blueprint, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.prediction import Prediction
from backend.models.user import User
from backend.extensions import db
from backend.utils.helpers import api_error

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

report_bp = Blueprint('report', __name__)

def cleanup_old_reports(reports_dir):
    """Delete PDF files older than 24 hours."""
    now = time.time()
    cutoff = now - (24 * 3600)
    for root, dirs, files in os.walk(reports_dir):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass


@report_bp.route('/<prediction_type>/<int:prediction_id>', methods=['GET'])
@jwt_required()
def generate_report(prediction_type, prediction_id):
    """
    Generate and download a PDF report.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 1. Fetch data
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=user_id, prediction_type=prediction_type).first()
    if not prediction:
        return api_error("Prediction not found or unauthorized.", 404)
        
    try:
        raw_data = json.loads(prediction.raw_output)
    except json.JSONDecodeError:
        raw_data = {}

    # 2. Setup directory
    reports_dir = current_app.config.get('REPORTS_FOLDER')
    user_report_dir = os.path.join(reports_dir, str(user_id))
    os.makedirs(user_report_dir, exist_ok=True)
    
    # Clean up old reports
    cleanup_old_reports(reports_dir)
    
    filename = f"report_{prediction_type}_{prediction_id}.pdf"
    filepath = os.path.join(user_report_dir, filename)
    
    # 3. Generate PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], textColor=colors.HexColor('#16a34a'), alignment=1)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], textColor=colors.HexColor('#0f172a'))
    normal_style = styles['Normal']
    
    elements = []
    
    # Header
    elements.append(Paragraph("AI Smart Agriculture System", title_style))
    elements.append(Paragraph(f"Prediction Report: {prediction_type.replace('_', ' ').title()}", styles['Heading3']))
    elements.append(Paragraph(f"Date: {prediction.created_at.strftime('%Y-%m-%d %H:%M:%S') if prediction.created_at else 'N/A'}", normal_style))
    elements.append(Paragraph(f"Farmer: {user.name} ({user.email})", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Inputs Table
    if 'input' in raw_data:
        elements.append(Paragraph("Input Parameters", heading_style))
        input_data = [["Parameter", "Value"]]
        for k, v in raw_data['input'].items():
            input_data.append([str(k).capitalize(), str(v)])
            
        t = Table(input_data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0fdf4')),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2 * inch))

    # Prediction Result
    elements.append(Paragraph("Prediction Result", heading_style))
    
    result_text = ""
    if prediction_type == 'crop_recommendation':
        result_text = f"<b>Recommended Crop:</b> {prediction.recommended_crop} <br/><b>Confidence:</b> {prediction.confidence_score}%"
    elif prediction_type == 'disease_detection':
        result_text = f"<b>Detected Disease:</b> {prediction.disease_name} <br/><b>Confidence:</b> {prediction.confidence_score}%"
    elif prediction_type == 'yield_prediction':
        result_text = f"<b>Total Estimated Yield:</b> {prediction.predicted_yield_kg} kg <br/><b>Crop:</b> {prediction.crop_name}"
    elif prediction_type == 'fertilizer_recommendation':
        result_text = f"<b>Recommended Fertilizer:</b> {raw_data.get('fertilizer', 'N/A')} <br/><b>Confidence:</b> {raw_data.get('confidence', 'N/A')}%"
        
    p = Paragraph(result_text, normal_style)
    # Wrap result in a simple table for "box" effect
    res_table = Table([[p]], colWidths=[6*inch])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e0f2fe')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284c7')),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    elements.append(res_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Recommendation Details
    if prediction_type == 'disease_detection':
        elements.append(Paragraph("Remedy & Treatment", heading_style))
        elements.append(Paragraph(str(prediction.remedy), normal_style))
    elif prediction_type == 'fertilizer_recommendation' and 'info' in raw_data:
        info = raw_data['info']
        elements.append(Paragraph("Application Guidelines", heading_style))
        elements.append(Paragraph(f"<b>Dosage:</b> {info.get('quantity_kg_per_acre', 'N/A')} kg/acre", normal_style))
        elements.append(Paragraph(f"<b>Method:</b> {info.get('application_method', 'N/A')}", normal_style))
        elements.append(Paragraph(f"<b>Warning:</b> {info.get('warning', 'N/A')}", normal_style))
    
    elements.append(Spacer(1, 0.4 * inch))
    
    # Disclaimer
    elements.append(Paragraph("Disclaimer", styles['Heading4']))
    elements.append(Paragraph("This report is AI-generated based on input parameters. Please verify with local agricultural experts before making critical farming decisions. AI Smart Agriculture assumes no liability for crop failures.", styles['Italic']))
    
    elements.append(Spacer(1, 0.4 * inch))
    
    # Footer
    elements.append(Paragraph(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - aismartagriculture.com", styles['Italic']))
    
    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        current_app.logger.error(f"PDF generation failed: {e}")
        return api_error("Failed to generate PDF report", 500)
    
    # Serve file
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
