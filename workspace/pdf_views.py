"""
PDF Generation Module
Automatic PDF generation for estimates, reports, signatures, payout slips, etc.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import base64

from .models import (
    Estimate, EstimateLineItem, Job, JobCompletion, 
    Payout, ComplianceData, Contractor
)
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== Estimate PDF ====================

class GenerateEstimatePDFView(APIView):
    """Generate PDF for estimate"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request, estimate_id):
        estimate = get_object_or_404(Estimate, id=estimate_id)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )

        
        # Title
        title = Paragraph(f"ESTIMATE", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Company Info (Header)
        company_data = [
            ['Your Company Name', ''],
            ['123 Business Street', f'Estimate #: {estimate.estimate_number}'],
            ['City, State 12345', f'Date: {estimate.created_at.strftime("%B %d, %Y")}'],
            ['Phone: (555) 123-4567', f'Valid Until: {estimate.valid_until or "N/A"}'],
        ]
        
        company_table = Table(company_data, colWidths=[3.5*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Info
        elements.append(Paragraph("BILL TO:", heading_style))
        
        customer_info = []
        if estimate.job:
            if estimate.job.customer_name:
                customer_info.append([estimate.job.customer_name])
            if estimate.job.customer_address:
                customer_info.append([estimate.job.customer_address])
            if estimate.job.customer_email:
                customer_info.append([f'Email: {estimate.job.customer_email}'])
            if estimate.job.customer_phone:
                customer_info.append([f'Phone: {estimate.job.customer_phone}'])
        
        if customer_info:
            customer_table = Table(customer_info, colWidths=[6.5*inch])
            customer_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(customer_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Estimate Details
        elements.append(Paragraph(f"Project: {estimate.title}", heading_style))
        if estimate.description:
            desc = Paragraph(estimate.description, styles['Normal'])
            elements.append(desc)
        elements.append(Spacer(1, 0.2*inch))
        
        # Line Items Table
        line_items_data = [['#', 'Description', 'Qty', 'Unit Price', 'Total']]
        
        for idx, item in enumerate(estimate.line_items.all().order_by('item_order'), 1):
            line_items_data.append([
                str(idx),
                item.description,
                str(item.quantity),
                f'${item.unit_price:,.2f}',
                f'${item.total:,.2f}'
            ])
        
        line_items_table = Table(line_items_data, colWidths=[0.5*inch, 3.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        line_items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))
        elements.append(line_items_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Totals
        totals_data = [
            ['Subtotal:', f'${estimate.subtotal:,.2f}'],
            [f'Tax ({estimate.tax_rate}%):', f'${estimate.tax_amount:,.2f}'],
        ]
        
        if estimate.discount_amount > 0:
            totals_data.append(['Discount:', f'-${estimate.discount_amount:,.2f}'])
        
        totals_data.append(['TOTAL:', f'${estimate.total_amount:,.2f}'])
        
        totals_table = Table(totals_data, colWidths=[5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c3e50')),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Signature Section
        if estimate.customer_signature:
            elements.append(Paragraph("Customer Signature:", heading_style))
            elements.append(Paragraph(f"Signed on: {estimate.customer_signed_at.strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        else:
            elements.append(Paragraph("Terms & Conditions:", heading_style))
            elements.append(Paragraph("This estimate is valid for 30 days from the date above. Payment terms: 50% deposit, 50% upon completion.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="estimate_{estimate.estimate_number}.pdf"'
        
        return response


# ==================== Job Report PDF ====================

class GenerateJobReportPDFView(APIView):
    """Generate PDF for completed job report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("JOB COMPLETION REPORT", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Job Information
        job_data = [
            ['Job Number:', job.job_number],
            ['Job Title:', job.title],
            ['Status:', job.status],
            ['Priority:', job.priority],
            ['Created Date:', job.created_at.strftime('%B %d, %Y')],
            ['Start Date:', job.start_date.strftime('%B %d, %Y') if job.start_date else 'N/A'],
            ['Due Date:', job.due_date.strftime('%B %d, %Y') if job.due_date else 'N/A'],
            ['Completed Date:', job.completed_date.strftime('%B %d, %Y') if job.completed_date else 'N/A'],
        ]
        
        job_table = Table(job_data, colWidths=[2*inch, 4.5*inch])
        job_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(job_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Information
        elements.append(Paragraph("Customer Information", styles['Heading2']))
        customer_data = [
            ['Name:', job.customer_name or 'N/A'],
            ['Email:', job.customer_email or 'N/A'],
            ['Phone:', job.customer_phone or 'N/A'],
            ['Address:', job.customer_address or 'N/A'],
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4.5*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Cost Information
        elements.append(Paragraph("Cost Information", styles['Heading2']))
        cost_data = [
            ['Estimated Cost:', f'${job.estimated_cost:,.2f}' if job.estimated_cost else 'N/A'],
            ['Actual Cost:', f'${job.actual_cost:,.2f}' if job.actual_cost else 'N/A'],
            ['Estimated Hours:', f'{job.estimated_hours}' if job.estimated_hours else 'N/A'],
            ['Actual Hours:', f'{job.actual_hours}' if job.actual_hours else 'N/A'],
        ]
        
        cost_table = Table(cost_data, colWidths=[2*inch, 4.5*inch])
        cost_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(cost_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Job Description
        elements.append(Paragraph("Job Description", styles['Heading2']))
        desc = Paragraph(job.description or 'No description provided', styles['Normal'])
        elements.append(desc)
        elements.append(Spacer(1, 0.3*inch))
        
        # Completion Details
        if hasattr(job, 'completion'):
            completion = job.completion
            elements.append(Paragraph("Completion Details", styles['Heading2']))
            
            completion_data = [
                ['Status:', completion.status],
                ['Submitted At:', completion.submitted_at.strftime('%B %d, %Y at %I:%M %p')],
                ['Verified By:', completion.verified_by.email if completion.verified_by else 'Pending'],
                ['Verified At:', completion.verified_at.strftime('%B %d, %Y at %I:%M %p') if completion.verified_at else 'Pending'],
            ]
            
            if completion.quality_rating:
                completion_data.append(['Quality Rating:', f'{completion.quality_rating}/5'])
            if completion.timeliness_rating:
                completion_data.append(['Timeliness Rating:', f'{completion.timeliness_rating}/5'])
            if completion.professionalism_rating:
                completion_data.append(['Professionalism Rating:', f'{completion.professionalism_rating}/5'])
            if completion.overall_rating:
                completion_data.append(['Overall Rating:', f'{completion.overall_rating:.1f}/5'])
            
            completion_table = Table(completion_data, colWidths=[2*inch, 4.5*inch])
            completion_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ]))
            elements.append(completion_table)
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="job_report_{job.job_number}.pdf"'
        
        return response



# ==================== Payout Slip PDF ====================

class GeneratePayoutSlipPDFView(APIView):
    """Generate PDF for payout slip"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payout_id):
        payout = get_object_or_404(Payout, id=payout_id)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#27ae60'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("PAYOUT SLIP", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Payout Information
        payout_data = [
            ['Payout Number:', payout.payout_number],
            ['Date:', payout.created_at.strftime('%B %d, %Y')],
            ['Status:', payout.status],
            ['Payment Method:', payout.get_payment_method_display()],
        ]
        
        if payout.paid_date:
            payout_data.append(['Paid Date:', payout.paid_date.strftime('%B %d, %Y')])
        
        payout_table = Table(payout_data, colWidths=[2.5*inch, 4*inch])
        payout_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(payout_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Contractor Information
        elements.append(Paragraph("Payee Information", styles['Heading2']))
        contractor_data = [
            ['Contractor:', payout.contractor.user.email],
            ['Company:', payout.contractor.company_name or 'N/A'],
            ['License Number:', payout.contractor.license_number or 'N/A'],
        ]
        
        contractor_table = Table(contractor_data, colWidths=[2.5*inch, 4*inch])
        contractor_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(contractor_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Job Information
        if payout.job:
            elements.append(Paragraph("Job Information", styles['Heading2']))
            job_data = [
                ['Job Number:', payout.job.job_number],
                ['Job Title:', payout.job.title],
                ['Completed Date:', payout.job.completed_date.strftime('%B %d, %Y') if payout.job.completed_date else 'N/A'],
            ]
            
            job_table = Table(job_data, colWidths=[2.5*inch, 4*inch])
            job_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ]))
            elements.append(job_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Amount Section
        amount_data = [
            ['PAYOUT AMOUNT:', f'${payout.amount:,.2f}'],
        ]
        
        amount_table = Table(amount_data, colWidths=[4*inch, 2.5*inch])
        amount_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#27ae60')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#27ae60')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f8f5')),
        ]))
        elements.append(amount_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Notes
        if payout.notes:
            elements.append(Paragraph("Notes:", styles['Heading3']))
            notes = Paragraph(payout.notes, styles['Normal'])
            elements.append(notes)
            elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = "This is an official payout slip. Please keep for your records."
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="payout_slip_{payout.payout_number}.pdf"'
        
        return response


# ==================== Compliance Certificate PDF ====================

class GenerateComplianceCertificatePDFView(APIView):
    """Generate PDF for compliance certificate"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, compliance_id):
        compliance = get_object_or_404(ComplianceData, id=compliance_id)
        
        if compliance.status != 'APPROVED':
            return Response(
                {'error': 'Certificate can only be generated for approved compliance documents'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        title = Paragraph("COMPLIANCE CERTIFICATE", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Certificate Number
        cert_num_style = ParagraphStyle(
            'CertNum',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        cert_num = Paragraph(f"Certificate No: CERT-{compliance.id:06d}", cert_num_style)
        elements.append(cert_num)
        elements.append(Spacer(1, 0.4*inch))
        
        # Certificate Text
        cert_text_style = ParagraphStyle(
            'CertText',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            leading=20
        )
        
        cert_text = f"""
        This is to certify that<br/>
        <b>{compliance.contractor.user.email}</b><br/>
        {compliance.contractor.company_name or ''}<br/><br/>
        has successfully completed and submitted<br/>
        <b>{compliance.get_compliance_type_display()}</b><br/><br/>
        Document: {compliance.document_name}<br/>
        Document Number: {compliance.document_number or 'N/A'}<br/><br/>
        This certificate is valid from {compliance.issue_date or 'N/A'} to {compliance.expiry_date or 'N/A'}
        """
        
        cert_para = Paragraph(cert_text, cert_text_style)
        elements.append(cert_para)
        elements.append(Spacer(1, 0.5*inch))
        
        # Verification Details
        verification_data = [
            ['Verified By:', compliance.verified_by.email if compliance.verified_by else 'N/A'],
            ['Verification Date:', compliance.verified_at.strftime('%B %d, %Y') if compliance.verified_at else 'N/A'],
            ['Status:', compliance.status],
        ]
        
        verification_table = Table(verification_data, colWidths=[2*inch, 4.5*inch])
        verification_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(verification_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Signature Line
        sig_style = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("_" * 40, sig_style))
        elements.append(Paragraph("Authorized Signature", sig_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="compliance_certificate_{compliance.id}.pdf"'
        
        return response


# ==================== Investor Report PDF ====================

class GenerateInvestorReportPDFView(APIView):
    """Generate comprehensive PDF investor report"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        from datetime import datetime, timedelta
        from django.db.models import Sum, Avg, Count
        
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8e44ad'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("INVESTOR REPORT", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Report Period
        period_style = ParagraphStyle(
            'Period',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER
        )
        period = Paragraph(f"Period: {date_from.strftime('%B %d, %Y')} to {date_to.strftime('%B %d, %Y')}", period_style)
        elements.append(period)
        elements.append(Spacer(1, 0.3*inch))
        
        # Calculate metrics
        jobs_queryset = Job.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        total_revenue = jobs_queryset.filter(status='COMPLETED').aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        total_payouts = Payout.objects.filter(
            status='COMPLETED',
            paid_date__gte=date_from,
            paid_date__lte=date_to
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        net_profit = total_revenue - total_payouts
        roi = ((net_profit / total_payouts) * 100) if total_payouts > 0 else 0
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", styles['Heading2']))
        
        summary_data = [
            ['Total Revenue', f'${total_revenue:,.2f}'],
            ['Total Payouts', f'${total_payouts:,.2f}'],
            ['Net Profit', f'${net_profit:,.2f}'],
            ['ROI', f'{roi:.2f}%'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Job Statistics
        elements.append(Paragraph("Job Statistics", styles['Heading2']))
        
        total_jobs = jobs_queryset.count()
        completed_jobs = jobs_queryset.filter(status='COMPLETED').count()
        active_jobs = jobs_queryset.filter(status='IN_PROGRESS').count()
        pending_jobs = jobs_queryset.filter(status='PENDING').count()
        
        job_stats_data = [
            ['Total Jobs', str(total_jobs)],
            ['Completed Jobs', str(completed_jobs)],
            ['Active Jobs', str(active_jobs)],
            ['Pending Jobs', str(pending_jobs)],
            ['Completion Rate', f'{(completed_jobs/total_jobs*100):.1f}%' if total_jobs > 0 else '0%'],
        ]
        
        job_stats_table = Table(job_stats_data, colWidths=[3*inch, 3.5*inch])
        job_stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(job_stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style)
        elements.append(Spacer(1, 0.5*inch))
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="investor_report_{date_from}_{date_to}.pdf"'
        
        return response
