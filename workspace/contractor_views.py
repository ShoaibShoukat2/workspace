"""
Contractor Module Views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg

from .models import (
    Job, JobAssignment, JobChecklist, ChecklistStep, StepMedia,
    JobCompletion, JobNotification, Contractor, SupportTicket
)
from .serializers import (
    JobAssignmentSerializer, JobChecklistSerializer, ChecklistStepSerializer,
    StepMediaSerializer, JobCompletionSerializer, JobNotificationSerializer,
    ContractorJobDetailSerializer
)
from authentication.permissions import IsContractor
from authentication.permissions import IsAdminOrFM


# ==================== Contractor Dashboard ====================

class ContractorDashboardView(APIView):
    """Contractor dashboard with job statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get contractor profile
        try:
            contractor = Contractor.objects.get(user=user)
        except Contractor.DoesNotExist:
            return Response(
                {'error': 'Contractor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Job assignments statistics
        total_assignments = JobAssignment.objects.filter(contractor=contractor).count()
        pending_assignments = JobAssignment.objects.filter(
            contractor=contractor,
            status='PENDING'
        ).count()
        accepted_assignments = JobAssignment.objects.filter(
            contractor=contractor,
            status='ACCEPTED'
        ).count()
        rejected_assignments = JobAssignment.objects.filter(
            contractor=contractor,
            status='REJECTED'
        ).count()
        
        # Active jobs (accepted and in progress)
        active_jobs = Job.objects.filter(
            assignments__contractor=contractor,
            assignments__status='ACCEPTED',
            status='IN_PROGRESS'
        ).count()
        
        # Completed jobs
        completed_jobs = JobCompletion.objects.filter(
            contractor=contractor,
            status='APPROVED'
        ).count()
        
        # Jobs pending verification
        pending_verification = JobCompletion.objects.filter(
            contractor=contractor,
            status__in=['SUBMITTED', 'UNDER_REVIEW']
        ).count()
        
        # Average ratings
        ratings = JobCompletion.objects.filter(
            contractor=contractor,
            overall_rating__isnull=False
        ).aggregate(
            avg_quality=Avg('quality_rating'),
            avg_timeliness=Avg('timeliness_rating'),
            avg_professionalism=Avg('professionalism_rating'),
            avg_overall=Avg('overall_rating')
        )
        
        # Unread notifications
        unread_notifications = JobNotification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        # Recent assignments
        recent_assignments = JobAssignment.objects.filter(
            contractor=contractor
        ).order_by('-assigned_at')[:5]
        
        return Response({
            'contractor_info': {
                'company_name': contractor.company_name,
                'specialization': contractor.specialization,
                'rating': float(contractor.rating) if contractor.rating else None,
                'total_jobs_completed': contractor.total_jobs_completed
            },
            'assignment_statistics': {
                'total_assignments': total_assignments,
                'pending_assignments': pending_assignments,
                'accepted_assignments': accepted_assignments,
                'rejected_assignments': rejected_assignments,
                'active_jobs': active_jobs,
                'completed_jobs': completed_jobs,
                'pending_verification': pending_verification
            },
            'ratings': {
                'average_quality': float(ratings['avg_quality']) if ratings['avg_quality'] else None,
                'average_timeliness': float(ratings['avg_timeliness']) if ratings['avg_timeliness'] else None,
                'average_professionalism': float(ratings['avg_professionalism']) if ratings['avg_professionalism'] else None,
                'average_overall': float(ratings['avg_overall']) if ratings['avg_overall'] else None
            },
            'unread_notifications': unread_notifications,
            'recent_assignments': JobAssignmentSerializer(recent_assignments, many=True).data
        })


# ==================== Job Assignments ====================

class ContractorAssignmentsView(generics.ListAPIView):
    """List all job assignments for contractor"""
    serializer_class = JobAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        contractor = get_object_or_404(Contractor, user=user)
        
        queryset = JobAssignment.objects.filter(contractor=contractor)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        return queryset.order_by('-assigned_at')


class AcceptJobView(APIView):
    """Contractor accepts a job assignment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, assignment_id):
        contractor = get_object_or_404(Contractor, user=request.user)
        assignment = get_object_or_404(
            JobAssignment,
            id=assignment_id,
            contractor=contractor,
            status='PENDING'
        )
        
        # Accept assignment
        assignment.status = 'ACCEPTED'
        assignment.responded_at = timezone.now()
        assignment.save()
        
        # Update job status
        job = assignment.job
        job.status = 'IN_PROGRESS'
        job.assigned_to = request.user
        job.save()
        
        # Create notification for FM/Admin
        JobNotification.objects.create(
            recipient=job.created_by,
            job=job,
            notification_type='JOB_ACCEPTED',
            title=f'Job Accepted: {job.job_number}',
            message=f'{contractor.user.email} has accepted the job assignment.'
        )
        
        return Response({
            'message': 'Job accepted successfully',
            'assignment': JobAssignmentSerializer(assignment).data
        })


class RejectJobView(APIView):
    """Contractor rejects a job assignment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, assignment_id):
        contractor = get_object_or_404(Contractor, user=request.user)
        assignment = get_object_or_404(
            JobAssignment,
            id=assignment_id,
            contractor=contractor,
            status='PENDING'
        )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Reject assignment
        assignment.status = 'REJECTED'
        assignment.responded_at = timezone.now()
        assignment.rejection_reason = rejection_reason
        assignment.save()
        
        # Create notification for FM/Admin
        JobNotification.objects.create(
            recipient=assignment.job.created_by,
            job=assignment.job,
            notification_type='JOB_REJECTED',
            title=f'Job Rejected: {assignment.job.job_number}',
            message=f'{contractor.user.email} has rejected the job assignment. Reason: {rejection_reason}'
        )
        
        return Response({
            'message': 'Job rejected successfully',
            'assignment': JobAssignmentSerializer(assignment).data
        })


# ==================== Active Jobs ====================

class ContractorActiveJobsView(generics.ListAPIView):
    """List contractor's active jobs"""
    serializer_class = ContractorJobDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        
        return Job.objects.filter(
            assignments__contractor=contractor,
            assignments__status='ACCEPTED',
            status='IN_PROGRESS'
        ).distinct().order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        contractor = get_object_or_404(Contractor, user=self.request.user)
        context['contractor'] = contractor
        return context


class ContractorJobDetailView(generics.RetrieveAPIView):
    """Get detailed job information for contractor"""
    serializer_class = ContractorJobDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        return Job.objects.filter(
            assignments__contractor=contractor,
            assignments__status='ACCEPTED'
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        contractor = get_object_or_404(Contractor, user=self.request.user)
        context['contractor'] = contractor
        return context


# ==================== Checklist Management ====================

class ChecklistStepUpdateView(APIView):
    """Update checklist step (mark complete, add notes)"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, step_id):
        step = get_object_or_404(ChecklistStep, id=step_id)
        
        # Verify contractor has access to this job
        contractor = get_object_or_404(Contractor, user=request.user)
        if not step.checklist.job.assignments.filter(
            contractor=contractor,
            status='ACCEPTED'
        ).exists():
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update step
        is_completed = request.data.get('is_completed')
        notes = request.data.get('notes')
        
        if is_completed is not None:
            if is_completed and not step.is_completed:
                step.mark_complete(request.user)
                
                # Create notification
                JobNotification.objects.create(
                    recipient=step.checklist.job.created_by,
                    job=step.checklist.job,
                    notification_type='STEP_COMPLETED',
                    title=f'Step Completed: {step.title}',
                    message=f'Contractor has completed step {step.step_number} in {step.checklist.title}'
                )
            elif not is_completed:
                step.is_completed = False
                step.completed_by = None
                step.completed_at = None
                step.save()
        
        if notes is not None:
            step.notes = notes
            step.save()
        
        return Response({
            'message': 'Step updated successfully',
            'step': ChecklistStepSerializer(step).data
        })


class UploadStepMediaView(generics.CreateAPIView):
    """Upload photo/video for a checklist step"""
    serializer_class = StepMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        step_id = self.request.data.get('step')
        step = get_object_or_404(ChecklistStep, id=step_id)
        
        # Verify contractor has access
        contractor = get_object_or_404(Contractor, user=self.request.user)
        if not step.checklist.job.assignments.filter(
            contractor=contractor,
            status='ACCEPTED'
        ).exists():
            raise PermissionError('Access denied')
        
        serializer.save(uploaded_by=self.request.user)


class StepMediaListView(generics.ListAPIView):
    """List all media for a step"""
    serializer_class = StepMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        step_id = self.kwargs.get('step_id')
        return StepMedia.objects.filter(step_id=step_id)


class DeleteStepMediaView(generics.DestroyAPIView):
    """Delete step media"""
    serializer_class = StepMediaSerializer
    permission_classes = [IsAuthenticated]
    queryset = StepMedia.objects.all()


# ==================== Job Completion ====================

class SubmitJobCompletionView(APIView):
    """Contractor submits job as completed"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, job_id):
        contractor = get_object_or_404(Contractor, user=request.user)
        job = get_object_or_404(Job, id=job_id)
        
        # Verify contractor is assigned to this job
        if not job.assignments.filter(
            contractor=contractor,
            status='ACCEPTED'
        ).exists():
            return Response(
                {'error': 'You are not assigned to this job'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already submitted
        if hasattr(job, 'completion'):
            return Response(
                {'error': 'Job completion already submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if all required checklist steps are completed
        incomplete_steps = ChecklistStep.objects.filter(
            checklist__job=job,
            is_required=True,
            is_completed=False
        )
        
        if incomplete_steps.exists():
            return Response({
                'error': 'All required checklist steps must be completed',
                'incomplete_steps': ChecklistStepSerializer(incomplete_steps, many=True).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create completion record
        completion = JobCompletion.objects.create(
            job=job,
            contractor=contractor,
            completion_notes=request.data.get('completion_notes', ''),
            actual_hours_worked=request.data.get('actual_hours_worked'),
            status='SUBMITTED'
        )
        
        # Update job status
        job.status = 'COMPLETED'
        job.completed_date = timezone.now().date()
        job.save()
        
        # Create notifications for FM and Admin
        JobNotification.objects.create(
            recipient=job.created_by,
            job=job,
            notification_type='JOB_COMPLETED',
            title=f'Job Completed: {job.job_number}',
            message=f'{contractor.user.email} has submitted the job as completed and is awaiting verification.'
        )
        
        return Response({
            'message': 'Job submitted for verification successfully',
            'completion': JobCompletionSerializer(completion).data
        }, status=status.HTTP_201_CREATED)


class ContractorCompletedJobsView(generics.ListAPIView):
    """List contractor's completed jobs"""
    serializer_class = JobCompletionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        return JobCompletion.objects.filter(contractor=contractor).order_by('-submitted_at')


# ==================== Notifications ====================

class ContractorNotificationsView(generics.ListAPIView):
    """List contractor's notifications"""
    serializer_class = JobNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = JobNotification.objects.filter(recipient=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')


class MarkNotificationReadView(APIView):
    """Mark notification as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        notification = get_object_or_404(
            JobNotification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read',
            'notification': JobNotificationSerializer(notification).data
        })


class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        JobNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': 'All notifications marked as read'
        })


# ==================== Contractor Support Access ====================

class ContractorSupportInfoView(APIView):
    """Get support information for contractor dashboard"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def get(self, request):
        contractor = get_object_or_404(Contractor, user=request.user)
        
        # Get recent support tickets
        recent_tickets = SupportTicket.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        # Count open tickets
        open_tickets_count = SupportTicket.objects.filter(
            user=request.user,
            status__in=['OPEN', 'IN_PROGRESS']
        ).count()
        
        return Response({
            'support_available': True,
            'open_tickets_count': open_tickets_count,
            'recent_tickets': [{
                'ticket_number': ticket.ticket_number,
                'subject': ticket.subject,
                'status': ticket.status,
                'created_at': ticket.created_at
            } for ticket in recent_tickets],
            'support_channels': {
                'automated_support': True,
                'faq_available': True,
                'guided_help': True,
                'human_chat': True,  # This would integrate with Zendesk/FreshDesk/Intercom
                'email_support': True
            }
        })


# ==================== Admin/FM Views for Contractor Module ====================

class AssignJobToContractorView(APIView):
    """FM/Admin assigns job to contractor"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        job_id = request.data.get('job_id')
        contractor_id = request.data.get('contractor_id')
        notes = request.data.get('notes', '')
        
        job = get_object_or_404(Job, id=job_id)
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        # Check if already assigned
        existing_assignment = JobAssignment.objects.filter(
            job=job,
            contractor=contractor,
            status__in=['PENDING', 'ACCEPTED']
        ).first()
        
        if existing_assignment:
            return Response(
                {'error': 'Job already assigned to this contractor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create assignment
        assignment = JobAssignment.objects.create(
            job=job,
            contractor=contractor,
            assigned_by=request.user,
            notes=notes
        )
        
        # Create notification for contractor
        JobNotification.objects.create(
            recipient=contractor.user,
            job=job,
            notification_type='JOB_ASSIGNED',
            title=f'New Job Assignment: {job.job_number}',
            message=f'You have been assigned a new job: {job.title}. Please review and accept/reject.'
        )
        
        return Response({
            'message': 'Job assigned successfully',
            'assignment': JobAssignmentSerializer(assignment).data
        }, status=status.HTTP_201_CREATED)


class VerifyJobCompletionView(APIView):
    """FM/Admin verifies job completion"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, completion_id):
        completion = get_object_or_404(JobCompletion, id=completion_id)
        
        action = request.data.get('action')  # 'approve', 'reject', 'request_revision'
        verification_notes = request.data.get('verification_notes', '')
        
        if action == 'approve':
            completion.status = 'APPROVED'
            completion.verified_by = request.user
            completion.verified_at = timezone.now()
            completion.verification_notes = verification_notes
            
            # Update ratings if provided
            if 'quality_rating' in request.data:
                completion.quality_rating = request.data['quality_rating']
            if 'timeliness_rating' in request.data:
                completion.timeliness_rating = request.data['timeliness_rating']
            if 'professionalism_rating' in request.data:
                completion.professionalism_rating = request.data['professionalism_rating']
            
            completion.calculate_overall_rating()
            completion.save()
            
            # Update contractor stats
            contractor = completion.contractor
            contractor.total_jobs_completed += 1
            
            # Update contractor rating
            avg_rating = JobCompletion.objects.filter(
                contractor=contractor,
                overall_rating__isnull=False
            ).aggregate(Avg('overall_rating'))['overall_rating__avg']
            
            if avg_rating:
                contractor.rating = avg_rating
            
            contractor.save()
            
            notification_type = 'JOB_VERIFIED'
            message = f'Your job completion has been approved. Great work!'
            
        elif action == 'reject':
            completion.status = 'REJECTED'
            completion.verified_by = request.user
            completion.verified_at = timezone.now()
            completion.verification_notes = verification_notes
            completion.save()
            
            notification_type = 'JOB_VERIFIED'
            message = f'Your job completion has been rejected. Reason: {verification_notes}'
            
        elif action == 'request_revision':
            completion.status = 'REVISION_REQUIRED'
            completion.verification_notes = verification_notes
            completion.save()
            
            # Update job status back to in progress
            completion.job.status = 'IN_PROGRESS'
            completion.job.save()
            
            notification_type = 'REVISION_REQUIRED'
            message = f'Revision required for job completion. Details: {verification_notes}'
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification for contractor
        JobNotification.objects.create(
            recipient=completion.contractor.user,
            job=completion.job,
            notification_type=notification_type,
            title=f'Job Verification: {completion.job.job_number}',
            message=message
        )
        
        # Auto-create payout eligibility if approved
        if action == 'approve':
            from .payout_views import create_payout_eligibility_on_verification
            create_payout_eligibility_on_verification(completion)
        
        return Response({
            'message': f'Job completion {action}d successfully',
            'completion': JobCompletionSerializer(completion).data
        })


class CreateJobChecklistView(generics.CreateAPIView):
    """FM/Admin creates checklist for a job"""
    serializer_class = JobChecklistSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CreateChecklistStepView(generics.CreateAPIView):
    """FM/Admin creates checklist step"""
    serializer_class = ChecklistStepSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
