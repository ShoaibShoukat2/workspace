from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta

from .models import (
    Job, JobTracking, ContractorLocation, CustomerProfile, 
    CustomerNotification, MaterialReference, Contractor
)
from .serializers import (
    JobSerializer, JobTrackingSerializer, ContractorLocationSerializer,
    CustomerProfileSerializer, CustomerNotificationSerializer, MaterialReferenceSerializer
)
from authentication.permissions import IsCustomer


def get_or_create_customer_profile(user):
    """Helper function to get or create customer profile"""
    try:
        return CustomerProfile.objects.get(user=user)
    except CustomerProfile.DoesNotExist:
        # Get or create a default customer workspace
        from .models import Workspace
        
        # Try to find an existing workspace for this user
        user_workspace = Workspace.objects.filter(owner=user).first()
        
        if not user_workspace:
            # Create a workspace owned by this user
            user_workspace = Workspace.objects.create(
                name=f"{user.email}'s Workspace",
                description=f"Default workspace for {user.email}",
                owner=user,
                workspace_type=Workspace.WorkspaceType.CUSTOMER
            )
        
        return CustomerProfile.objects.create(
            user=user,
            workspace=user_workspace,
            company_name="",
            preferred_contact_method='EMAIL'
        )


# ==================== Customer Dashboard Views ====================

class CustomerDashboardView(APIView):
    """Customer dashboard with live job tracking"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request):
        customer_profile = get_or_create_customer_profile(request.user)
        
        # Get customer's jobs
        jobs = Job.objects.filter(
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        # Dashboard statistics
        stats = {
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(status__in=['PENDING', 'IN_PROGRESS']).count(),
            'completed_jobs': jobs.filter(status='COMPLETED').count(),
            'upcoming_jobs': jobs.filter(
                start_date__gte=timezone.now().date(),
                status='PENDING'
            ).count(),
        }
        
        # Recent jobs with tracking
        recent_jobs = jobs.select_related('tracking', 'assigned_to').order_by('-created_at')[:5]
        recent_jobs_data = []
        
        for job in recent_jobs:
            job_data = JobSerializer(job).data
            if hasattr(job, 'tracking'):
                job_data['tracking'] = JobTrackingSerializer(job.tracking).data
            recent_jobs_data.append(job_data)
        
        # Unread notifications
        unread_notifications = CustomerNotification.objects.filter(
            customer=customer_profile,
            is_read=False
        ).count()
        
        return Response({
            'stats': stats,
            'recent_jobs': recent_jobs_data,
            'unread_notifications': unread_notifications,
            'customer_profile': CustomerProfileSerializer(customer_profile).data
        })


class CustomerJobListView(generics.ListAPIView):
    """List all customer jobs with filtering"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get_queryset(self):
        customer_profile = get_or_create_customer_profile(self.request.user)
        
        queryset = Job.objects.filter(
            customer_email=self.request.user.email,
            workspace=customer_profile.workspace
        ).select_related('tracking', 'assigned_to').order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset


