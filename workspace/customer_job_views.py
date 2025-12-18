"""
Customer Job Experience Views
Timeline, checkpoints, and material management
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import (
    Job, JobCheckpoint, JobPhoto, JobQuote, JobChecklist,
    MaterialSuggestion, CustomerProfile
)
from .serializers import (
    CustomerJobSerializer, JobCheckpointSerializer, JobPhotoSerializer,
    JobQuoteSerializer, MaterialSuggestionSerializer
)
from authentication.permissions import IsCustomer


# ==================== Customer Job Timeline ====================

class CustomerJobTimelineView(APIView):
    """C1. Job Timeline (Main Screen)"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        # Verify customer owns this job
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        # Build timeline steps
        steps = self._build_timeline_steps(job)
        
        return Response({
            'job': {
                'id': job.id,
                'status': job.status,
                'address': job.customer_address,
                'brandName': job.brand_name,
                'poweredBy': job.powered_by
            },
            'steps': steps
        })
    
    def _build_timeline_steps(self, job):
        """Build timeline steps based on job status and checkpoints"""
        steps = []
        
        # Step 1: Evaluation Scheduled
        steps.append({
            'type': 'evaluation_scheduled',
            'status': 'done' if job.status != 'LEAD' else 'pending',
            'timestamp': job.scheduled_evaluation_at.isoformat() if job.scheduled_evaluation_at else None
        })
        
        # Step 2: Walkthrough Completed
        steps.append({
            'type': 'walkthrough_completed',
            'status': 'done' if job.status in [
                'EVALUATION_COMPLETED', 'AWAITING_PRE_START_APPROVAL', 
                'IN_PROGRESS', 'MID_CHECKPOINT_PENDING', 
                'AWAITING_FINAL_APPROVAL', 'COMPLETED'
            ] else 'waiting',
            'timestamp': job.evaluation.submitted_at.isoformat() if hasattr(job, 'evaluation') and job.evaluation.submitted_at else None
        })
        
        # Step 3: Pre-Start Verification
        pre_start_checkpoint = job.checkpoints.filter(checkpoint_type='PRE_START').first()
        if pre_start_checkpoint:
            steps.append({
                'type': 'pre_start_verification',
                'status': 'done' if pre_start_checkpoint.status == 'APPROVED' else 'pending',
                'timestamp': pre_start_checkpoint.approved_at.isoformat() if pre_start_checkpoint.approved_at else None
            })
        else:
            steps.append({
                'type': 'pre_start_verification',
                'status': 'waiting'
            })
        
        # Step 4: In Progress
        steps.append({
            'type': 'in_progress',
            'status': 'done' if job.status in [
                'IN_PROGRESS', 'MID_CHECKPOINT_PENDING', 
                'AWAITING_FINAL_APPROVAL', 'COMPLETED'
            ] else 'waiting'
        })
        
        # Step 5: Mid-Project Checkpoint (if applicable)
        mid_checkpoint = job.checkpoints.filter(checkpoint_type='MID_PROJECT').first()
        if mid_checkpoint:
            steps.append({
                'type': 'mid_project_checkpoint',
                'status': 'done' if mid_checkpoint.status == 'APPROVED' else 'pending',
                'timestamp': mid_checkpoint.approved_at.isoformat() if mid_checkpoint.approved_at else None
            })
        else:
            steps.append({
                'type': 'mid_project_checkpoint',
                'status': 'not_applicable'
            })
        
        # Step 6: Final Verification
        final_checkpoint = job.checkpoints.filter(checkpoint_type='FINAL').first()
        if final_checkpoint:
            steps.append({
                'type': 'final_verification',
                'status': 'done' if final_checkpoint.status == 'APPROVED' else 'pending',
                'timestamp': final_checkpoint.approved_at.isoformat() if final_checkpoint.approved_at else None
            })
        else:
            steps.append({
                'type': 'final_verification',
                'status': 'waiting'
            })
        
        return steps


# ==================== Pre-Start Verification ====================

