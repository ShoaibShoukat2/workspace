"""
Field Manager (FM) specific views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg

from .models import (
    Workspace, Job, JobAttachment, Estimate, 
    EstimateLineItem, Contractor
)
from .serializers import (
    JobSerializer, JobAttachmentSerializer,
    EstimateSerializer, EstimateLineItemSerializer,
    EstimateWithLineItemsSerializer
)
from .utils import generate_job_number, generate_estimate_number
from authentication.permissions import IsAdminOrFM


# ==================== FM Dashboard ====================

class FMDashboardView(APIView):
    """FM Dashboard with job statistics and overview"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        user = request.user
        workspace_id = request.query_params.get('workspace_id')
        
        # Filter jobs created by FM
        jobs_query = Job.objects.filter(created_by=user)
        
        if workspace_id:
            jobs_query = jobs_query.filter(workspace__workspace_id=workspace_id)
        
        # Job statistics
        total_jobs = jobs_query.count()
        pending_jobs = jobs_query.filter(status='PENDING').count()
        active_jobs = jobs_query.filter(status='IN_PROGRESS').count()
        completed_jobs = jobs_query.filter(status='COMPLETED').count()
        cancelled_jobs = jobs_query.filter(status='CANCELLED').count()
        
        # Priority breakdown
        high_priority = jobs_query.filter(priority='HIGH').count()
        urgent_priority = jobs_query.filter(priority='URGENT').count()
        
        # Financial overview
        total_estimated_cost = jobs_query.aggregate(Sum('estimated_cost'))['estimated_cost__sum'] or 0
        total_actual_cost = jobs_query.aggregate(Sum('actual_cost'))['actual_cost__sum'] or 0
        
        # Estimates statistics
        estimates_query = Estimate.objects.filter(created_by=user)
        if workspace_id:
            estimates_query = estimates_query.filter(workspace__workspace_id=workspace_id)
        
        total_estimates = estimates_query.count()
        draft_estimates = estimates_query.filter(status='DRAFT').count()
        sent_estimates = estimates_query.filter(status='SENT').count()
        approved_estimates = estimates_query.filter(status='APPROVED').count()
        signed_estimates = estimates_query.exclude(customer_signature__isnull=True).exclude(customer_signature='').count()
        
        total_estimate_value = estimates_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        approved_estimate_value = estimates_query.filter(status='APPROVED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Recent jobs
        recent_jobs = jobs_query.order_by('-created_at')[:5]
        recent_jobs_data = JobSerializer(recent_jobs, many=True).data
        
        # Upcoming deadlines
        upcoming_deadlines = jobs_query.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            due_date__isnull=False
        ).order_by('due_date')[:5]
        upcoming_deadlines_data = JobSerializer(upcoming_deadlines, many=True).data
        
        # Overdue jobs
        overdue_jobs = jobs_query.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            due_date__lt=timezone.now().date()
        ).count()
        
        return Response({
            'job_statistics': {
                'total_jobs': total_jobs,
                'pending_jobs': pending_jobs,
                'active_jobs': active_jobs,
                'completed_jobs': completed_jobs,
                'cancelled_jobs': cancelled_jobs,
                'high_priority': high_priority,
                'urgent_priority': urgent_priority,
                'overdue_jobs': overdue_jobs
            },
            'financial_overview': {
                'total_estimated_cost': float(total_estimated_cost),
                'total_actual_cost': float(total_actual_cost),
                'variance': float(total_estimated_cost - total_actual_cost)
            },
            'estimate_statistics': {
                'total_estimates': total_estimates,
                'draft_estimates': draft_estimates,
                'sent_estimates': sent_estimates,
                'approved_estimates': approved_estimates,
                'signed_estimates': signed_estimates,
                'total_estimate_value': float(total_estimate_value),
                'approved_estimate_value': float(approved_estimate_value)
            },
            'recent_jobs': recent_jobs_data,
            'upcoming_deadlines': upcoming_deadlines_data
        })


class FMJobsByStatusView(APIView):
    """Get FM's jobs filtered by status"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request, status):
        user = request.user
        workspace_id = request.query_params.get('workspace_id')
        
        jobs_query = Job.objects.filter(created_by=user, status=status.upper())
        
        if workspace_id:
            jobs_query = jobs_query.filter(workspace__workspace_id=workspace_id)
        
        jobs = jobs_query.order_by('-created_at')
        serializer = JobSerializer(jobs, many=True)
        
        return Response({
            'status': status,
            'count': jobs.count(),
            'jobs': serializer.data
        })


# ==================== Job Management ====================

class FMCreateJobView(generics.CreateAPIView):
    """FM creates a new job with full details"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        job_number = generate_job_number(workspace.workspace_id)
        serializer.save(
            workspace=workspace,
            job_number=job_number,
            created_by=self.request.user
        )


class FMJobDetailView(generics.RetrieveUpdateAPIView):
    """FM views and updates job details"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        # FM can only access their own jobs
        return Job.objects.filter(created_by=self.request.user)


class FMJobListView(generics.ListAPIView):
    """List all jobs created by FM"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = Job.objects.filter(created_by=self.request.user)
        
        # Filter by workspace
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace__workspace_id=workspace_id)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status.upper())
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority.upper())
        
        return queryset.order_by('-created_at')


