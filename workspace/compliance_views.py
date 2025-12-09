"""
Compliance & Disputes System Views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count

from .models import (
    Contractor, ComplianceData, Dispute, DisputeMessage,
    DisputeAttachment, Job, JobNotification
)
from .serializers import (
    ComplianceDataSerializer, DisputeSerializer,
    DisputeMessageSerializer, DisputeAttachmentSerializer
)
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== Contractor Compliance Hub ====================

class ContractorComplianceListView(generics.ListAPIView):
    """Contractor views their compliance documents"""
    serializer_class = ComplianceDataSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        return ComplianceData.objects.filter(contractor=contractor).order_by('-created_at')


class ContractorUploadComplianceView(generics.CreateAPIView):
    """Contractor uploads compliance document"""
    serializer_class = ComplianceDataSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(contractor.workspace.__class__, workspace_id=workspace_id)
        
        serializer.save(
            contractor=contractor,
            workspace=workspace,
            status='PENDING'
        )


class ContractorComplianceStatsView(APIView):
    """Contractor views compliance statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        contractor = get_object_or_404(Contractor, user=request.user)
        
        total_documents = ComplianceData.objects.filter(contractor=contractor).count()
        pending = ComplianceData.objects.filter(contractor=contractor, status='PENDING').count()
        approved = ComplianceData.objects.filter(contractor=contractor, status='APPROVED').count()
        rejected = ComplianceData.objects.filter(contractor=contractor, status='REJECTED').count()
        expiring_soon = ComplianceData.objects.filter(
            contractor=contractor,
            status='APPROVED'
        ).filter(
            expiry_date__lte=timezone.now().date() + timezone.timedelta(days=30),
            expiry_date__gt=timezone.now().date()
        ).count()
        expired = ComplianceData.objects.filter(
            contractor=contractor,
            expiry_date__lt=timezone.now().date()
        ).count()
        
        return Response({
            'total_documents': total_documents,
            'pending_verification': pending,
            'approved': approved,
            'rejected': rejected,
            'expiring_soon': expiring_soon,
            'expired': expired
        })


# ==================== Admin Compliance Center ====================

class AdminComplianceListView(generics.ListAPIView):
    """Admin views all compliance documents"""
    serializer_class = ComplianceDataSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = ComplianceData.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        # Filter by contractor
        contractor_id = self.request.query_params.get('contractor_id')
        if contractor_id:
            queryset = queryset.filter(contractor_id=contractor_id)
        
        # Filter by compliance type
        compliance_type = self.request.query_params.get('compliance_type')
        if compliance_type:
            queryset = queryset.filter(compliance_type=compliance_type.upper())
        
        return queryset.order_by('-created_at')