class CustomerPreStartCheckpointView(APIView):
    """C2. Pre-Start Verification Screen"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='PRE_START'
        )
        
        # Get quote
        quote = job.quotes.first()
        
        # Get before photos
        before_photos = job.photos.filter(photo_type='BEFORE')
        
        # Get materials assumptions
        materials = MaterialSuggestion.objects.filter(job=job)
        
        return Response({
            'checkpointId': checkpoint.id,
            'status': checkpoint.status,
            'scopeSummary': checkpoint.scope_summary,
            'materialsAssumptions': [
                {
                    'itemName': m.item_name,
                    'quantity': float(m.suggested_qty),
                    'unit': m.unit,
                    'priceRange': m.price_range
                }
                for m in materials
            ],
            'pricing': {
                'quoteId': quote.quote_id if quote else None,
                'gbbTotal': float(quote.gbb_total) if quote else 0,
                'evaluationFee': float(quote.evaluation_fee) if quote else 0,
                'totalAfterCredit': float(quote.total_after_credit) if quote else 0
            } if quote else None,
            'beforePhotos': [
                {
                    'photoId': photo.id,
                    'url': photo.file_url
                }
                for photo in before_photos
            ]
        })


class CustomerApprovePreStartView(APIView):
    """C3. Approve pre-start (move job to In Progress)"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='PRE_START'
        )
        
        if checkpoint.status != 'PENDING':
            return Response(
                {'error': 'Checkpoint is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approve checkpoint
        checkpoint.status = 'APPROVED'
        checkpoint.approved_at = timezone.now()
        checkpoint.customer_note = request.data.get('note', '')
        checkpoint.save()
        
        # Update job status
        job.status = 'IN_PROGRESS'
        job.save()
        
        return Response({
            'jobId': job.id,
            'status': job.status
        })


class CustomerRejectPreStartView(APIView):
    """C4. Request changes / ask question"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='PRE_START'
        )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'Reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reject checkpoint
        checkpoint.status = 'REJECTED'
        checkpoint.rejected_at = timezone.now()
        checkpoint.rejection_reason = reason
        checkpoint.save()
        
        return Response({
            'checkpointId': checkpoint.id,
            'status': checkpoint.status
        })


# ==================== Mid-Project Checkpoint ====================

class CustomerMidProjectCheckpointView(APIView):
    """C5. Mid-Project Checkpoint"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='MID_PROJECT'
        )
        
        # Get progress photos
        progress_photos = job.photos.filter(photo_type='PROGRESS')
        
        return Response({
            'checkpointId': checkpoint.id,
            'status': checkpoint.status,
            'progressNote': checkpoint.progress_note,
            'progressPhotos': [
                {
                    'photoId': photo.id,
                    'url': photo.file_url
                }
                for photo in progress_photos
            ]
        })


class CustomerApproveMidProjectView(APIView):
    """C6. Approve mid-project checkpoint"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='MID_PROJECT'
        )
        
        checkpoint.status = 'APPROVED'
        checkpoint.approved_at = timezone.now()
        checkpoint.customer_note = request.data.get('note', '')
        checkpoint.save()
        
        return Response({
            'status': checkpoint.status
        })


class CustomerRejectMidProjectView(APIView):
    """C7. Flag issue at mid-project"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='MID_PROJECT'
        )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'Reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        checkpoint.status = 'ISSUE'
        checkpoint.rejected_at = timezone.now()
        checkpoint.rejection_reason = reason
        checkpoint.save()
        
        # Optionally update job status
        job.status = 'MID_CHECKPOINT_PENDING'
        job.save()
        
        return Response({
            'status': checkpoint.status
        })


# ==================== Final Verification & Payment ====================

class CustomerFinalCheckpointView(APIView):
    """C8. Final Verification & Payment Release"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='FINAL'
        )
        
        # Get final photos
        final_photos = job.photos.filter(photo_type='AFTER')
        
        # Get checklist
        checklist_items = []
        if hasattr(job, 'checklist'):
            checklist_items = job.checklist.items
        
        return Response({
            'checkpointId': checkpoint.id,
            'status': checkpoint.status,
            'finalPhotos': [
                {
                    'photoId': photo.id,
                    'url': photo.file_url
                }
                for photo in final_photos
            ],
            'checklist': checklist_items,
            'summary': checkpoint.scope_summary or 'Work completed as scoped.'
        })


class CustomerApproveFinalView(APIView):
    """C9. Approve completion & release payment"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='FINAL'
        )
        
        # Approve checkpoint
        checkpoint.status = 'APPROVED'
        checkpoint.approved_at = timezone.now()
        checkpoint.customer_note = request.data.get('note', '')
        checkpoint.customer_rating = request.data.get('rating')
        checkpoint.customer_review = request.data.get('review', '')
        checkpoint.save()
        
        # Complete job
        job.status = 'COMPLETED'
        job.completed_date = timezone.now().date()
        job.save()
        
        # TODO: Trigger payout release workflow
        
        return Response({
            'jobId': job.id,
            'status': job.status
        })


class CustomerRejectFinalView(APIView):
    """C10. Raise issue at final checkpoint"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        checkpoint = get_object_or_404(
            JobCheckpoint,
            job=job,
            checkpoint_type='FINAL'
        )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'Reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        checkpoint.status = 'REJECTED'
        checkpoint.rejected_at = timezone.now()
        checkpoint.rejection_reason = reason
        checkpoint.save()
        
        return Response({
            'status': checkpoint.status
        })


# ==================== Customer Materials Management ====================

class CustomerJobMaterialsView(APIView):
    """C11. Materials Screen (Customer)"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        materials = MaterialSuggestion.objects.filter(job=job)
        
        return Response({
            'materialSource': materials.first().customer_material_source if materials.exists() else 'links',
            'items': [
                {
                    'id': m.id,
                    'itemName': m.item_name,
                    'vendor': m.vendor,
                    'priceRange': m.price_range,
                    'productUrl': m.product_url,
                    'vendorLogoUrl': m.vendor_logo_url
                }
                for m in materials
            ]
        })


class CustomerMaterialSourceView(APIView):
    """C12. Choose material source"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        material_source = request.data.get('materialSource')
        
        if material_source not in ['links', 'customer_supplied']:
            return Response(
                {'error': 'Invalid material source'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update all materials for this job
        MaterialSuggestion.objects.filter(job=job).update(
            customer_material_source=material_source
        )
        
        return Response({'success': True})


class CustomerMaterialPhotosView(APIView):
    """C13. Upload customer material photos"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = JobPhoto.objects.create(
            job=job,
            photo_type='CUSTOMER_MATERIALS',
            file_path=f'jobs/{job.id}/customer_materials/{file.name}',
            file_url=f'/media/jobs/{job.id}/customer_materials/{file.name}',
            caption=request.data.get('caption', ''),
            uploaded_by=request.user
        )
        
        return Response({
            'photoId': photo.id,
            'url': photo.file_url
        })


class CustomerMaterialLiabilityView(APIView):
    """C14. Confirm liability disclaimer"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email
        )
        
        accepted = request.data.get('accepted')
        if not accepted:
            return Response(
                {'error': 'Liability acceptance is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update materials liability acceptance
        MaterialSuggestion.objects.filter(job=job).update(
            customer_liability_accepted=True
        )
        
        return Response({'success': True})