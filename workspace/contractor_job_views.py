"""
Contractor Job Management Views
Handles job workflow, evaluation, checkpoints, and materials
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from decimal import Decimal
import uuid
import json

from .models import (
    Job, JobEvaluation, JobPhoto, JobQuote, JobCheckpoint, 
    JobProgressNote, JobChecklist, MaterialSuggestion, Contractor
)
from .serializers import (
    ContractorJobSerializer, JobEvaluationSerializer, JobPhotoSerializer,
    JobQuoteSerializer, JobCheckpointSerializer, JobProgressNoteSerializer,
    JobChecklistSerializer, MaterialSuggestionSerializer
)
from authentication.permissions import IsContractor


# ==================== Contractor Job List & Detail ====================

class ContractorJobListView(generics.ListAPIView):
    """B1. Contractor Home / Job List"""
    serializer_class = ContractorJobSerializer
    permission_classes = [IsAuthenticated, IsContractor]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        
        queryset = Job.objects.filter(
            assigned_to=self.request.user,
            workspace=contractor.workspace
        ).order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class ContractorJobDetailView(generics.RetrieveAPIView):
    """B2. Job Detail — Overview Tab"""
    serializer_class = ContractorJobSerializer
    permission_classes = [IsAuthenticated, IsContractor]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        return Job.objects.filter(
            assigned_to=self.request.user,
            workspace=contractor.workspace
        )


# ==================== Job Evaluation (Walkthrough) ====================

class JobPhotoUploadView(APIView):
    """B3. Upload evaluation photos"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        photo_type = request.data.get('type')
        file = request.FILES.get('file')
        
        if not photo_type or not file:
            return Response(
                {'error': 'Both type and file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if photo_type not in ['before', 'evaluation', 'progress', 'after']:
            return Response(
                {'error': 'Invalid photo type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save photo (in real implementation, upload to S3/cloud storage)
        photo = JobPhoto.objects.create(
            job=job,
            photo_type=photo_type.upper(),
            file_path=f'jobs/{job.id}/photos/{file.name}',
            file_url=f'/media/jobs/{job.id}/photos/{file.name}',
            caption=request.data.get('caption', ''),
            uploaded_by=request.user
        )
        
        return Response({
            'photoId': photo.id,
            'url': photo.file_url
        })


class JobEvaluationUpdateView(APIView):
    """B4. Save/update evaluation data"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def put(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        # Get or create evaluation
        evaluation, created = JobEvaluation.objects.get_or_create(
            job=job,
            defaults={
                'measurements_data': {},
                'tools_required': [],
            }
        )
        
        # Update evaluation data
        data = request.data
        
        if 'measurements' in data:
            measurements = data['measurements']
            evaluation.room_count = measurements.get('roomCount')
            evaluation.square_feet = measurements.get('squareFeet')
            evaluation.measurements_data = measurements
        
        if 'scope' in data:
            evaluation.scope = data['scope']
        
        if 'toolsRequired' in data:
            evaluation.tools_required = data['toolsRequired']
        
        if 'laborRequired' in data:
            evaluation.labor_required = data['laborRequired']
        
        if 'estimatedHours' in data:
            evaluation.estimated_hours = data['estimatedHours']
        
        if 'safetyConcerns' in data:
            evaluation.safety_concerns = data['safetyConcerns']
        
        evaluation.save()
        
        return Response({'success': True})


class JobEvaluationSubmitView(APIView):
    """B5. Submit evaluation + trigger pricing"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        try:
            evaluation = job.evaluation
        except JobEvaluation.DoesNotExist:
            return Response(
                {'error': 'No evaluation data found. Please complete evaluation first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if evaluation.is_submitted:
            return Response(
                {'error': 'Evaluation already submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lock evaluation data
        evaluation.is_submitted = True
        evaluation.submitted_at = timezone.now()
        evaluation.save()
        
        # Update job status
        job.status = 'EVALUATION_COMPLETED'
        job.save()
        
        # Call RAG pricing service
        quote = self._generate_quote(job, evaluation)
        
        # Create pre-start checkpoint
        checkpoint = JobCheckpoint.objects.create(
            job=job,
            checkpoint_type='PRE_START',
            scope_summary=evaluation.scope or 'Evaluation completed, awaiting customer approval'
        )
        
        # Update job status to awaiting approval
        job.status = 'AWAITING_PRE_START_APPROVAL'
        job.save()
        
        return Response({
            'jobId': job.id,
            'status': job.status,
            'quoteId': quote.quote_id,
            'gbbTotal': float(quote.gbb_total),
            'evaluationFeeCredit': float(quote.evaluation_fee)
        })
    
    def _generate_quote(self, job, evaluation):
        """Generate AI-powered quote"""
        # This would call the actual RAG pricing service
        # For now, we'll create a mock quote
        
        quote_id = f"QUOTE-{str(uuid.uuid4())[:8].upper()}"
        
        # Mock pricing calculation
        base_labor = float(evaluation.estimated_hours or 8) * 75  # $75/hour
        overhead = base_labor * 0.2  # 20% overhead
        gbb_total = base_labor + overhead
        
        line_items = [
            {
                'label': f'Labor - {evaluation.labor_required or 1} techs x {evaluation.estimated_hours or 8}h',
                'amount': base_labor
            },
            {
                'label': 'Overhead & fees',
                'amount': overhead
            }
        ]
        
        quote = JobQuote.objects.create(
            job=job,
            quote_id=quote_id,
            gbb_total=Decimal(str(gbb_total)),
            evaluation_fee=job.evaluation_fee,
            total_after_credit=Decimal(str(gbb_total)) - job.evaluation_fee,
            line_items=line_items,
            generation_context={
                'scope': evaluation.scope,
                'measurements': evaluation.measurements_data,
                'labor_required': evaluation.labor_required,
                'estimated_hours': float(evaluation.estimated_hours or 0),
                'location': job.customer_address
            }
        )
        
        return quote


# ==================== Materials & Technical Verification ====================

class JobMaterialSuggestionsView(APIView):
    """B6. Get suggested materials list"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        # Get existing suggestions or generate new ones
        suggestions = MaterialSuggestion.objects.filter(job=job)
        
        if not suggestions.exists():
            # Generate suggestions using RAG/scraper
            suggestions = self._generate_material_suggestions(job)
        
        return Response([
            {
                'id': s.id,
                'itemName': s.item_name,
                'sku': s.sku,
                'vendor': s.vendor,
                'vendorLogoUrl': s.vendor_logo_url,
                'priceRange': s.price_range,
                'suggestedQty': float(s.suggested_qty),
                'unit': s.unit,
                'productUrl': s.product_url
            }
            for s in suggestions
        ])
    
    def _generate_material_suggestions(self, job):
        """Generate material suggestions using AI/scraping"""
        # This would call the actual material scraper/RAG service
        # For now, we'll create mock suggestions
        
        mock_materials = [
            {
                'item_name': 'Interior eggshell paint - white',
                'sku': 'HD-12345',
                'vendor': 'Home Depot',
                'vendor_logo_url': '/static/logos/home_depot.png',
                'price_range': '$35–$45 / gallon',
                'suggested_qty': 3,
                'unit': 'gallon',
                'product_url': 'https://homedepot.com/paint/interior-white'
            },
            {
                'item_name': 'Painter\'s tape 1.5"',
                'sku': 'HD-67890',
                'vendor': 'Home Depot',
                'vendor_logo_url': '/static/logos/home_depot.png',
                'price_range': '$4–$7',
                'suggested_qty': 2,
                'unit': 'roll',
                'product_url': 'https://homedepot.com/tape/painters-tape'
            }
        ]
        
        suggestions = []
        for material in mock_materials:
            suggestion = MaterialSuggestion.objects.create(
                job=job,
                **material
            )
            suggestions.append(suggestion)
        
        return suggestions


class JobMaterialVerificationView(APIView):
    """B7. Save contractor-verified materials"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def put(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        items = request.data.get('items', [])
        
        for item_data in items:
            try:
                suggestion = MaterialSuggestion.objects.get(
                    id=item_data['id'],
                    job=job
                )
                
                suggestion.contractor_confirmed_qty = item_data.get('confirmedQty', suggestion.suggested_qty)
                suggestion.contractor_status = item_data.get('status', 'confirmed')
                suggestion.save()
                
            except MaterialSuggestion.DoesNotExist:
                continue
        
        return Response({'success': True})


# ==================== Progress Updates ====================

class JobProgressPhotoUploadView(APIView):
    """B8. Upload in-progress photos"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = JobPhoto.objects.create(
            job=job,
            photo_type='PROGRESS',
            file_path=f'jobs/{job.id}/progress/{file.name}',
            file_url=f'/media/jobs/{job.id}/progress/{file.name}',
            caption=request.data.get('caption', ''),
            uploaded_by=request.user
        )
        
        return Response({
            'photoId': photo.id,
            'url': photo.file_url
        })


class JobProgressNoteCreateView(APIView):
    """B9. Add progress note"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        note_text = request.data.get('note')
        if not note_text:
            return Response(
                {'error': 'Note is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's an active mid-project checkpoint
        mid_checkpoint = job.checkpoints.filter(
            checkpoint_type='MID_PROJECT',
            status='PENDING'
        ).first()
        
        progress_note = JobProgressNote.objects.create(
            job=job,
            note=note_text,
            added_by=request.user,
            checkpoint=mid_checkpoint
        )
        
        return Response({
            'id': progress_note.id,
            'createdAt': progress_note.created_at
        })


# ==================== Completion & Checklist ====================

class JobChecklistView(APIView):
    """B10. Get checklist template & status"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        # Get or create checklist
        checklist, created = JobChecklist.objects.get_or_create(
            job=job,
            defaults={
                'items': [
                    {'id': 'c1', 'label': 'All walls painted', 'done': False},
                    {'id': 'c2', 'label': 'Area cleaned up', 'done': False},
                    {'id': 'c3', 'label': 'Tools and equipment removed', 'done': False},
                    {'id': 'c4', 'label': 'Final quality check completed', 'done': False}
                ]
            }
        )
        
        return Response({
            'items': checklist.items
        })


class JobChecklistUpdateView(APIView):
    """B11. Update checklist status"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def put(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        try:
            checklist = job.checklist
        except JobChecklist.DoesNotExist:
            return Response(
                {'error': 'Checklist not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        items = request.data.get('items', [])
        
        # Update checklist items
        item_dict = {item['id']: item for item in items}
        
        for checklist_item in checklist.items:
            if checklist_item['id'] in item_dict:
                checklist_item['done'] = item_dict[checklist_item['id']].get('done', False)
        
        checklist.save()
        checklist.calculate_completion()
        
        return Response({'success': True})


class JobCompleteWorkView(APIView):
    """B13. Mark work complete → trigger final checkpoint"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        # Validate checklist is 100% done
        try:
            checklist = job.checklist
            if checklist.completion_percentage < 100:
                return Response(
                    {'error': 'Checklist must be 100% complete before marking work as done'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except JobChecklist.DoesNotExist:
            return Response(
                {'error': 'Checklist not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create final checkpoint
        final_checkpoint, created = JobCheckpoint.objects.get_or_create(
            job=job,
            checkpoint_type='FINAL',
            defaults={
                'scope_summary': 'Work completed, awaiting final customer approval'
            }
        )
        
        # Update job status
        job.status = 'AWAITING_FINAL_APPROVAL'
        job.save()
        
        return Response({
            'jobId': job.id,
            'status': job.status
        })


# ==================== Customer Material Verification ====================

class ContractorVerifyCustomerMaterialsView(APIView):
    """B29. Contractor verifies customer materials"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, assigned_to=request.user)
        
        verification_status = request.data.get('status')  # verified or issue
        note = request.data.get('note', '')
        
        if verification_status not in ['verified', 'issue']:
            return Response(
                {'error': 'Status must be "verified" or "issue"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update material suggestions
        MaterialSuggestion.objects.filter(
            job=job,
            customer_material_source='customer_supplied'
        ).update(
            contractor_verified_customer_materials=(verification_status == 'verified'),
            contractor_verification_note=note
        )
        
        return Response({
            'status': verification_status
        })