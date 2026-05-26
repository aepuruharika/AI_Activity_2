from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any


def generate_resume_summary_pdf(
    candidate_name: str,
    job_title: str,
    extracted_resume: Dict[str, Any],
    analysis: Dict[str, Any],
    recruiter_summary: Dict[str, Any]
) -> BytesIO:
    """
    Generate a comprehensive PDF summary of resume screening.
    Returns BytesIO object that can be sent as file download.
    """

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#2563eb'),
        borderWidth=2,
        borderPadding=4
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=12
    )

    story.append(Paragraph("Resume Screening Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(f"<b>Candidate:</b> {candidate_name}", normal_style))
    story.append(Paragraph(f"<b>Position Applied For:</b> {job_title}", normal_style))
    story.append(Paragraph(f"<b>Generated Date:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    if recruiter_summary.get('executive_summary'):
        story.append(Paragraph(recruiter_summary['executive_summary'], normal_style))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("MATCH ASSESSMENT", heading_style))

    match_score = analysis.get('match_score', 0)
    is_qualified = analysis.get('is_qualified', match_score > 70)

    score_text = f"<b>Overall Match Score:</b> {match_score}%"
    status_text = f"<b>Qualification Status:</b> {'<font color=green>QUALIFIED</font>' if is_qualified else '<font color=red>NOT QUALIFIED</font>'}"

    story.append(Paragraph(score_text, normal_style))
    story.append(Paragraph(status_text, normal_style))
    story.append(Spacer(1, 0.1*inch))

    if analysis.get('score_breakdown'):
        breakdown = analysis['score_breakdown']
        breakdown_data = [
            ['Criterion', 'Score'],
            ['Skills Match', f"{breakdown.get('skills_match', 0)}%"],
            ['Experience Match', f"{breakdown.get('experience_match', 0)}%"],
            ['Education Match', f"{breakdown.get('education_match', 0)}%"]
        ]
        breakdown_table = Table(breakdown_data, colWidths=[3*inch, 2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 0.1*inch))

    if analysis.get('matching_skills'):
        skills_text = f"<b>Matching Skills:</b> {', '.join(analysis['matching_skills'])}"
        story.append(Paragraph(skills_text, normal_style))

    if analysis.get('missing_skills'):
        missing_text = f"<b>Missing Skills:</b> {', '.join(analysis['missing_skills'])}"
        story.append(Paragraph(missing_text, normal_style))

    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("CANDIDATE INFORMATION", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {extracted_resume.get('name', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Email:</b> {extracted_resume.get('email', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Phone:</b> {extracted_resume.get('phone', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Education:</b> {extracted_resume.get('education', 'N/A')}", normal_style))

    if extracted_resume.get('experience_years'):
        story.append(Paragraph(f"<b>Years of Experience:</b> {extracted_resume['experience_years']}", normal_style))

    if extracted_resume.get('skills'):
        skills_text = f"<b>Skills:</b> {', '.join(extracted_resume['skills'])}"
        story.append(Paragraph(skills_text, normal_style))

    if extracted_resume.get('certifications'):
        certs_text = f"<b>Certifications:</b> {', '.join(extracted_resume['certifications'])}"
        story.append(Paragraph(certs_text, normal_style))

    story.append(Spacer(1, 0.2*inch))

    if is_qualified and analysis.get('interview_questions'):
        story.append(PageBreak())
        story.append(Paragraph("INTERVIEW QUESTIONS", heading_style))
        story.append(Paragraph("The following advanced technical questions have been prepared for this candidate:", normal_style))
        story.append(Spacer(1, 0.1*inch))

        for idx, question in enumerate(analysis['interview_questions'], 1):
            question_para = Paragraph(f"<b>{idx}. </b>{question}", normal_style)
            story.append(question_para)
            story.append(Spacer(1, 0.08*inch))

    else:
        story.append(Paragraph("FEEDBACK & RECOMMENDATIONS", heading_style))

        if analysis.get('rejection_reasons'):
            story.append(Paragraph("<b>Reasons for Not Meeting Requirements:</b>", normal_style))
            for reason in analysis['rejection_reasons']:
                reason_para = Paragraph(f"• {reason}", normal_style)
                story.append(reason_para)
                story.append(Spacer(1, 0.05*inch))
            story.append(Spacer(1, 0.1*inch))

        if analysis.get('improvement_suggestions'):
            story.append(Paragraph("<b>Improvement Suggestions:</b>", normal_style))
            for suggestion in analysis['improvement_suggestions']:
                sugg_para = Paragraph(f"• {suggestion}", normal_style)
                story.append(sugg_para)
                story.append(Spacer(1, 0.05*inch))

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("RECRUITER RECOMMENDATION", heading_style))

    if recruiter_summary.get('recommendation'):
        recommendation = recruiter_summary['recommendation']
        rec_color = 'green' if recommendation == 'RECOMMEND' else 'red' if recommendation == 'DO NOT RECOMMEND' else 'orange'
        rec_text = f"<b>Recommendation:</b> <font color={rec_color}><b>{recommendation}</b></font>"
        story.append(Paragraph(rec_text, normal_style))

    if recruiter_summary.get('recommendation_reason'):
        reason_text = f"<b>Reason:</b> {recruiter_summary['recommendation_reason']}"
        story.append(Paragraph(reason_text, normal_style))

    if recruiter_summary.get('key_highlights'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Key Highlights:</b>", normal_style))
        for highlight in recruiter_summary['key_highlights']:
            highlight_para = Paragraph(f"• {highlight}", normal_style)
            story.append(highlight_para)
            story.append(Spacer(1, 0.05*inch))

    if recruiter_summary.get('interview_complexity'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Interview Complexity Level:</b> {recruiter_summary['interview_complexity']}", normal_style))

    if recruiter_summary.get('next_steps'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Next Steps:</b>", normal_style))
        for step in recruiter_summary['next_steps']:
            step_para = Paragraph(f"• {step}", normal_style)
            story.append(step_para)
            story.append(Spacer(1, 0.05*inch))

    story.append(Spacer(1, 0.3*inch))
    footer_text = "This report was generated using AI-powered resume screening technology."
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))

    pdf.build(story)
    buffer.seek(0)
    return buffer
