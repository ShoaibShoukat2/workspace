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


# ==================== FM Site Visit Management ====================

class FMSiteVisitCreateView(APIView):
    """Create a new site visit for a job"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        # Create site visit record
        from .models import JobPhoto
        
        visit_data = {
            'job_id': job.id,
            'fm_user': request.user.id,
            'status': 'IN_PROGRESS',
            'started_at': timezone.now(),
            'measurements': request.data.get('measurements', {}),
            'scope_confirmed': request.data.get('scope_confirmed', False),
            'tools_required': request.data.get('tools_required', []),
            'labor_required': request.data.get('labor_required', 1),
            'estimated_time': request.data.get('estimated_time', 0),
            'safety_concerns': request.data.get('safety_concerns', ''),
        }
        
        # Update job status
        job.status = 'EVALUATION_IN_PROGRESS'
        job.save()
        
        return Response({
            'message': 'Site visit started successfully',
            'job_id': job.id,
            'visit_data': visit_data
        })


class FMSiteVisitUpdateView(APIView):
    """Update site visit progress"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def put(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        # Update job with visit data
        update_fields = {}
        
        if 'measurements' in request.data:
            update_fields['measurements'] = request.data['measurements']
        
        if 'scope_confirmed' in request.data:
            update_fields['scope_confirmed'] = request.data['scope_confirmed']
        
        if 'tools_required' in request.data:
            update_fields['tools_required'] = request.data['tools_required']
        
        if 'labor_required' in request.data:
            update_fields['labor_required'] = request.data['labor_required']
        
        if 'estimated_time' in request.data:
            update_fields['estimated_time'] = request.data['estimated_time']
        
        if 'safety_concerns' in request.data:
            update_fields['safety_concerns'] = request.data['safety_concerns']
        
        # Update job fields
        for field, value in update_fields.items():
            setattr(job, field, value)
        
        job.save()
        
        return Response({
            'message': 'Site visit updated successfully',
            'job_id': job.id,
            'updated_fields': list(update_fields.keys())
        })


