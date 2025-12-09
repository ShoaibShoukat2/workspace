from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum

from .models import (
    Workspace, WorkspaceMember, Job, Estimate,
    Contractor, Payout, Report, ComplianceData
)
from .serializers import (
    WorkspaceSerializer, WorkspaceMemberSerializer, JobSerializer,
    EstimateSerializer, ContractorSerializer, PayoutSerializer,
    ReportSerializer, ComplianceDataSerializer
)
from .utils import (
    generate_job_number, generate_estimate_number, generate_payout_number,
    export_jobs_to_csv, export_estimates_to_csv, export_contractors_to_csv,
    export_payouts_to_csv, export_compliance_to_csv, create_csv_response
)
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== Workspace Views ====================

class WorkspaceListCreateView(generics.ListCreateAPIView):
    """List all workspaces or create new workspace"""
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'workspace_type']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Workspace.objects.all()
        return Workspace.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        # Add owner as workspace member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=self.request.user,
            role=WorkspaceMember.MemberRole.OWNER
        )


class WorkspaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete workspace"""
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Workspace.objects.all()
        return Workspace.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct()


class WorkspaceStatsView(APIView):
    """Get workspace statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Check permission
        if not (workspace.owner == request.user or 
                workspace.members.filter(user=request.user).exists() or
                request.user.role == 'ADMIN'):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_jobs': workspace.jobs.count(),
            'pending_jobs': workspace.jobs.filter(status='PENDING').count(),
            'in_progress_jobs': workspace.jobs.filter(status='IN_PROGRESS').count(),
            'completed_jobs': workspace.jobs.filter(status='COMPLETED').count(),
            'total_estimates': workspace.estimates.count(),
            'approved_estimates': workspace.estimates.filter(status='APPROVED').count(),
            'total_contractors': workspace.contractors.count(),
            'active_contractors': workspace.contractors.filter(status='ACTIVE').count(),
            'total_payouts': workspace.payouts.aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_payouts': workspace.payouts.filter(status='PENDING').count(),
            'compliance_expired': workspace.compliance_data.filter(status='EXPIRED').count(),
            'compliance_expiring_soon': workspace.compliance_data.filter(status='EXPIRING_SOON').count(),
        }
        
        return Response(stats)


# ==================== Workspace Member Views ====================

class WorkspaceMemberListView(generics.ListCreateAPIView):
    """List or add workspace members"""
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return WorkspaceMember.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        serializer.save(workspace=workspace)


class WorkspaceMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or remove workspace member"""
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkspaceMember.objects.all()


# ==================== Job Views ====================

class JobListCreateView(generics.ListCreateAPIView):
    """List or create jobs"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['job_number', 'title', 'status']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return Job.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        job_number = generate_job_number(workspace.workspace_id)
        serializer.save(
            workspace=workspace,
            job_number=job_number,
            created_by=self.request.user
        )


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete job"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()


class JobExportCSVView(APIView):
    """Export jobs to CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        jobs = Job.objects.filter(workspace=workspace)
        
        csv_content = export_jobs_to_csv(jobs)
        filename = f"jobs_{workspace.name}_{timezone.now().strftime('%Y%m%d')}.csv"
        
        return create_csv_response(csv_content, filename)


# ==================== Estimate Views ====================

class EstimateListCreateView(generics.ListCreateAPIView):
    """List or create estimates"""
    serializer_class = EstimateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['estimate_number', 'title', 'status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return Estimate.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        estimate_number = generate_estimate_number(workspace.workspace_id)
        serializer.save(
            workspace=workspace,
            estimate_number=estimate_number,
            created_by=self.request.user
        )


class EstimateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete estimate"""
    serializer_class = EstimateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Estimate.objects.all()


class EstimateExportCSVView(APIView):
    """Export estimates to CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        estimates = Estimate.objects.filter(workspace=workspace)
        
        csv_content = export_estimates_to_csv(estimates)
        filename = f"estimates_{workspace.name}_{timezone.now().strftime('%Y%m%d')}.csv"
        
        return create_csv_response(csv_content, filename)


# ==================== Contractor Views ====================

class ContractorListCreateView(generics.ListCreateAPIView):
    """List or create contractors"""
    serializer_class = ContractorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'company_name', 'specialization']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return Contractor.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        serializer.save(workspace=workspace)


class ContractorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete contractor"""
    serializer_class = ContractorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contractor.objects.all()


class ContractorExportCSVView(APIView):
    """Export contractors to CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        contractors = Contractor.objects.filter(workspace=workspace)
        
        csv_content = export_contractors_to_csv(contractors)
        filename = f"contractors_{workspace.name}_{timezone.now().strftime('%Y%m%d')}.csv"
        
        return create_csv_response(csv_content, filename)


# ==================== Payout Views ====================

class PayoutListCreateView(generics.ListCreateAPIView):
    """List or create payouts"""
    serializer_class = PayoutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['payout_number', 'contractor__user__email', 'status']
    ordering_fields = ['created_at', 'amount', 'scheduled_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return Payout.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        payout_number = generate_payout_number(workspace.workspace_id)
        serializer.save(
            workspace=workspace,
            payout_number=payout_number
        )


class PayoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete payout"""
    serializer_class = PayoutSerializer
    permission_classes = [IsAuthenticated]
    queryset = Payout.objects.all()


class PayoutExportCSVView(APIView):
    """Export payouts to CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        payouts = Payout.objects.filter(workspace=workspace)
        
        csv_content = export_payouts_to_csv(payouts)
        filename = f"payouts_{workspace.name}_{timezone.now().strftime('%Y%m%d')}.csv"
        
        return create_csv_response(csv_content, filename)


# ==================== Report Views ====================

class ReportListCreateView(generics.ListCreateAPIView):
    """List or create reports"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'report_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return Report.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        serializer.save(
            workspace=workspace,
            generated_by=self.request.user
        )


class ReportDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete report"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    queryset = Report.objects.all()


# ==================== Compliance Views ====================

class ComplianceListCreateView(generics.ListCreateAPIView):
    """List or create compliance data"""
    serializer_class = ComplianceDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['contractor__user__email', 'compliance_type', 'document_name']
    ordering_fields = ['created_at', 'expiry_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return ComplianceData.objects.filter(workspace__workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        serializer.save(workspace=workspace)


class ComplianceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete compliance data"""
    serializer_class = ComplianceDataSerializer
    permission_classes = [IsAuthenticated]
    queryset = ComplianceData.objects.all()


class ComplianceExportCSVView(APIView):
    """Export compliance data to CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        compliance_data = ComplianceData.objects.filter(workspace=workspace)
        
        csv_content = export_compliance_to_csv(compliance_data)
        filename = f"compliance_{workspace.name}_{timezone.now().strftime('%Y%m%d')}.csv"
        
        return create_csv_response(csv_content, filename)


class ComplianceExpiringView(APIView):
    """Get expiring or expired compliance documents"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        expiring_soon = []
        expired = []
        
        for compliance in workspace.compliance_data.all():
            if compliance.is_expired:
                expired.append(ComplianceDataSerializer(compliance).data)
            elif compliance.is_expiring_soon:
                expiring_soon.append(ComplianceDataSerializer(compliance).data)
        
        return Response({
            'expiring_soon': expiring_soon,
            'expired': expired
        })