class ApproveComplianceView(APIView):
    """Admin approves compliance document"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, compliance_id):
        compliance = get_object_or_404(ComplianceData, id=compliance_id)
        
        if compliance.status != 'PENDING':
            return Response(
                {'error': 'Document is not pending verification'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        compliance.approve(request.user)
        
        # Create notification
        JobNotification.objects.create(
            recipient=compliance.contractor.user,
            job=Job.objects.filter(assigned_to=compliance.contractor.user).first(),
            notification_type='JOB_VERIFIED',
            title=f'Compliance Document Approved',
            message=f'Your {compliance.get_compliance_type_display()} document has been approved.'
        )
        
        return Response({
            'message': 'Compliance document approved successfully',
            'compliance': ComplianceDataSerializer(compliance).data
        })


class RejectComplianceView(APIView):
    """Admin rejects compliance document"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, compliance_id):
        compliance = get_object_or_404(ComplianceData, id=compliance_id)
        
        if compliance.status != 'PENDING':
            return Response(
                {'error': 'Document is not pending verification'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        compliance.reject(request.user, rejection_reason)
        
        # Create notification
        JobNotification.objects.create(
            recipient=compliance.contractor.user,
            job=Job.objects.filter(assigned_to=compliance.contractor.user).first(),
            notification_type='REVISION_REQUIRED',
            title=f'Compliance Document Rejected',
            message=f'Your {compliance.get_compliance_type_display()} document has been rejected. Reason: {rejection_reason}'
        )
        
        return Response({
            'message': 'Compliance document rejected',
            'compliance': ComplianceDataSerializer(compliance).data
        })


class AdminComplianceStatsView(APIView):
    """Admin views compliance statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        total_documents = ComplianceData.objects.count()
        pending = ComplianceData.objects.filter(status='PENDING').count()
        approved = ComplianceData.objects.filter(status='APPROVED').count()
        rejected = ComplianceData.objects.filter(status='REJECTED').count()
        expiring_soon = ComplianceData.objects.filter(
            status='APPROVED',
            expiry_date__lte=timezone.now().date() + timezone.timedelta(days=30),
            expiry_date__gt=timezone.now().date()
        ).count()
        expired = ComplianceData.objects.filter(
            expiry_date__lt=timezone.now().date()
        ).count()
        
        # By type
        by_type = {}
        for choice in ComplianceData.ComplianceType.choices:
            by_type[choice[1]] = ComplianceData.objects.filter(compliance_type=choice[0]).count()
        
        return Response({
            'total_documents': total_documents,
            'pending_verification': pending,
            'approved': approved,
            'rejected': rejected,
            'expiring_soon': expiring_soon,
            'expired': expired,
            'by_type': by_type
        })


# ==================== Dispute Center ====================

class CreateDisputeView(generics.CreateAPIView):
    """Create a new dispute"""
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        job_id = self.request.data.get('job_id')
        job = get_object_or_404(Job, id=job_id)
        
        # Get contractor
        contractor = get_object_or_404(Contractor, user=job.assigned_to)
        
        # Generate dispute number
        count = Dispute.objects.count()
        dispute_number = f"DISP-{count + 1:06d}"
        
        serializer.save(
            dispute_number=dispute_number,
            raised_by=self.request.user,
            contractor=contractor
        )


class DisputeListView(generics.ListAPIView):
    """List disputes based on user role"""
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees all
        if user.role == 'ADMIN':
            queryset = Dispute.objects.all()
        # FM sees escalated to FM or Admin
        elif user.role == 'FM':
            queryset = Dispute.objects.filter(
                Q(status='ESCALATED_TO_FM') | Q(status='ESCALATED_TO_ADMIN')
            )
        # Contractor sees their disputes
        else:
            try:
                contractor = Contractor.objects.get(user=user)
                queryset = Dispute.objects.filter(contractor=contractor)
            except Contractor.DoesNotExist:
                # Customer sees disputes they raised
                queryset = Dispute.objects.filter(raised_by=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        return queryset.order_by('-created_at')


class DisputeDetailView(generics.RetrieveAPIView):
    """View dispute details"""
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Dispute.objects.all()


class EscalateDisputeToFMView(APIView):
    """Escalate dispute to FM"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, dispute_id):
        dispute = get_object_or_404(Dispute, id=dispute_id)
        
        if dispute.status != 'OPEN':
            return Response(
                {'error': 'Dispute can only be escalated from OPEN status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dispute.escalate_to_fm()
        
        # Notify FM
        JobNotification.objects.create(
            recipient=dispute.job.created_by,
            job=dispute.job,
            notification_type='REVISION_REQUIRED',
            title=f'Dispute Escalated: {dispute.dispute_number}',
            message=f'A dispute has been escalated to you for review: {dispute.title}'
        )
        
        return Response({
            'message': 'Dispute escalated to FM successfully',
            'dispute': DisputeSerializer(dispute).data
        })


class EscalateDisputeToAdminView(APIView):
    """Escalate dispute to Admin"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, dispute_id):
        dispute = get_object_or_404(Dispute, id=dispute_id)
        
        if dispute.status not in ['OPEN', 'ESCALATED_TO_FM']:
            return Response(
                {'error': 'Invalid dispute status for escalation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dispute.escalate_to_admin()
        
        return Response({
            'message': 'Dispute escalated to Admin successfully',
            'dispute': DisputeSerializer(dispute).data
        })


class ResolveDisputeView(APIView):
    """Admin resolves dispute"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, dispute_id):
        dispute = get_object_or_404(Dispute, id=dispute_id)
        
        resolution_notes = request.data.get('resolution_notes', '')
        dispute.resolve(request.user, resolution_notes)
        
        # Notify all parties
        JobNotification.objects.create(
            recipient=dispute.raised_by,
            job=dispute.job,
            notification_type='JOB_VERIFIED',
            title=f'Dispute Resolved: {dispute.dispute_number}',
            message=f'Your dispute has been resolved. Resolution: {resolution_notes}'
        )
        
        JobNotification.objects.create(
            recipient=dispute.contractor.user,
            job=dispute.job,
            notification_type='JOB_VERIFIED',
            title=f'Dispute Resolved: {dispute.dispute_number}',
            message=f'The dispute has been resolved. Resolution: {resolution_notes}'
        )
        
        return Response({
            'message': 'Dispute resolved successfully',
            'dispute': DisputeSerializer(dispute).data
        })


class AddDisputeMessageView(generics.CreateAPIView):
    """Add message to dispute"""
    serializer_class = DisputeMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class DisputeMessagesView(generics.ListAPIView):
    """List dispute messages"""
    serializer_class = DisputeMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        dispute_id = self.kwargs.get('dispute_id')
        user = self.request.user
        
        queryset = DisputeMessage.objects.filter(dispute_id=dispute_id)
        
        # Hide internal messages from non-admin/FM users
        if user.role not in ['ADMIN', 'FM']:
            queryset = queryset.filter(is_internal=False)
        
        return queryset.order_by('created_at')


class AddDisputeAttachmentView(generics.CreateAPIView):
    """Add attachment to dispute"""
    serializer_class = DisputeAttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class DisputeAttachmentsView(generics.ListAPIView):
    """List dispute attachments"""
    serializer_class = DisputeAttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        dispute_id = self.kwargs.get('dispute_id')
        return DisputeAttachment.objects.filter(dispute_id=dispute_id).order_by('-created_at')


class DisputeStatisticsView(APIView):
    """Admin views dispute statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        total_disputes = Dispute.objects.count()
        open_disputes = Dispute.objects.filter(status='OPEN').count()
        escalated_to_fm = Dispute.objects.filter(status='ESCALATED_TO_FM').count()
        escalated_to_admin = Dispute.objects.filter(status='ESCALATED_TO_ADMIN').count()
        resolved = Dispute.objects.filter(status='RESOLVED').count()
        closed = Dispute.objects.filter(status='CLOSED').count()
        
        # By category
        by_category = {}
        for choice in Dispute.DisputeCategory.choices:
            by_category[choice[1]] = Dispute.objects.filter(category=choice[0]).count()
        
        return Response({
            'total_disputes': total_disputes,
            'open': open_disputes,
            'escalated_to_fm': escalated_to_fm,
            'escalated_to_admin': escalated_to_admin,
            'resolved': resolved,
            'closed': closed,
            'by_category': by_category
        })