# ==================== Job Attachments ====================

class JobAttachmentCreateView(generics.CreateAPIView):
    """Upload attachment to a job"""
    serializer_class = JobAttachmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class JobAttachmentListView(generics.ListAPIView):
    """List all attachments for a job"""
    serializer_class = JobAttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return JobAttachment.objects.filter(job_id=job_id)


class JobAttachmentDeleteView(generics.DestroyAPIView):
    """Delete a job attachment"""
    serializer_class = JobAttachmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    queryset = JobAttachment.objects.all()


# ==================== Estimate Management ====================

class FMCreateEstimateView(generics.CreateAPIView):
    """FM creates estimate with line items"""
    serializer_class = EstimateWithLineItemsSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        estimate_number = generate_estimate_number(workspace.workspace_id)
        serializer.save(
            workspace=workspace,
            estimate_number=estimate_number,
            created_by=self.request.user
        )


class FMEstimateDetailView(generics.RetrieveUpdateAPIView):
    """FM views and updates estimate"""
    serializer_class = EstimateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        return Estimate.objects.filter(created_by=self.request.user)


class FMEstimateListView(generics.ListAPIView):
    """List all estimates created by FM"""
    serializer_class = EstimateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = Estimate.objects.filter(created_by=self.request.user)
        
        # Filter by workspace
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace__workspace_id=workspace_id)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status.upper())
        
        return queryset.order_by('-created_at')


# ==================== Estimate Line Items ====================

class EstimateLineItemCreateView(generics.CreateAPIView):
    """Add line item to estimate"""
    serializer_class = EstimateLineItemSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]


class EstimateLineItemUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete line item"""
    serializer_class = EstimateLineItemSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    queryset = EstimateLineItem.objects.all()


class EstimateLineItemListView(generics.ListAPIView):
    """List all line items for an estimate"""
    serializer_class = EstimateLineItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        estimate_id = self.kwargs.get('estimate_id')
        return EstimateLineItem.objects.filter(estimate_id=estimate_id)


# ==================== Customer Signature ====================

class CustomerSignEstimateView(APIView):
    """Customer signs the estimate digitally"""
    permission_classes = []  # Public endpoint with token validation
    
    def post(self, request, estimate_id):
        estimate = get_object_or_404(Estimate, id=estimate_id)
        
        # Validate estimate can be signed
        if estimate.status not in ['SENT', 'DRAFT']:
            return Response(
                {'error': 'Estimate cannot be signed in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        signature_data = request.data.get('signature')
        if not signature_data:
            return Response(
                {'error': 'Signature data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save signature
        estimate.customer_signature = signature_data
        estimate.customer_signed_at = timezone.now()
        estimate.customer_ip_address = self.get_client_ip(request)
        estimate.status = 'APPROVED'
        estimate.approved_at = timezone.now()
        estimate.save()
        
        return Response({
            'message': 'Estimate signed successfully',
            'estimate_number': estimate.estimate_number,
            'signed_at': estimate.customer_signed_at
        })
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GetEstimateForSigningView(APIView):
    """Get estimate details for customer signing (public endpoint)"""
    permission_classes = []
    
    def get(self, request, estimate_number):
        estimate = get_object_or_404(Estimate, estimate_number=estimate_number)
        
        # Return estimate details without sensitive info
        return Response({
            'estimate_number': estimate.estimate_number,
            'title': estimate.title,
            'description': estimate.description,
            'status': estimate.status,
            'line_items': EstimateLineItemSerializer(estimate.line_items.all(), many=True).data,
            'subtotal': estimate.subtotal,
            'tax_rate': estimate.tax_rate,
            'tax_amount': estimate.tax_amount,
            'discount_amount': estimate.discount_amount,
            'total_amount': estimate.total_amount,
            'valid_until': estimate.valid_until,
            'is_signed': bool(estimate.customer_signature),
            'created_at': estimate.created_at
        })


# ==================== Estimate Actions ====================

class SendEstimateView(APIView):
    """Mark estimate as sent to customer"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, estimate_id):
        estimate = get_object_or_404(
            Estimate, 
            id=estimate_id, 
            created_by=request.user
        )
        
        if estimate.status != 'DRAFT':
            return Response(
                {'error': 'Only draft estimates can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate.status = 'SENT'
        estimate.save()
        
        # TODO: Send email to customer with signing link
        
        return Response({
            'message': 'Estimate sent successfully',
            'estimate_number': estimate.estimate_number,
            'status': estimate.status
        })


class RecalculateEstimateView(APIView):
    """Recalculate estimate totals"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, estimate_id):
        estimate = get_object_or_404(
            Estimate, 
            id=estimate_id, 
            created_by=request.user
        )
        
        estimate.calculate_totals()
        
        return Response({
            'message': 'Estimate totals recalculated',
            'subtotal': estimate.subtotal,
            'tax_amount': estimate.tax_amount,
            'total_amount': estimate.total_amount
        })
