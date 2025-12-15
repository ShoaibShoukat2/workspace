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
    CustomerNotification, MaterialDelivery, Contractor
)
from .serializers import (
    JobSerializer, JobTrackingSerializer, ContractorLocationSerializer,
    CustomerProfileSerializer, CustomerNotificationSerializer, MaterialDeliverySerializer
)
from authentication.permissions import IsCustomer


# ==================== Customer Dashboard Views ====================

class CustomerDashboardView(APIView):
    """Customer dashboard with live job tracking"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        
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
        customer_profile = get_object_or_404(CustomerProfile, user=self.request.user)
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
        
        # Add material deliveries
        material_deliveries = MaterialDelivery.objects.filter(job=job)
        job_data['material_deliveries'] = MaterialDeliverySerializer(material_deliveries, many=True).data
        
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


# ==================== Material Delivery Tracking ====================

class JobMaterialDeliveriesView(generics.ListAPIView):
    """List material deliveries for a job"""
    serializer_class = MaterialDeliverySerializer
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
        return MaterialDelivery.objects.filter(job=job).order_by('-created_at')


class MaterialDeliveryDetailView(APIView):
    """Get detailed material delivery information"""
    permission_classes = [IsAuthenticated, IsCustomer]
    
    def get(self, request, delivery_id):
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        delivery = get_object_or_404(MaterialDelivery, id=delivery_id)
        
        # Verify customer owns this job
        if delivery.job.customer_email != request.user.email:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        return Response(MaterialDeliverySerializer(delivery).data)


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