class CustomerJobDetailView(APIView):
    """Detailed job view with live tracking"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        job_data = JobSerializer(job).data
        
        # Add tracking information
        if hasattr(job, 'tracking'):
            job_data['tracking'] = JobTrackingSerializer(job.tracking).data
            
            # Get contractor's current location if job is active
            if job.tracking.status in ['EN_ROUTE', 'IN_PROGRESS'] and job.assigned_to:
                try:
                    contractor = Contractor.objects.get(
                        user=job.assigned_to,
                        workspace=customer_profile.workspace
                    )
                    latest_location = ContractorLocation.objects.filter(
                        contractor=contractor,
                        job=job,
                        is_active=True
                    ).order_by('-timestamp').first()
                    
                    if latest_location:
                        job_data['contractor_location'] = ContractorLocationSerializer(latest_location).data
                except Contractor.DoesNotExist:
                    pass
        
        # Add material references (read-only)
        material_references = MaterialReference.objects.filter(job=job)
        job_data['material_references'] = MaterialReferenceSerializer(material_references, many=True).data
        
        # Add contractor information
        if job.assigned_to:
            try:
                contractor = Contractor.objects.get(
                    user=job.assigned_to,
                    workspace=customer_profile.workspace
                )
                job_data['contractor_info'] = {
                    'name': f"{job.assigned_to.first_name} {job.assigned_to.last_name}",
                    'email': job.assigned_to.email,
                    'phone': contractor.phone,
                    'company_name': contractor.company_name,
                    'rating': contractor.rating,
                    'profile_picture': job.assigned_to.profile_picture
                }
            except Contractor.DoesNotExist:
                pass
        
        return Response(job_data)


# ==================== Live GPS Tracking Views ====================

class LiveContractorTrackingView(APIView):
    """Get live contractor location for a specific job"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        if not job.assigned_to:
            return Response({'error': 'No contractor assigned to this job'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        try:
            contractor = Contractor.objects.get(
                user=job.assigned_to,
                workspace=customer_profile.workspace
            )
            
            # Get latest location within last 5 minutes
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            latest_location = ContractorLocation.objects.filter(
                contractor=contractor,
                job=job,
                is_active=True,
                timestamp__gte=five_minutes_ago
            ).order_by('-timestamp').first()
            
            if latest_location:
                location_data = ContractorLocationSerializer(latest_location).data
                
                # Calculate ETA if contractor is en route
                if hasattr(job, 'tracking') and job.tracking.status == 'EN_ROUTE':
                    # This would integrate with Google Maps API for real ETA calculation
                    # For now, we'll use estimated arrival from tracking
                    if job.tracking.estimated_arrival:
                        location_data['eta'] = job.tracking.estimated_arrival
                
                return Response(location_data)
            else:
                return Response({'error': 'No recent location data available'}, 
                              status=status.HTTP_404_NOT_FOUND)
                
        except Contractor.DoesNotExist:
            return Response({'error': 'Contractor not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class JobTrackingUpdatesView(APIView):
    """Get real-time job tracking updates"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        if not hasattr(job, 'tracking'):
            return Response({'error': 'No tracking information available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        tracking_data = JobTrackingSerializer(job.tracking).data
        
        # Add status-specific information
        if job.tracking.status == 'EN_ROUTE':
            tracking_data['message'] = f"Your technician is on the way!"
            if job.tracking.estimated_arrival:
                eta_minutes = int((job.tracking.estimated_arrival - timezone.now()).total_seconds() / 60)
                tracking_data['eta_minutes'] = max(0, eta_minutes)
        elif job.tracking.status == 'ARRIVED':
            tracking_data['message'] = "Your technician has arrived!"
        elif job.tracking.status == 'IN_PROGRESS':
            tracking_data['message'] = "Work is in progress"
        elif job.tracking.status == 'COMPLETED':
            tracking_data['message'] = "Job completed successfully!"
        elif job.tracking.status == 'DELAYED':
            tracking_data['message'] = f"Job delayed: {job.tracking.delay_reason}"
        
        return Response(tracking_data)


# ==================== Customer Notifications ====================

class CustomerNotificationsView(generics.ListAPIView):
    """List customer notifications"""
    serializer_class = CustomerNotificationSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        return CustomerNotification.objects.filter(
            customer=customer_profile
        ).order_by('-sent_at')


class MarkNotificationReadView(APIView):
    """Mark notification as read"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, notification_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        notification = get_object_or_404(
            CustomerNotification,
            id=notification_id,
            customer=customer_profile
        )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({'message': 'Notification marked as read'})


class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        CustomerNotification.objects.filter(
            customer=customer_profile,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All notifications marked as read'})


# ==================== Material Reference Viewing (Read-Only) ====================

class JobMaterialReferencesView(generics.ListAPIView):
    """List material references for a job (read-only for price transparency)"""
    serializer_class = MaterialReferenceSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get_queryset(self):
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=self.request.user.email,
            workspace=customer_profile.workspace
        )
        return MaterialReference.objects.filter(job=job).order_by('item_name')


class MaterialReferenceDetailView(APIView):
    """Get detailed material reference information with purchase links"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, reference_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        material_ref = get_object_or_404(MaterialReference, id=reference_id)
        
        # Verify customer owns this job
        if material_ref.job.customer_email != request.user.email:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        material_data = MaterialReferenceSerializer(material_ref).data
        
        # Add disclaimer
        material_data['disclaimer'] = "Materials are purchased directly by the customer from suppliers. Apex does not handle material logistics or delivery."
        
        return Response(material_data)


# ==================== Customer Profile Management ====================

class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """Customer profile management"""
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get_object(self):
        return get_object_or_404(CustomerProfile, user=self.request.user)


class CustomerPreferencesView(APIView):
    """Update customer notification preferences"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        return Response({
            'notification_preferences': customer_profile.notification_preferences,
            'preferred_contact_method': customer_profile.preferred_contact_method
        })
    
    def post(self, request):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        
        notification_preferences = request.data.get('notification_preferences', {})
        preferred_contact_method = request.data.get('preferred_contact_method')
        
        if notification_preferences:
            customer_profile.notification_preferences = notification_preferences
        
        if preferred_contact_method:
            customer_profile.preferred_contact_method = preferred_contact_method
        
        customer_profile.save()
        
        return Response({'message': 'Preferences updated successfully'})


# ==================== Issue Reporting ====================

class ReportIssueView(APIView):
    """Report issues with jobs"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        issue_description = request.data.get('description')
        issue_category = request.data.get('category', 'OTHER')
        
        if not issue_description:
            return Response({'error': 'Issue description is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create dispute or issue record
        from .models import Dispute
        
        # Generate dispute number
        import uuid
        dispute_number = f"DISP-{str(uuid.uuid4())[:8].upper()}"
        
        # Get contractor if assigned
        contractor = None
        if job.assigned_to:
            try:
                contractor = Contractor.objects.get(
                    user=job.assigned_to,
                    workspace=customer_profile.workspace
                )
            except Contractor.DoesNotExist:
                pass
        
        if contractor:
            dispute = Dispute.objects.create(
                dispute_number=dispute_number,
                job=job,
                raised_by=request.user,
                contractor=contractor,
                category=issue_category,
                title=f"Customer Issue - {job.job_number}",
                description=issue_description
            )
            
            return Response({
                'message': 'Issue reported successfully',
                'dispute_number': dispute_number
            })
        else:
            return Response({'error': 'No contractor assigned to report issue against'}, 
                          status=status.HTTP_400_BAD_REQUEST)


# ==================== Temporary Credentials Management ====================

class GenerateCustomerCredentialsView(APIView):
    """Generate temporary credentials for customer after quote approval"""
    permission_classes = []  # Public endpoint with token validation
    
    def post(self, request):
        email = request.data.get('email')
        quote_token = request.data.get('quote_token')
        
        if not email or not quote_token:
            return Response({'error': 'Email and quote token are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validate quote token and get job
        from .models import Job
        try:
            job = Job.objects.get(magic_token=quote_token)
            if job.customer_email != email:
                return Response({'error': 'Email does not match quote'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({'error': 'Invalid quote token'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Get or create user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': job.customer_name.split(' ')[0] if job.customer_name else '',
                'last_name': ' '.join(job.customer_name.split(' ')[1:]) if job.customer_name and len(job.customer_name.split(' ')) > 1 else '',
                'is_active': True
            }
        )
        
        # Generate temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Set password
        user.set_password(temp_password)
        user.save()
        
        # Create customer profile if needed
        customer_profile = get_or_create_customer_profile(user)
        
        # Generate auth token
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Credentials generated successfully',
            'credentials': {
                'email': email,
                'temporary_password': temp_password,
                'portal_link': f"{request.build_absolute_uri('/customer/dashboard')}",
                'auth_token': token.key
            },
            'user_created': created
        })


class ValidateQuoteTokenView(APIView):
    """Validate quote token and get job details"""
    permission_classes = []  # Public endpoint
    
    def get(self, request, token):
        try:
            from .models import Job, Estimate
            job = Job.objects.get(magic_token=token)
            
            # Get associated estimate
            estimate = Estimate.objects.filter(job=job).first()
            
            return Response({
                'valid': True,
                'job': {
                    'id': job.id,
                    'job_number': job.job_number,
                    'customer_name': job.customer_name,
                    'customer_email': job.customer_email,
                    'customer_address': job.customer_address,
                    'status': job.status
                },
                'estimate': {
                    'id': estimate.id,
                    'estimate_number': estimate.estimate_number,
                    'total_amount': estimate.total_amount,
                    'status': estimate.status,
                    'is_signed': bool(estimate.customer_signature)
                } if estimate else None
            })
        except Job.DoesNotExist:
            return Response({'valid': False, 'error': 'Invalid token'}, 
                          status=status.HTTP_404_NOT_FOUND)


# ==================== Quote Approval (Separate from Estimate Signing) ====================

class ApproveQuoteView(APIView):
    """Approve quote and start job (separate from estimate signing)"""
    permission_classes = []  # Public endpoint with token validation
    
    def post(self, request, token):
        try:
            from .models import Job, Estimate
            job = Job.objects.get(magic_token=token)
            
            # Get associated estimate
            estimate = Estimate.objects.filter(job=job).first()
            if not estimate:
                return Response({'error': 'No estimate found for this job'}, 
                              status=status.HTTP_404_NOT_FOUND)
            
            # Update job status
            job.status = 'AWAITING_PRE_START_APPROVAL'
            job.save()
            
            # Update estimate status
            estimate.status = 'APPROVED'
            estimate.approved_at = timezone.now()
            estimate.save()
            
            # Create job tracking if not exists
            from .models import JobTracking
            tracking, created = JobTracking.objects.get_or_create(
                job=job,
                defaults={
                    'status': 'PENDING',
                    'created_at': timezone.now()
                }
            )
            
            return Response({
                'message': 'Quote approved successfully',
                'job_id': job.id,
                'job_status': job.status,
                'estimate_status': estimate.status,
                'next_step': 'credentials_generation'
            })
            
        except Job.DoesNotExist:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_404_NOT_FOUND)


# ==================== Material Delivery Confirmation ====================

class MaterialDeliveryConfirmationView(APIView):
    """Handle material delivery confirmation (legacy support)"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, job_id):
        """Get material delivery status for a job"""
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        # Get material references (since MaterialDelivery was removed)
        material_references = MaterialReference.objects.filter(job=job)
        
        return Response({
            'job_id': job.id,
            'materials': [
                {
                    'id': ref.id,
                    'item_name': ref.item_name,
                    'quantity': ref.suggested_qty,
                    'status': 'pending_delivery',  # Default status since delivery tracking was removed
                    'supplier': ref.vendor,
                    'price_range': ref.price_range
                }
                for ref in material_references
            ],
            'delivery_status': 'not_tracked',
            'message': 'Material delivery tracking has been discontinued. Materials are reference-only for price transparency.'
        })
    
    def post(self, request, job_id):
        """Submit material delivery confirmation (legacy support)"""
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        delivery_status = request.data.get('status')
        photos = request.data.get('photos', [])
        notes = request.data.get('notes', '')
        location = request.data.get('location')
        
        # Since MaterialDelivery model was removed, we'll create a note in the job
        if notes or delivery_status:
            job.notes = f"{job.notes or ''}\n\nMaterial Delivery Note ({timezone.now().strftime('%Y-%m-%d %H:%M')}): Status: {delivery_status}, Notes: {notes}"
            job.save()
        
        # Create a customer notification
        CustomerNotification.objects.create(
            customer=customer_profile,
            notification_type='MATERIAL_UPDATE',
            title='Material Delivery Confirmation Received',
            message=f'Your material delivery confirmation has been recorded. Status: {delivery_status}',
            is_read=False
        )
        
        return Response({
            'message': 'Material delivery confirmation recorded',
            'status': delivery_status,
            'note': 'Material delivery tracking has been discontinued. This information has been saved as a job note.',
            'job_id': job.id
        })


class MaterialDeliveryPhotosUploadView(APIView):
    """Upload photos for material delivery confirmation"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def post(self, request, job_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        job = get_object_or_404(
            Job,
            id=job_id,
            customer_email=request.user.email,
            workspace=customer_profile.workspace
        )
        
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'File is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create job photo for material delivery
        from .models import JobPhoto
        photo = JobPhoto.objects.create(
            job=job,
            photo_type='CUSTOMER_MATERIALS',
            file_path=f'jobs/{job.id}/material_delivery/{file.name}',
            file_url=f'/media/jobs/{job.id}/material_delivery/{file.name}',
            caption=request.data.get('caption', 'Material delivery photo'),
            uploaded_by=request.user
        )
        
        return Response({
            'photo_id': photo.id,
            'url': photo.file_url,
            'message': 'Photo uploaded successfully'
        })


# ==================== Magic Token Based Access ====================

class JobDetailByTokenView(APIView):
    """Get job details using magic token (for public access)"""
    permission_classes = []  # Public endpoint
    
    def get(self, request, token):
        try:
            from .models import Job, Estimate, MaterialReference
            job = Job.objects.get(magic_token=token)
            
            # Get associated estimate
            estimate = Estimate.objects.filter(job=job).first()
            
            # Get material references
            materials = MaterialReference.objects.filter(job=job)
            
            return Response({
                'job': {
                    'id': job.id,
                    'job_number': job.job_number,
                    'title': job.title,
                    'description': job.description,
                    'status': job.status,
                    'customer_name': job.customer_name,
                    'customer_email': job.customer_email,
                    'customer_address': job.customer_address,
                    'customer_phone': job.customer_phone,
                    'property_address': job.customer_address,  # Alias for frontend compatibility
                    'trade': job.title.split(' ')[0].lower() if job.title else 'general',  # Extract trade from title
                    'created_at': job.created_at,
                    'start_date': job.start_date,
                    'due_date': job.due_date
                },
                'estimate': {
                    'id': estimate.id,
                    'estimate_number': estimate.estimate_number,
                    'total_amount': float(estimate.total_amount),
                    'status': estimate.status,
                    'is_signed': bool(estimate.customer_signature),
                    'scope_of_work': estimate.notes or 'Standard service work as discussed.',
                    'created_at': estimate.created_at,
                    'valid_until': estimate.valid_until
                } if estimate else None,
                'materials': [
                    {
                        'id': mat.id,
                        'name': mat.item_name,
                        'quantity': int(mat.suggested_qty) if mat.suggested_qty else 1,
                        'supplier': mat.vendor,
                        'price_range': mat.price_range,
                        'product_url': mat.product_url
                    }
                    for mat in materials
                ],
                'magic_token': token
            })
            
        except Job.DoesNotExist:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_404_NOT_FOUND)


class CustomerTrackingByTokenView(APIView):
    """Get job tracking information using magic token"""
    permission_classes = []  # Public endpoint
    
    def get(self, request, token):
        try:
            from .models import Job, JobTracking, Contractor, ContractorLocation
            job = Job.objects.get(magic_token=token)
            
            # Get job tracking
            tracking = None
            if hasattr(job, 'tracking'):
                tracking = job.tracking
            
            # Get contractor info
            contractor_info = None
            contractor_location = None
            
            if job.assigned_to:
                try:
                    contractor = Contractor.objects.get(user=job.assigned_to)
                    contractor_info = {
                        'name': f"{job.assigned_to.first_name} {job.assigned_to.last_name}",
                        'email': job.assigned_to.email,
                        'phone': contractor.phone,
                        'company_name': contractor.company_name,
                        'rating': float(contractor.rating) if contractor.rating else 4.5
                    }
                    
                    # Get latest location
                    latest_location = ContractorLocation.objects.filter(
                        contractor=contractor,
                        job=job,
                        is_active=True
                    ).order_by('-timestamp').first()
                    
                    if latest_location:
                        contractor_location = {
                            'latitude': float(latest_location.latitude),
                            'longitude': float(latest_location.longitude),
                            'timestamp': latest_location.timestamp,
                            'accuracy': latest_location.accuracy
                        }
                        
                except Contractor.DoesNotExist:
                    pass
            
            return Response({
                'job': {
                    'id': job.id,
                    'status': job.status,
                    'customer_address': job.customer_address,
                    'property_address': job.customer_address
                },
                'tracking': {
                    'status': tracking.status if tracking else 'PENDING',
                    'estimated_arrival': tracking.estimated_arrival if tracking else None,
                    'actual_arrival': tracking.actual_arrival if tracking else None,
                    'started_at': tracking.started_at if tracking else None,
                    'completed_at': tracking.completed_at if tracking else None
                } if tracking else None,
                'contractor': contractor_info,
                'contractor_location': contractor_location
            })
            
        except Job.DoesNotExist:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_404_NOT_FOUND)