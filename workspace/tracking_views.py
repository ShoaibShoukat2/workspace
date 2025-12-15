from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import json

from .models import (
    Job, JobTracking, ContractorLocation, Contractor, 
    CustomerNotification, CustomerProfile
)
from .serializers import (
    JobTrackingSerializer, ContractorLocationSerializer
)
from authentication.permissions import IsContractor, IsAdmin


# ==================== Contractor GPS Tracking ====================

class UpdateContractorLocationView(APIView):
    """Update contractor's GPS location"""
    permission_classes = [IsAuthenticated, IsContractor]
    
    def post(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        accuracy = request.data.get('accuracy', 10.0)
        speed = request.data.get('speed')
        heading = request.data.get('heading')
        altitude = request.data.get('altitude')
        job_id = request.data.get('job_id')
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get contractor profile
        try:
            contractor = Contractor.objects.get(user=request.user)
        except Contractor.DoesNotExist:
            return Response(
                {'error': 'Contractor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get job if provided
        job = None
        if job_id:
            try:
                job = Job.objects.get(
                    id=job_id,
                    assigned_to=request.user,
                    status__in=['PENDING', 'IN_PROGRESS']
                )
            except Job.DoesNotExist:
                return Response(
                    {'error': 'Job not found or not assigned to you'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Deactivate previous locations for this contractor
        ContractorLocation.objects.filter(
            contractor=contractor,
            is_active=True
        ).update(is_active=False)
        
        # Create new location record
        location = ContractorLocation.objects.create(
            contractor=contractor,
            job=job,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            speed=speed,
            heading=heading,
            altitude=altitude,
            is_active=True
        )
        
        # Update job tracking if job is provided
        if job and hasattr(job, 'tracking'):
            job.tracking.last_location_update = timezone.now()
            job.tracking.save()
        
        return Response({
            'message': 'Location updated successfully',
            'location': ContractorLocationSerializer(location).data
        })


class ContractorLocationHistoryView(generics.ListAPIView):
    """Get contractor's location history"""
    serializer_class = ContractorLocationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor_id = self.kwargs.get('contractor_id')
        job_id = self.request.query_params.get('job_id')
        hours = int(self.request.query_params.get('hours', 24))
        
        # Check permissions
        if self.request.user.role not in ['ADMIN', 'FM']:
            # Contractors can only see their own location
            if hasattr(self.request.user, 'contractor_profiles'):
                contractor = self.request.user.contractor_profiles.first()
                if not contractor or contractor.id != int(contractor_id):
                    return ContractorLocation.objects.none()
            else:
                return ContractorLocation.objects.none()
        
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        # Filter by time range
        time_threshold = timezone.now() - timedelta(hours=hours)
        queryset = ContractorLocation.objects.filter(
            contractor=contractor,
            timestamp__gte=time_threshold
        ).order_by('-timestamp')
        
        # Filter by job if provided
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        return queryset


# ==================== Job Tracking Management ====================

class UpdateJobTrackingView(APIView):
    """Update job tracking status"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check permissions
        if request.user.role not in ['ADMIN', 'FM'] and job.assigned_to != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        delay_reason = request.data.get('delay_reason')
        estimated_arrival = request.data.get('estimated_arrival')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create job tracking
        tracking, created = JobTracking.objects.get_or_create(
            job=job,
            defaults={'status': 'SCHEDULED'}
        )
        
        # Update tracking
        old_status = tracking.status
        tracking.status = new_status
        
        if delay_reason:
            tracking.delay_reason = delay_reason
        
        if estimated_arrival:
            from datetime import datetime
            tracking.estimated_arrival = datetime.fromisoformat(estimated_arrival.replace('Z', '+00:00'))
        
        # Set timestamps based on status
        if new_status == 'ARRIVED' and old_status != 'ARRIVED':
            tracking.actual_arrival = timezone.now()
        elif new_status == 'IN_PROGRESS' and old_status != 'IN_PROGRESS':
            tracking.started_at = timezone.now()
        elif new_status == 'COMPLETED' and old_status != 'COMPLETED':
            tracking.completed_at = timezone.now()
        
        tracking.save()
        
        # Send customer notification
        self._send_customer_notification(job, new_status, tracking)
        
        return Response({
            'message': 'Job tracking updated successfully',
            'tracking': JobTrackingSerializer(tracking).data
        })
    
    def _send_customer_notification(self, job, status, tracking):
        """Send notification to customer about status change"""
        if not job.customer_email:
            return
        
        try:
            # Get customer profile
            from authentication.models import User
            customer_user = User.objects.get(email=job.customer_email)
            customer_profile = CustomerProfile.objects.get(user=customer_user)
            
            # Create notification based on status
            notification_data = self._get_notification_data(status, job, tracking)
            
            if notification_data:
                CustomerNotification.objects.create(
                    customer=customer_profile,
                    job=job,
                    notification_type=notification_data['type'],
                    title=notification_data['title'],
                    message=notification_data['message']
                )
        except (User.DoesNotExist, CustomerProfile.DoesNotExist):
            pass  # Customer not in system
    
    def _get_notification_data(self, status, job, tracking):
        """Get notification data based on status"""
        contractor_name = f"{job.assigned_to.first_name} {job.assigned_to.last_name}" if job.assigned_to else "Your technician"
        
        notifications = {
            'EN_ROUTE': {
                'type': 'TECH_EN_ROUTE',
                'title': 'Technician is on the way!',
                'message': f'{contractor_name} is en route to your location for job {job.job_number}.'
            },
            'ARRIVED': {
                'type': 'TECH_ARRIVED',
                'title': 'Technician has arrived',
                'message': f'{contractor_name} has arrived at your location for job {job.job_number}.'
            },
            'IN_PROGRESS': {
                'type': 'JOB_STARTED',
                'title': 'Work has started',
                'message': f'{contractor_name} has started work on job {job.job_number}.'
            },
            'COMPLETED': {
                'type': 'JOB_COMPLETED',
                'title': 'Job completed',
                'message': f'Job {job.job_number} has been completed by {contractor_name}.'
            },
            'DELAYED': {
                'type': 'JOB_DELAYED',
                'title': 'Job delayed',
                'message': f'Job {job.job_number} has been delayed. Reason: {tracking.delay_reason or "Not specified"}'
            }
        }
        
        return notifications.get(status)


class JobTrackingDetailView(APIView):
    """Get detailed job tracking information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check permissions
        can_view = False
        if request.user.role in ['ADMIN', 'FM']:
            can_view = True
        elif job.assigned_to == request.user:
            can_view = True
        elif job.customer_email == request.user.email:
            can_view = True
        
        if not can_view:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get tracking information
        tracking_data = {}
        if hasattr(job, 'tracking'):
            tracking_data = JobTrackingSerializer(job.tracking).data
        
        # Get contractor's current location if job is active
        contractor_location = None
        if job.assigned_to and job.status in ['PENDING', 'IN_PROGRESS']:
            try:
                contractor = Contractor.objects.get(user=job.assigned_to)
                latest_location = ContractorLocation.objects.filter(
                    contractor=contractor,
                    job=job,
                    is_active=True,
                    timestamp__gte=timezone.now() - timedelta(minutes=10)
                ).order_by('-timestamp').first()
                
                if latest_location:
                    contractor_location = ContractorLocationSerializer(latest_location).data
            except Contractor.DoesNotExist:
                pass
        
        return Response({
            'job_id': job.id,
            'job_number': job.job_number,
            'job_title': job.title,
            'job_status': job.status,
            'tracking': tracking_data,
            'contractor_location': contractor_location,
            'contractor_info': {
                'name': f"{job.assigned_to.first_name} {job.assigned_to.last_name}" if job.assigned_to else None,
                'email': job.assigned_to.email if job.assigned_to else None,
                'phone': getattr(job.assigned_to, 'phone', None) if job.assigned_to else None
            } if job.assigned_to else None
        })


# ==================== Admin Tracking Views ====================

class AdminTrackingDashboardView(APIView):
    """Admin dashboard for tracking all active jobs"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all active jobs with tracking
        active_jobs = Job.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS']
        ).select_related('assigned_to', 'tracking', 'workspace')
        
        jobs_data = []
        for job in active_jobs:
            job_data = {
                'job_id': job.id,
                'job_number': job.job_number,
                'title': job.title,
                'workspace': job.workspace.name,
                'status': job.status,
                'assigned_contractor': job.assigned_to.email if job.assigned_to else None,
                'customer_name': job.customer_name,
                'start_date': job.start_date,
                'due_date': job.due_date,
                'tracking_status': None,
                'estimated_arrival': None,
                'last_location_update': None,
                'contractor_location': None
            }
            
            # Add tracking information
            if hasattr(job, 'tracking'):
                job_data['tracking_status'] = job.tracking.status
                job_data['estimated_arrival'] = job.tracking.estimated_arrival
                job_data['last_location_update'] = job.tracking.last_location_update
            
            # Add contractor location
            if job.assigned_to:
                try:
                    contractor = Contractor.objects.get(user=job.assigned_to)
                    latest_location = ContractorLocation.objects.filter(
                        contractor=contractor,
                        is_active=True,
                        timestamp__gte=timezone.now() - timedelta(minutes=30)
                    ).order_by('-timestamp').first()
                    
                    if latest_location:
                        job_data['contractor_location'] = {
                            'latitude': float(latest_location.latitude),
                            'longitude': float(latest_location.longitude),
                            'timestamp': latest_location.timestamp,
                            'accuracy': latest_location.accuracy
                        }
                except Contractor.DoesNotExist:
                    pass
            
            jobs_data.append(job_data)
        
        # Summary statistics
        summary = {
            'total_active_jobs': len(jobs_data),
            'en_route_jobs': len([j for j in jobs_data if j['tracking_status'] == 'EN_ROUTE']),
            'in_progress_jobs': len([j for j in jobs_data if j['tracking_status'] == 'IN_PROGRESS']),
            'delayed_jobs': len([j for j in jobs_data if j['tracking_status'] == 'DELAYED']),
            'jobs_with_tracking': len([j for j in jobs_data if j['contractor_location']])
        }
        
        return Response({
            'summary': summary,
            'active_jobs': jobs_data
        })


class ContractorTrackingStatusView(APIView):
    """Get tracking status for all contractors"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all active contractors
        contractors = Contractor.objects.filter(status='ACTIVE').select_related('user')
        
        contractors_data = []
        for contractor in contractors:
            # Get current job
            current_job = Job.objects.filter(
                assigned_to=contractor.user,
                status__in=['PENDING', 'IN_PROGRESS']
            ).first()
            
            # Get latest location
            latest_location = ContractorLocation.objects.filter(
                contractor=contractor,
                is_active=True,
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).order_by('-timestamp').first()
            
            contractor_data = {
                'contractor_id': contractor.id,
                'contractor_email': contractor.user.email,
                'contractor_name': f"{contractor.user.first_name} {contractor.user.last_name}",
                'company_name': contractor.company_name,
                'current_job': {
                    'job_id': current_job.id,
                    'job_number': current_job.job_number,
                    'title': current_job.title,
                    'status': current_job.status
                } if current_job else None,
                'location': {
                    'latitude': float(latest_location.latitude),
                    'longitude': float(latest_location.longitude),
                    'timestamp': latest_location.timestamp,
                    'accuracy': latest_location.accuracy
                } if latest_location else None,
                'is_online': latest_location is not None,
                'last_seen': latest_location.timestamp if latest_location else None
            }
            
            contractors_data.append(contractor_data)
        
        # Sort by online status and last seen
        contractors_data.sort(key=lambda x: (not x['is_online'], x['last_seen'] or timezone.now()), reverse=True)
        
        return Response({
            'contractors': contractors_data,
            'summary': {
                'total_contractors': len(contractors_data),
                'online_contractors': len([c for c in contractors_data if c['is_online']]),
                'contractors_with_jobs': len([c for c in contractors_data if c['current_job']])
            }
        })