"""
Insurance Verification System Views
Contractor insurance validation and compliance tracking
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
# PyPDF2 import - install with: pip install PyPDF2
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    # Mock for development
    class PyPDF2:
        class PdfReader:
            def __init__(self, *args):
                self.pages = []
import re
import json

from .models import InsuranceVerification, Contractor, Workspace
from .serializers import InsuranceVerificationSerializer
from authentication.permissions import IsAdmin, IsAdminOrFM, IsContractor


# ==================== Insurance Verification Management ====================

class InsuranceVerificationListView(generics.ListAPIView):
    """List insurance verifications"""
    serializer_class = InsuranceVerificationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = InsuranceVerification.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by workspace
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(contractor__workspace__workspace_id=workspace_id)
        
        # Filter expiring soon
        expiring_soon = self.request.query_params.get('expiring_soon')
        if expiring_soon == 'true':
            thirty_days_from_now = timezone.now().date() + timedelta(days=30)
            queryset = queryset.filter(
                expiry_date__lte=thirty_days_from_now,
                expiry_date__gt=timezone.now().date(),
                status='ACTIVE'
            )
        
        # Filter expired
        expired = self.request.query_params.get('expired')
        if expired == 'true':
            queryset = queryset.filter(
                expiry_date__lt=timezone.now().date()
            )
        
        return queryset


class ContractorInsuranceView(APIView):
    """Get or update contractor's insurance verification"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, contractor_id):
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        # Check permissions
        if request.user.role not in ['ADMIN', 'FM'] and contractor.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            insurance = InsuranceVerification.objects.get(contractor=contractor)
            return Response(InsuranceVerificationSerializer(insurance).data)
        except InsuranceVerification.DoesNotExist:
            return Response({
                'contractor_id': contractor_id,
                'insurance_status': 'NOT_SUBMITTED',
                'message': 'No insurance verification found'
            })
    
    def post(self, request, contractor_id):
        """Upload insurance document for verification"""
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        # Check permissions - contractor can upload their own, admin/FM can upload any
        if request.user.role not in ['ADMIN', 'FM'] and contractor.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get uploaded file
        document_file = request.FILES.get('document')
        if not document_file:
            return Response(
                {'error': 'Insurance document file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        if not document_file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'Only PDF files are accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse insurance document
            parsed_data = self._parse_insurance_document(document_file)
            
            # Create or update insurance verification
            insurance, created = InsuranceVerification.objects.update_or_create(
                contractor=contractor,
                defaults={
                    'insurance_company': parsed_data.get('insurance_company', ''),
                    'policy_number': parsed_data.get('policy_number', ''),
                    'coverage_amount': parsed_data.get('coverage_amount', 0),
                    'effective_date': parsed_data.get('effective_date'),
                    'expiry_date': parsed_data.get('expiry_date'),
                    'document_path': f'insurance/{contractor.id}/{document_file.name}',
                    'document_parsed_data': parsed_data,
                    'status': 'PENDING',
                    'apex_co_insured': parsed_data.get('apex_co_insured', False)
                }
            )
            
            # Auto-flag if issues detected
            self._auto_flag_insurance_issues(insurance)
            
            return Response({
                'message': 'Insurance document uploaded successfully',
                'insurance': InsuranceVerificationSerializer(insurance).data,
                'parsed_data': parsed_data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process insurance document: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _parse_insurance_document(self, document_file):
        """Parse insurance PDF document"""
        try:
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(document_file)
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            
            # Parse insurance information using regex patterns
            parsed_data = {
                'raw_text': text_content,
                'insurance_company': self._extract_insurance_company(text_content),
                'policy_number': self._extract_policy_number(text_content),
                'coverage_amount': self._extract_coverage_amount(text_content),
                'effective_date': self._extract_effective_date(text_content),
                'expiry_date': self._extract_expiry_date(text_content),
                'apex_co_insured': self._check_apex_co_insured(text_content)
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def _extract_insurance_company(self, text):
        """Extract insurance company name"""
        # Common insurance company patterns
        companies = [
            'State Farm', 'Allstate', 'GEICO', 'Progressive', 'Liberty Mutual',
            'Farmers', 'USAA', 'Nationwide', 'American Family', 'Travelers'
        ]
        
        for company in companies:
            if company.lower() in text.lower():
                return company
        
        # Try to extract from common patterns
        patterns = [
            r'Insurance Company[:\s]+([A-Za-z\s&]+)',
            r'Insurer[:\s]+([A-Za-z\s&]+)',
            r'Company[:\s]+([A-Za-z\s&]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return 'Unknown'
    
    def _extract_policy_number(self, text):
        """Extract policy number"""
        patterns = [
            r'Policy\s*(?:Number|No\.?)[:\s]+([A-Z0-9\-]+)',
            r'Policy[:\s]+([A-Z0-9\-]+)',
            r'Certificate\s*(?:Number|No\.?)[:\s]+([A-Z0-9\-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_coverage_amount(self, text):
        """Extract coverage amount"""
        patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)\s*(?:per|each|aggregate)',
            r'Coverage[:\s]+\$([0-9,]+)',
            r'Limit[:\s]+\$([0-9,]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return 0
    
    def _extract_effective_date(self, text):
        """Extract effective date"""
        patterns = [
            r'Effective\s*(?:Date)?[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'From[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'Start\s*(?:Date)?[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Parse date (handle different formats)
                    return self._parse_date_string(date_str)
                except:
                    continue
        
        return None
    
    def _extract_expiry_date(self, text):
        """Extract expiry date"""
        patterns = [
            r'Expir(?:y|ation)\s*(?:Date)?[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'To[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'End\s*(?:Date)?[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    return self._parse_date_string(date_str)
                except:
                    continue
        
        return None
    
    def _check_apex_co_insured(self, text):
        """Check if Apex is listed as co-insured"""
        apex_patterns = [
            r'apex',
            r'co-?insured.*apex',
            r'additional.*insured.*apex'
        ]
        
        for pattern in apex_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _parse_date_string(self, date_str):
        """Parse date string into date object"""
        formats = ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _auto_flag_insurance_issues(self, insurance):
        """Auto-flag insurance issues"""
        issues = []
        
        # Check if expired
        if insurance.is_expired:
            issues.append("Insurance policy is expired")
            insurance.status = 'EXPIRED'
        
        # Check if expiring soon
        elif insurance.is_expiring_soon:
            issues.append("Insurance policy expires within 30 days")
        
        # Check coverage amount
        if insurance.coverage_amount < 1000000:  # $1M minimum
            issues.append("Coverage amount below minimum requirement ($1,000,000)")
        
        # Check if Apex is co-insured
        if not insurance.apex_co_insured:
            issues.append("Apex is not listed as co-insured")
            insurance.status = 'CO_INSURED_MISSING'
        
        if issues:
            insurance.auto_flagged = True
            insurance.flag_reason = "; ".join(issues)
        
        insurance.save()


class ApproveInsuranceView(APIView):
    """Approve insurance verification"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, insurance_id):
        insurance = get_object_or_404(InsuranceVerification, id=insurance_id)
        
        notes = request.data.get('notes', '')
        
        insurance.verify_insurance(request.user, notes)
        
        return Response({
            'message': 'Insurance approved successfully',
            'insurance': InsuranceVerificationSerializer(insurance).data
        })


class RejectInsuranceView(APIView):
    """Reject insurance verification"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, insurance_id):
        insurance = get_object_or_404(InsuranceVerification, id=insurance_id)
        
        rejection_reason = request.data.get('reason', '')
        
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        insurance.status = 'INVALID'
        insurance.verified_by = request.user
        insurance.verified_at = timezone.now()
        insurance.verification_notes = rejection_reason
        insurance.save()
        
        return Response({
            'message': 'Insurance rejected',
            'insurance': InsuranceVerificationSerializer(insurance).data
        })


# ==================== Insurance Compliance Dashboard ====================

class InsuranceComplianceDashboardView(APIView):
    """Insurance compliance dashboard"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        workspace_id = request.query_params.get('workspace_id')
        
        if workspace_id:
            contractors = Contractor.objects.filter(workspace__workspace_id=workspace_id)
        else:
            contractors = Contractor.objects.all()
        
        total_contractors = contractors.count()
        
        # Insurance status breakdown
        insurance_verifications = InsuranceVerification.objects.filter(
            contractor__in=contractors
        )
        
        status_counts = insurance_verifications.values('status').annotate(
            count=Count('id')
        )
        
        # Expiring soon
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        expiring_soon = insurance_verifications.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=timezone.now().date(),
            status='ACTIVE'
        ).count()
        
        # Expired
        expired = insurance_verifications.filter(
            expiry_date__lt=timezone.now().date()
        ).count()
        
        # No insurance submitted
        contractors_with_insurance = insurance_verifications.values_list('contractor_id', flat=True)
        no_insurance = contractors.exclude(id__in=contractors_with_insurance).count()
        
        # Auto-flagged issues
        auto_flagged = insurance_verifications.filter(auto_flagged=True).count()
        
        return Response({
            'summary': {
                'total_contractors': total_contractors,
                'with_insurance': insurance_verifications.count(),
                'no_insurance': no_insurance,
                'expiring_soon': expiring_soon,
                'expired': expired,
                'auto_flagged': auto_flagged
            },
            'status_breakdown': list(status_counts),
            'compliance_rate': (
                insurance_verifications.filter(status='ACTIVE').count() / total_contractors * 100
            ) if total_contractors > 0 else 0
        })


class InsuranceExpiryNotificationsView(APIView):
    """Get contractors with expiring insurance"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        days_ahead = int(request.query_params.get('days', 30))
        
        expiry_threshold = timezone.now().date() + timedelta(days=days_ahead)
        
        expiring_insurance = InsuranceVerification.objects.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gt=timezone.now().date(),
            status='ACTIVE'
        ).select_related('contractor', 'contractor__user')
        
        notifications = []
        for insurance in expiring_insurance:
            days_until_expiry = (insurance.expiry_date - timezone.now().date()).days
            
            notifications.append({
                'contractor_id': insurance.contractor.id,
                'contractor_email': insurance.contractor.user.email,
                'contractor_company': insurance.contractor.company_name,
                'insurance_company': insurance.insurance_company,
                'policy_number': insurance.policy_number,
                'expiry_date': insurance.expiry_date,
                'days_until_expiry': days_until_expiry,
                'urgency': 'HIGH' if days_until_expiry <= 7 else 'MEDIUM' if days_until_expiry <= 14 else 'LOW'
            })
        
        # Sort by urgency and days until expiry
        notifications.sort(key=lambda x: (x['urgency'] != 'HIGH', x['days_until_expiry']))
        
        return Response({
            'expiring_insurance': notifications,
            'total_expiring': len(notifications),
            'high_urgency': len([n for n in notifications if n['urgency'] == 'HIGH']),
            'medium_urgency': len([n for n in notifications if n['urgency'] == 'MEDIUM'])
        })