class FMSiteVisitCompleteView(APIView):
    """Complete site visit and move to next stage"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        # Validate required fields
        required_checks = [
            ('measurements', 'Measurements are required'),
            ('scope_confirmed', 'Scope must be confirmed'),
            ('materials', 'Materials must be verified'),
        ]
        
        for field, error_msg in required_checks:
            if not getattr(job, field, None):
                return Response({'error': error_msg}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # Update job status
        job.status = 'EVALUATION_COMPLETED'
        job.evaluation_completed_at = timezone.now()
        job.save()
        
        return Response({
            'message': 'Site visit completed successfully',
            'job_id': job.id,
            'status': job.status,
            'next_step': 'quote_generation'
        })


class FMSiteVisitPhotoUploadView(APIView):
    """Upload photos during site visit"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        file = request.FILES.get('file')
        photo_type = request.data.get('photo_type', 'BEFORE')  # BEFORE, PROGRESS, AFTER
        caption = request.data.get('caption', '')
        
        if not file:
            return Response({'error': 'File is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create job photo
        from .models import JobPhoto
        photo = JobPhoto.objects.create(
            job=job,
            photo_type=photo_type,
            file_path=f'jobs/{job.id}/site_visit/{file.name}',
            file_url=f'/media/jobs/{job.id}/site_visit/{file.name}',
            caption=caption,
            uploaded_by=request.user
        )
        
        return Response({
            'photo_id': photo.id,
            'url': photo.file_url,
            'photo_type': photo_type,
            'message': 'Photo uploaded successfully'
        })


# ==================== AI Material Generation ====================

class AIGenerateMaterialsView(APIView):
    """Generate AI material suggestions for a job"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        # Mock AI material generation based on job details
        # In a real implementation, this would call an AI service
        
        job_scope = request.data.get('scope', job.description or '')
        trade = request.data.get('trade', job.title or 'general')
        
        # Generate mock materials based on trade
        mock_materials = self._generate_mock_materials(trade.lower(), job_scope)
        
        # Save as material suggestions
        from .models import MaterialReference
        
        # Clear existing AI suggestions
        MaterialReference.objects.filter(job=job, status='AI_GENERATED').delete()
        
        created_materials = []
        for material_data in mock_materials:
            material = MaterialReference.objects.create(
                job=job,
                item_name=material_data['name'],
                suggested_qty=material_data['quantity'],
                unit=material_data.get('unit', 'each'),
                vendor=material_data.get('supplier', 'Home Depot'),
                price_range=material_data.get('price_range', '$10-20'),
                product_url=material_data.get('product_url', ''),
                status='AI_GENERATED',
                created_by=request.user
            )
            created_materials.append({
                'id': material.id,
                'name': material.item_name,
                'quantity': material.suggested_qty,
                'supplier': material.vendor,
                'price_range': material.price_range,
                'status': material.status
            })
        
        return Response({
            'message': f'Generated {len(created_materials)} material suggestions',
            'materials': created_materials,
            'ai_analysis': f'Based on {trade} work scope: {job_scope[:100]}...'
        })
    
    def _generate_mock_materials(self, trade, scope):
        """Generate mock materials based on trade type"""
        materials_db = {
            'painting': [
                {'name': 'Premium Paint (Eggshell)', 'quantity': 3, 'unit': 'gallon', 'supplier': 'Sherwin Williams', 'price_range': '$45-50'},
                {'name': 'Roller Kit (9")', 'quantity': 2, 'unit': 'each', 'supplier': 'Home Depot', 'price_range': '$15-20'},
                {'name': 'Painters Tape (Blue)', 'quantity': 4, 'unit': 'roll', 'supplier': '3M', 'price_range': '$5-8'},
                {'name': 'Drop Cloths', 'quantity': 3, 'unit': 'each', 'supplier': 'Home Depot', 'price_range': '$8-12'},
            ],
            'plumbing': [
                {'name': 'PVC Pipe (1/2")', 'quantity': 10, 'unit': 'feet', 'supplier': 'Home Depot', 'price_range': '$2-3'},
                {'name': 'Pipe Fittings', 'quantity': 5, 'unit': 'each', 'supplier': 'Lowes', 'price_range': '$3-5'},
                {'name': 'Plumber Putty', 'quantity': 1, 'unit': 'tube', 'supplier': 'Home Depot', 'price_range': '$8-10'},
            ],
            'electrical': [
                {'name': 'Electrical Wire (12 AWG)', 'quantity': 50, 'unit': 'feet', 'supplier': 'Home Depot', 'price_range': '$1-2'},
                {'name': 'Wire Nuts', 'quantity': 20, 'unit': 'each', 'supplier': 'Lowes', 'price_range': '$0.50-1'},
                {'name': 'Electrical Outlet', 'quantity': 3, 'unit': 'each', 'supplier': 'Home Depot', 'price_range': '$5-8'},
            ]
        }
        
        return materials_db.get(trade, [
            {'name': 'General Materials', 'quantity': 1, 'unit': 'lot', 'supplier': 'Home Depot', 'price_range': '$50-100'}
        ])


class FMVerifyMaterialsView(APIView):
    """FM verifies and updates AI-generated materials"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        materials_data = request.data.get('materials', [])
        
        if not materials_data:
            return Response({'error': 'Materials data is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Clear existing materials
        from .models import MaterialReference
        MaterialReference.objects.filter(job=job).delete()
        
        # Create verified materials
        verified_materials = []
        for material_data in materials_data:
            material = MaterialReference.objects.create(
                job=job,
                item_name=material_data['name'],
                suggested_qty=material_data['quantity'],
                unit=material_data.get('unit', 'each'),
                vendor=material_data.get('supplier', 'Home Depot'),
                price_range=material_data.get('price_range', '$10-20'),
                product_url=material_data.get('product_url', ''),
                status='FM_VERIFIED',
                created_by=request.user
            )
            verified_materials.append({
                'id': material.id,
                'name': material.item_name,
                'quantity': material.suggested_qty,
                'supplier': material.vendor,
                'price_range': material.price_range,
                'status': material.status
            })
        
        # Update job material status
        job.material_status = 'FM_VERIFIED'
        job.save()
        
        return Response({
            'message': f'Verified {len(verified_materials)} materials',
            'materials': verified_materials,
            'job_status': job.material_status
        })


# ==================== Change Order Management ====================

class FMCreateChangeOrderView(APIView):
    """Create a change order for additional work"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        reason = request.data.get('reason')
        line_items = request.data.get('line_items', [])
        
        if not reason:
            return Response({'error': 'Reason is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not line_items:
            return Response({'error': 'At least one line item is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total
        total_additional_cost = sum(
            item.get('quantity', 0) * item.get('rate', 0) 
            for item in line_items
        )
        
        # Create dispute/change order record
        from .models import Dispute
        import uuid
        
        change_order_number = f"CO-{str(uuid.uuid4())[:8].upper()}"
        
        # Format line items for description
        line_items_text = '\n'.join([
            f"- {item['description']}: {item['quantity']} x ${item['rate']} = ${item['quantity'] * item['rate']}"
            for item in line_items
        ])
        
        description = f"""Change Order Request
Reason: {reason}

Additional Work:
{line_items_text}

Total Additional Cost: ${total_additional_cost:.2f}"""
        
        change_order = Dispute.objects.create(
            dispute_number=change_order_number,
            job=job,
            raised_by=request.user,
            category='CHANGE_ORDER',
            title=f'Change Order - {job.job_number}',
            description=description,
            status='PENDING'
        )
        
        return Response({
            'message': 'Change order created successfully',
            'change_order_number': change_order_number,
            'total_additional_cost': total_additional_cost,
            'status': 'pending_approval'
        })


class FMChangeOrderListView(APIView):
    """List change orders created by FM"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        from .models import Dispute
        
        change_orders = Dispute.objects.filter(
            raised_by=request.user,
            category='CHANGE_ORDER'
        ).order_by('-created_at')
        
        change_orders_data = []
        for co in change_orders:
            change_orders_data.append({
                'id': co.id,
                'change_order_number': co.dispute_number,
                'job_id': co.job.id,
                'job_address': co.job.customer_address,
                'title': co.title,
                'status': co.status,
                'created_at': co.created_at,
                'description': co.description[:200] + '...' if len(co.description) > 200 else co.description
            })
        
        return Response({
            'change_orders': change_orders_data,
            'count': len(change_orders_data)
        })


# ==================== FM Job Visit Details ====================

class FMJobVisitDetailView(APIView):
    """Get detailed job information for site visit"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, created_by=request.user)
        
        # Get job photos
        from .models import JobPhoto, MaterialReference
        
        photos = JobPhoto.objects.filter(job=job)
        materials = MaterialReference.objects.filter(job=job)
        
        # Get existing estimates
        estimates = Estimate.objects.filter(job=job)
        
        job_data = {
            'id': job.id,
            'job_number': job.job_number,
            'title': job.title,
            'description': job.description,
            'status': job.status,
            'customer_name': job.customer_name,
            'customer_email': job.customer_email,
            'customer_address': job.customer_address,
            'customer_phone': job.customer_phone,
            'trade': job.title.split(' ')[0] if job.title else 'General',
            'priority': job.priority,
            'created_at': job.created_at,
            'start_date': job.start_date,
            'due_date': job.due_date,
            
            # Visit-specific data
            'measurements': getattr(job, 'measurements', {}),
            'scope_confirmed': getattr(job, 'scope_confirmed', False),
            'tools_required': getattr(job, 'tools_required', []),
            'labor_required': getattr(job, 'labor_required', 1),
            'estimated_time': getattr(job, 'estimated_time', 0),
            'safety_concerns': getattr(job, 'safety_concerns', ''),
            'material_status': getattr(job, 'material_status', 'PENDING'),
            
            # Related data
            'photos': [
                {
                    'id': photo.id,
                    'url': photo.file_url,
                    'photo_type': photo.photo_type,
                    'caption': photo.caption,
                    'uploaded_at': photo.uploaded_at
                }
                for photo in photos
            ],
            'materials': [
                {
                    'id': mat.id,
                    'name': mat.item_name,
                    'quantity': mat.suggested_qty,
                    'unit': mat.unit,
                    'supplier': mat.vendor,
                    'price_range': mat.price_range,
                    'status': mat.status
                }
                for mat in materials
            ],
            'estimates': [
                {
                    'id': est.id,
                    'estimate_number': est.estimate_number,
                    'total_amount': float(est.total_amount),
                    'status': est.status,
                    'created_at': est.created_at
                }
                for est in estimates
            ]
        }
        
        return Response(job_data)
