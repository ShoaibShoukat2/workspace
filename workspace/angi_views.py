"""
Angi Integration Views
Lead scraping, OAuth connection, and lead management
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
import uuid
import requests
import json

from .models import (
    AngiConnection, Lead, LeadActivity, Workspace
)
from .serializers import (
    AngiConnectionSerializer, LeadSerializer, LeadActivitySerializer
)
from authentication.permissions import IsAdmin, IsInvestor, IsAdminOrFM


# ==================== Angi OAuth Integration ====================

class AngiOAuthInitiateView(APIView):
    """Initiate Angi OAuth connection"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Check if user can connect Angi (Admin or Investor)
        if request.user.role not in ['ADMIN', 'INVESTOR']:
            return Response(
                {'error': 'Only Admin or Investor can connect Angi accounts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate OAuth URL (this would be actual Angi OAuth URL)
        oauth_url = f"https://api.angi.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&state={workspace.workspace_id}"
        
        return Response({
            'oauth_url': oauth_url,
            'message': 'Redirect user to this URL to complete Angi connection'
        })


class AngiOAuthCallbackView(APIView):
    """Handle Angi OAuth callback"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        state = request.data.get('state')  # workspace_id
        
        if not code or not state:
            return Response(
                {'error': 'Missing authorization code or state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        workspace = get_object_or_404(Workspace, workspace_id=state)
        
        # Exchange code for access token (mock implementation)
        try:
            # This would be actual Angi API call
            token_response = self._exchange_code_for_token(code)
            
            # Create or update Angi connection
            angi_connection, created = AngiConnection.objects.update_or_create(
                user=request.user,
                workspace=workspace,
                defaults={
                    'access_token': token_response['access_token'],
                    'refresh_token': token_response.get('refresh_token', ''),
                    'token_expires_at': timezone.now() + timedelta(seconds=token_response['expires_in']),
                    'angi_account_id': token_response['account_id'],
                    'is_active': True
                }
            )
            
            return Response({
                'message': 'Angi account connected successfully',
                'connection': AngiConnectionSerializer(angi_connection).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to connect Angi account: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        # Mock implementation - replace with actual Angi API call
        return {
            'access_token': 'mock_access_token_' + str(uuid.uuid4()),
            'refresh_token': 'mock_refresh_token_' + str(uuid.uuid4()),
            'expires_in': 3600,
            'account_id': 'angi_account_' + str(uuid.uuid4())[:8]
        }


class AngiConnectionStatusView(APIView):
    """Get Angi connection status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        workspace_id = request.query_params.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        try:
            connection = AngiConnection.objects.get(
                user=request.user,
                workspace=workspace
            )
            
            return Response({
                'connected': True,
                'connection': AngiConnectionSerializer(connection).data,
                'is_expired': connection.is_token_expired,
                'last_sync': connection.last_sync
            })
            
        except AngiConnection.DoesNotExist:
            return Response({
                'connected': False,
                'message': 'No Angi connection found'
            })


class DisconnectAngiView(APIView):
    """Disconnect Angi account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        try:
            connection = AngiConnection.objects.get(
                user=request.user,
                workspace=workspace
            )
            connection.is_active = False
            connection.save()
            
            return Response({'message': 'Angi account disconnected successfully'})
            
        except AngiConnection.DoesNotExist:
            return Response(
                {'error': 'No Angi connection found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== Lead Management ====================

class LeadListCreateView(generics.ListCreateAPIView):
    """List and create leads - Available to Admin and Investors"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Enhanced permission check - allow Admin, Investor, and FM roles
        user_role = getattr(self.request.user, 'role', 'ADMIN')
        if user_role not in ['ADMIN', 'INVESTOR', 'FM']:
            return Lead.objects.none()
        
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
            
            # Role-based workspace access control
            if user_role == 'INVESTOR':
                # Check if investor has access to this workspace
                try:
                    from .models import InvestorProfile
                    investor_profile = InvestorProfile.objects.get(user=self.request.user)
                    if investor_profile.workspace != workspace:
                        return Lead.objects.none()
                except InvestorProfile.DoesNotExist:
                    return Lead.objects.none()
            
            queryset = Lead.objects.filter(workspace=workspace)
        else:
            # Role-based global access
            if user_role == 'ADMIN':
                queryset = Lead.objects.all()
            elif user_role == 'INVESTOR':
                # Investor - filter by their workspace
                try:
                    from .models import InvestorProfile
                    investor_profile = InvestorProfile.objects.get(user=self.request.user)
                    queryset = Lead.objects.filter(workspace=investor_profile.workspace)
                except InvestorProfile.DoesNotExist:
                    queryset = Lead.objects.none()
            else:  # FM role
                # FM can see leads from workspaces they manage
                queryset = Lead.objects.filter(workspace__owner=self.request.user)
        
        # Enhanced filtering options
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(source=source_filter)
        
        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search) |
                Q(customer_email__icontains=search) |
                Q(service_type__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Assigned leads filter
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            if assigned_to == 'me':
                queryset = queryset.filter(assigned_to=self.request.user)
            elif assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Enhanced validation for manual lead creation
        self._validate_lead_data(self.request.data)
        
        # Generate unique lead number
        lead_number = self._generate_lead_number()
        
        # Auto-assign lead based on user role and preferences
        assigned_to = self._determine_lead_assignment(workspace)
        
        lead = serializer.save(
            workspace=workspace,
            lead_number=lead_number,
            created_by=self.request.user,
            assigned_to=assigned_to
        )
        
        # Create comprehensive initial activity
        LeadActivity.objects.create(
            lead=lead,
            activity_type='NOTE_ADDED',
            description=f'Lead created manually by {self.request.user.email}',
            performed_by=self.request.user,
            metadata={
                'creation_method': 'manual',
                'user_role': getattr(self.request.user, 'role', 'ADMIN'),
                'workspace_id': str(workspace.workspace_id)
            }
        )
        
        # Enhanced AI follow-up trigger
        if lead.source == 'MANUAL' and self.request.data.get('trigger_ai_contact', True):
            self._trigger_ai_followup(lead)
        
        # Send notification to assigned user if different from creator
        if assigned_to and assigned_to != self.request.user:
            self._send_lead_assignment_notification(lead, assigned_to)
    
    def _validate_lead_data(self, data):
        """Enhanced validation for lead creation"""
        required_fields = ['customer_name', 'customer_phone', 'service_type', 'location']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            })
        
        # Validate phone number format
        phone = data.get('customer_phone', '')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'customer_phone': 'Invalid phone number format'})
    
    def _generate_lead_number(self):
        """Generate unique lead number with retry logic"""
        max_attempts = 5
        for attempt in range(max_attempts):
            lead_number = f"LEAD-{str(uuid.uuid4())[:8].upper()}"
            if not Lead.objects.filter(lead_number=lead_number).exists():
                return lead_number
        
        # Fallback with timestamp
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"LEAD-{timestamp[-8:]}"
    
    def _determine_lead_assignment(self, workspace):
        """Smart lead assignment based on workload and availability"""
        # For now, assign to creator if they're not admin
        user_role = getattr(self.request.user, 'role', 'ADMIN')
        if user_role in ['INVESTOR', 'FM']:
            return self.request.user
        
        # Admin can leave unassigned or implement round-robin logic here
        return None
    
    def _trigger_ai_followup(self, lead):
        """Enhanced AI voice agent follow-up trigger"""
        # Set AI contact preferences based on customer data
        ai_preference = 'CALL'  # Default to call
        if not lead.customer_phone or lead.customer_email:
            ai_preference = 'EMAIL'
        
        lead.ai_contacted = False
        lead.ai_contact_preference = ai_preference
        lead.save()
        
        # Create AI follow-up activity
        LeadActivity.objects.create(
            lead=lead,
            activity_type='AI_TEXT_SENT',
            description=f'AI follow-up scheduled via {ai_preference}',
            metadata={
                'ai_preference': ai_preference,
                'scheduled_at': timezone.now().isoformat()
            }
        )
    
    def _send_lead_assignment_notification(self, lead, assigned_user):
        """Send notification about lead assignment"""
        # This would integrate with notification system
        # For now, just log the assignment
        LeadActivity.objects.create(
            lead=lead,
            activity_type='NOTE_ADDED',
            description=f'Lead assigned to {assigned_user.email}',
            performed_by=self.request.user,
            metadata={
                'assignment_type': 'auto',
                'assigned_to_id': assigned_user.id,
                'assigned_to_email': assigned_user.email
            }
        )


class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete lead - Available to Admin, Investor, and FM"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    queryset = Lead.objects.all()
    
    def get_queryset(self):
        """Filter leads based on user permissions"""
        user_role = getattr(self.request.user, 'role', 'ADMIN')
        
        if user_role == 'ADMIN':
            return Lead.objects.all()
        elif user_role == 'INVESTOR':
            try:
                from .models import InvestorProfile
                investor_profile = InvestorProfile.objects.get(user=self.request.user)
                return Lead.objects.filter(workspace=investor_profile.workspace)
            except InvestorProfile.DoesNotExist:
                return Lead.objects.none()
        elif user_role == 'FM':
            return Lead.objects.filter(workspace__owner=self.request.user)
        else:
            return Lead.objects.none()
    
    def perform_update(self, serializer):
        old_lead = self.get_object()
        old_status = old_lead.status
        old_assigned_to = old_lead.assigned_to
        
        lead = serializer.save()
        
        # Log status change
        if old_status != lead.status:
            LeadActivity.objects.create(
                lead=lead,
                activity_type='STATUS_CHANGED',
                description=f'Status changed from {old_status} to {lead.status}',
                performed_by=self.request.user,
                metadata={
                    'old_status': old_status,
                    'new_status': lead.status,
                    'changed_by_role': getattr(self.request.user, 'role', 'ADMIN')
                }
            )
        
        # Log assignment change
        if old_assigned_to != lead.assigned_to:
            old_assignee = old_assigned_to.email if old_assigned_to else 'Unassigned'
            new_assignee = lead.assigned_to.email if lead.assigned_to else 'Unassigned'
            
            LeadActivity.objects.create(
                lead=lead,
                activity_type='NOTE_ADDED',
                description=f'Assignment changed from {old_assignee} to {new_assignee}',
                performed_by=self.request.user,
                metadata={
                    'old_assigned_to': old_assignee,
                    'new_assigned_to': new_assignee,
                    'assignment_changed_by': self.request.user.email
                }
            )
    
    def perform_destroy(self, instance):
        """Log lead deletion before removing"""
        LeadActivity.objects.create(
            lead=instance,
            activity_type='NOTE_ADDED',
            description=f'Lead deleted by {self.request.user.email}',
            performed_by=self.request.user,
            metadata={
                'deletion_reason': self.request.data.get('reason', 'Not specified'),
                'deleted_by_role': getattr(self.request.user, 'role', 'ADMIN')
            }
        )
        super().perform_destroy(instance)


class LeadActivitiesView(generics.ListCreateAPIView):
    """List and create lead activities - Available to Admin, Investor, and FM"""
    serializer_class = LeadActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        lead_id = self.kwargs.get('lead_id')
        lead = get_object_or_404(Lead, id=lead_id)
        
        # Check if user has access to this lead
        user_role = getattr(self.request.user, 'role', 'ADMIN')
        
        if user_role == 'ADMIN':
            # Admin can access all leads
            pass
        elif user_role == 'INVESTOR':
            try:
                from .models import InvestorProfile
                investor_profile = InvestorProfile.objects.get(user=self.request.user)
                if lead.workspace != investor_profile.workspace:
                    return LeadActivity.objects.none()
            except InvestorProfile.DoesNotExist:
                return LeadActivity.objects.none()
        elif user_role == 'FM':
            if lead.workspace.owner != self.request.user:
                return LeadActivity.objects.none()
        else:
            return LeadActivity.objects.none()
        
        return LeadActivity.objects.filter(lead_id=lead_id).order_by('-created_at')
    
    def perform_create(self, serializer):
        lead_id = self.kwargs.get('lead_id')
        lead = get_object_or_404(Lead, id=lead_id)
        
        # Validate access to lead
        user_role = getattr(self.request.user, 'role', 'ADMIN')
        
        if user_role == 'INVESTOR':
            try:
                from .models import InvestorProfile
                investor_profile = InvestorProfile.objects.get(user=self.request.user)
                if lead.workspace != investor_profile.workspace:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("Access denied to this lead")
            except InvestorProfile.DoesNotExist:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Investor profile not found")
        elif user_role == 'FM':
            if lead.workspace.owner != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Access denied to this lead")
        
        # Enhanced activity creation with metadata
        activity_data = {
            'lead': lead,
            'performed_by': self.request.user,
            'metadata': {
                'user_role': user_role,
                'workspace_id': str(lead.workspace.workspace_id),
                'created_via': 'api'
            }
        }
        
        serializer.save(**activity_data)


class ConvertLeadToJobView(APIView):
    """Convert lead to job"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        
        if lead.status == 'CONVERTED':
            return Response(
                {'error': 'Lead is already converted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create job from lead
        from .models import Job
        
        job_number = f"JOB-{str(uuid.uuid4())[:8].upper()}"
        
        job = Job.objects.create(
            workspace=lead.workspace,
            job_number=job_number,
            title=f"{lead.service_type} - {lead.customer_name}",
            description=lead.description,
            customer_name=lead.customer_name,
            customer_email=lead.customer_email,
            customer_phone=lead.customer_phone,
            customer_address=lead.location,
            created_by=request.user
        )
        
        # Update lead
        lead.status = 'CONVERTED'
        lead.converted_job = job
        lead.save()
        
        # Log activity
        LeadActivity.objects.create(
            lead=lead,
            activity_type='STATUS_CHANGED',
            description=f'Lead converted to job {job.job_number}',
            performed_by=request.user
        )
        
        return Response({
            'message': 'Lead converted to job successfully',
            'job_id': job.id,
            'job_number': job.job_number
        })


# ==================== Angi Lead Scraping ====================

class SyncAngiLeadsView(APIView):
    """Enhanced Angi lead sync - Available to Admin and Investors"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Enhanced permission check
        user_role = getattr(request.user, 'role', 'ADMIN')
        if user_role not in ['ADMIN', 'INVESTOR']:
            return Response(
                {'error': 'Only Admin or Investor can sync Angi leads'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Validate workspace access for investors
        if user_role == 'INVESTOR':
            try:
                from .models import InvestorProfile
                investor_profile = InvestorProfile.objects.get(user=request.user)
                if investor_profile.workspace != workspace:
                    return Response(
                        {'error': 'Access denied to this workspace'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except InvestorProfile.DoesNotExist:
                return Response(
                    {'error': 'Investor profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Find active Angi connection for this workspace
            connection = AngiConnection.objects.get(
                workspace=workspace,
                is_active=True
            )
            
            if connection.is_token_expired:
                return Response(
                    {'error': 'Angi token expired. Please reconnect your Angi account.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Enhanced sync options
            sync_options = {
                'date_from': request.data.get('date_from'),
                'date_to': request.data.get('date_to'),
                'lead_status': request.data.get('lead_status'),
                'service_types': request.data.get('service_types', []),
                'bulk_import': request.data.get('bulk_import', False),
                'auto_assign': request.data.get('auto_assign', True)
            }
            
            # Fetch leads from Angi API with enhanced filtering
            leads_data = self._fetch_angi_leads(connection, sync_options)
            
            # Enhanced processing with bulk operations
            result = self._process_angi_leads(leads_data, workspace, connection, request.user, sync_options)
            
            # Update connection sync status
            connection.last_sync = timezone.now()
            connection.save()
            
            # Create sync activity log
            self._log_sync_activity(workspace, request.user, result)
            
            return Response({
                'message': 'Angi leads synced successfully',
                'summary': result,
                'sync_timestamp': timezone.now().isoformat(),
                'connection_status': 'active'
            })
            
        except AngiConnection.DoesNotExist:
            return Response(
                {'error': 'No active Angi connection found for this workspace. Please connect your Angi account first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Enhanced error logging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Angi sync failed for user {request.user.email}: {str(e)}')
            
            return Response(
                {'error': f'Failed to sync leads: {str(e)}', 'details': 'Please check your Angi connection and try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _fetch_angi_leads(self, connection, sync_options=None):
        """Enhanced Angi API lead fetching with filtering options"""
        if sync_options is None:
            sync_options = {}
        
        # Mock implementation - replace with actual Angi API call
        # This would use connection.access_token for authentication
        
        # Simulate API parameters
        api_params = {
            'account_id': connection.angi_account_id,
            'access_token': connection.access_token,
            'date_from': sync_options.get('date_from'),
            'date_to': sync_options.get('date_to'),
            'status': sync_options.get('lead_status'),
            'service_types': sync_options.get('service_types', []),
            'limit': 100 if sync_options.get('bulk_import') else 20
        }
        
        # Mock response - in real implementation, this would be actual API call
        mock_leads = [
            {
                'id': 'angi_lead_123',
                'customer_name': 'John Doe',
                'customer_phone': '+1234567890',
                'customer_email': 'john@example.com',
                'service_type': 'HVAC Repair',
                'location': '123 Main St, City, State 12345',
                'description': 'Air conditioning not working properly',
                'status': 'new',
                'priority': 'high',
                'budget_range': '$500-$1000',
                'preferred_contact': 'phone',
                'created_at': '2024-01-15T10:30:00Z',
                'updated_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 'angi_lead_124',
                'customer_name': 'Jane Smith',
                'customer_phone': '+1987654321',
                'customer_email': 'jane@example.com',
                'service_type': 'Plumbing',
                'location': '456 Oak Ave, City, State 12345',
                'description': 'Kitchen sink leak needs repair',
                'status': 'new',
                'priority': 'medium',
                'budget_range': '$200-$500',
                'preferred_contact': 'email',
                'created_at': '2024-01-16T14:20:00Z',
                'updated_at': '2024-01-16T14:20:00Z'
            }
        ]
        
        # Apply filtering based on sync options
        filtered_leads = []
        for lead in mock_leads:
            # Filter by service types if specified
            if sync_options.get('service_types') and lead['service_type'] not in sync_options['service_types']:
                continue
            
            # Filter by status if specified
            if sync_options.get('lead_status') and lead['status'] != sync_options['lead_status']:
                continue
            
            filtered_leads.append(lead)
        
        return filtered_leads
    
    def _process_angi_leads(self, leads_data, workspace, connection, user, sync_options):
        """Enhanced bulk processing of Angi leads"""
        result = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'total_processed': len(leads_data),
            'details': []
        }
        
        # Bulk processing for better performance
        leads_to_create = []
        leads_to_update = []
        activities_to_create = []
        
        for lead_data in leads_data:
            try:
                # Check if lead already exists
                existing_lead = Lead.objects.filter(
                    angi_lead_id=lead_data['id'],
                    workspace=workspace
                ).first()
                
                if existing_lead:
                    # Update existing lead
                    updated = self._update_existing_lead(existing_lead, lead_data, connection)
                    if updated:
                        result['updated'] += 1
                        leads_to_update.append(existing_lead)
                    else:
                        result['skipped'] += 1
                else:
                    # Prepare new lead for bulk creation
                    lead_number = f"ANGI-{lead_data['id'][-8:].upper()}"
                    
                    # Auto-assignment logic
                    assigned_to = None
                    if sync_options.get('auto_assign'):
                        assigned_to = self._determine_lead_assignment_for_angi(workspace, user)
                    
                    new_lead_data = {
                        'workspace': workspace,
                        'lead_number': lead_number,
                        'source': 'ANGI',
                        'customer_name': lead_data['customer_name'],
                        'customer_phone': lead_data['customer_phone'],
                        'customer_email': lead_data.get('customer_email', ''),
                        'service_type': lead_data['service_type'],
                        'location': lead_data['location'],
                        'description': lead_data['description'],
                        'angi_lead_id': lead_data['id'],
                        'angi_connection': connection,
                        'created_by': user,
                        'assigned_to': assigned_to,
                        'ai_contact_preference': lead_data.get('preferred_contact', 'CALL').upper()
                    }
                    
                    leads_to_create.append(new_lead_data)
                    result['created'] += 1
                    
            except Exception as e:
                result['errors'] += 1
                result['details'].append({
                    'lead_id': lead_data.get('id', 'unknown'),
                    'error': str(e)
                })
        
        # Bulk create new leads
        if leads_to_create:
            created_leads = self._bulk_create_leads(leads_to_create, activities_to_create)
            
            # Trigger AI follow-up for new leads
            for lead in created_leads:
                if sync_options.get('auto_assign', True):
                    self._trigger_ai_followup(lead)
        
        return result
    
    def _bulk_create_leads(self, leads_data, activities_to_create):
        """Bulk create leads for better performance"""
        created_leads = []
        
        for lead_data in leads_data:
            lead = Lead.objects.create(**lead_data)
            created_leads.append(lead)
            
            # Prepare activity for bulk creation
            activities_to_create.append(LeadActivity(
                lead=lead,
                activity_type='NOTE_ADDED',
                description='Lead imported from Angi via bulk sync',
                metadata={
                    'angi_lead_id': lead_data['angi_lead_id'],
                    'import_method': 'bulk_sync',
                    'imported_by': lead_data['created_by'].email
                }
            ))
        
        # Bulk create activities
        if activities_to_create:
            LeadActivity.objects.bulk_create(activities_to_create)
        
        return created_leads
    
    def _update_existing_lead(self, existing_lead, lead_data, connection):
        """Update existing lead with new Angi data"""
        updated = False
        
        # Check if any data has changed
        if (existing_lead.customer_name != lead_data['customer_name'] or
            existing_lead.customer_phone != lead_data['customer_phone'] or
            existing_lead.description != lead_data['description']):
            
            existing_lead.customer_name = lead_data['customer_name']
            existing_lead.customer_phone = lead_data['customer_phone']
            existing_lead.customer_email = lead_data.get('customer_email', existing_lead.customer_email)
            existing_lead.description = lead_data['description']
            existing_lead.save()
            
            # Log update activity
            LeadActivity.objects.create(
                lead=existing_lead,
                activity_type='NOTE_ADDED',
                description='Lead updated from Angi sync',
                metadata={
                    'angi_lead_id': lead_data['id'],
                    'update_method': 'angi_sync',
                    'changes': ['customer_info', 'description']
                }
            )
            
            updated = True
        
        return updated
    
    def _determine_lead_assignment_for_angi(self, workspace, importing_user):
        """Smart assignment for Angi imported leads"""
        # If importing user is investor, assign to them
        if getattr(importing_user, 'role', 'ADMIN') == 'INVESTOR':
            return importing_user
        
        # For admin, implement round-robin or workload-based assignment
        # For now, leave unassigned for manual assignment
        return None
    
    def _log_sync_activity(self, workspace, user, result):
        """Log sync activity for audit trail"""
        # This could be stored in a separate SyncLog model
        # For now, we'll use the existing activity system
        summary = f"Angi sync completed: {result['created']} created, {result['updated']} updated, {result['errors']} errors"
        
        # Could create a workspace-level activity log here
        pass
    
    def _trigger_ai_followup(self, lead):
        """Enhanced AI voice agent follow-up for Angi leads"""
        # Set AI contact preferences based on Angi lead data
        ai_preference = lead.ai_contact_preference or 'CALL'
        
        lead.ai_contacted = False
        lead.save()
        
        # Create AI follow-up activity
        LeadActivity.objects.create(
            lead=lead,
            activity_type='AI_TEXT_SENT',
            description=f'AI follow-up scheduled via {ai_preference} for Angi lead',
            metadata={
                'ai_preference': ai_preference,
                'source': 'angi_import',
                'scheduled_at': timezone.now().isoformat()
            }
        )


# ==================== Enhanced Lead Management ====================

class BulkImportAngiLeadsView(APIView):
    """Bulk import leads from Angi with advanced options"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Permission check
        user_role = getattr(request.user, 'role', 'ADMIN')
        if user_role not in ['ADMIN', 'INVESTOR']:
            return Response(
                {'error': 'Only Admin or Investor can perform bulk import'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Validate workspace access for investors
        if user_role == 'INVESTOR':
            try:
                from .models import InvestorProfile
                investor_profile = InvestorProfile.objects.get(user=request.user)
                if investor_profile.workspace != workspace:
                    return Response(
                        {'error': 'Access denied to this workspace'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except InvestorProfile.DoesNotExist:
                return Response(
                    {'error': 'Investor profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            connection = AngiConnection.objects.get(
                workspace=workspace,
                is_active=True
            )
            
            if connection.is_token_expired:
                return Response(
                    {'error': 'Angi token expired. Please reconnect.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Enhanced bulk import options
            import_options = {
                'date_range_days': request.data.get('date_range_days', 30),
                'service_types': request.data.get('service_types', []),
                'priority_filter': request.data.get('priority_filter'),
                'budget_range': request.data.get('budget_range'),
                'auto_assign': request.data.get('auto_assign', True),
                'trigger_ai_contact': request.data.get('trigger_ai_contact', True),
                'batch_size': request.data.get('batch_size', 50)
            }
            
            # Calculate date range
            from datetime import timedelta
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=import_options['date_range_days'])
            
            import_options['date_from'] = start_date.isoformat()
            import_options['date_to'] = end_date.isoformat()
            
            # Fetch and process leads in batches
            all_leads_data = self._fetch_angi_leads_bulk(connection, import_options)
            
            # Process in batches for better performance
            batch_size = import_options['batch_size']
            total_batches = (len(all_leads_data) + batch_size - 1) // batch_size
            
            overall_result = {
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0,
                'total_processed': len(all_leads_data),
                'batches_processed': 0,
                'details': []
            }
            
            for i in range(0, len(all_leads_data), batch_size):
                batch_leads = all_leads_data[i:i + batch_size]
                batch_result = self._process_angi_leads(
                    batch_leads, workspace, connection, request.user, import_options
                )
                
                # Aggregate results
                overall_result['created'] += batch_result['created']
                overall_result['updated'] += batch_result['updated']
                overall_result['skipped'] += batch_result['skipped']
                overall_result['errors'] += batch_result['errors']
                overall_result['details'].extend(batch_result['details'])
                overall_result['batches_processed'] += 1
            
            # Update connection
            connection.last_sync = timezone.now()
            connection.save()
            
            return Response({
                'message': 'Bulk import completed successfully',
                'summary': overall_result,
                'import_options': import_options,
                'sync_timestamp': timezone.now().isoformat()
            })
            
        except AngiConnection.DoesNotExist:
            return Response(
                {'error': 'No active Angi connection found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Bulk import failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _fetch_angi_leads_bulk(self, connection, import_options):
        """Fetch leads in bulk with enhanced filtering"""
        # This would make multiple API calls to get all leads within date range
        # For now, return mock data
        
        mock_bulk_leads = []
        for i in range(1, 26):  # Mock 25 leads
            mock_bulk_leads.append({
                'id': f'angi_bulk_{i:03d}',
                'customer_name': f'Customer {i}',
                'customer_phone': f'+123456{i:04d}',
                'customer_email': f'customer{i}@example.com',
                'service_type': ['HVAC', 'Plumbing', 'Electrical', 'Roofing'][i % 4],
                'location': f'{i*100} Main St, City, State 12345',
                'description': f'Service request {i} - needs attention',
                'status': 'new',
                'priority': ['low', 'medium', 'high'][i % 3],
                'budget_range': ['$200-$500', '$500-$1000', '$1000-$2000'][i % 3],
                'preferred_contact': ['phone', 'email'][i % 2],
                'created_at': f'2024-01-{15 + (i % 15):02d}T10:30:00Z'
            })
        
        return mock_bulk_leads


class ManualLeadCreateView(APIView):
    """Enhanced manual lead creation with validation and workflow"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Permission check
        user_role = getattr(request.user, 'role', 'ADMIN')
        if user_role not in ['ADMIN', 'INVESTOR', 'FM']:
            return Response(
                {'error': 'Insufficient permissions to create leads'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Enhanced validation
        validation_result = self._validate_manual_lead_data(request.data)
        if not validation_result['valid']:
            return Response(
                {'error': 'Validation failed', 'details': validation_result['errors']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create lead with enhanced data
            lead_data = self._prepare_manual_lead_data(request.data, workspace, request.user)
            
            serializer = LeadSerializer(data=lead_data)
            if serializer.is_valid():
                lead = serializer.save()
                
                # Create comprehensive activity log
                LeadActivity.objects.create(
                    lead=lead,
                    activity_type='NOTE_ADDED',
                    description=f'Lead created manually by {request.user.email}',
                    performed_by=request.user,
                    metadata={
                        'creation_method': 'manual_enhanced',
                        'user_role': user_role,
                        'workspace_id': str(workspace.workspace_id),
                        'initial_data': {
                            'service_type': lead.service_type,
                            'priority': request.data.get('priority', 'medium'),
                            'budget_estimate': request.data.get('budget_estimate')
                        }
                    }
                )
                
                # Enhanced AI follow-up
                if request.data.get('trigger_ai_contact', True):
                    self._setup_ai_followup(lead, request.data)
                
                # Send notifications if assigned
                if lead.assigned_to and lead.assigned_to != request.user:
                    self._send_assignment_notification(lead)
                
                return Response({
                    'message': 'Lead created successfully',
                    'lead': LeadSerializer(lead).data,
                    'next_steps': self._get_next_steps(lead)
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Invalid lead data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to create lead: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _validate_manual_lead_data(self, data):
        """Enhanced validation for manual lead creation"""
        errors = []
        
        # Required fields
        required_fields = {
            'customer_name': 'Customer name is required',
            'customer_phone': 'Customer phone is required',
            'service_type': 'Service type is required',
            'location': 'Location is required',
            'description': 'Description is required'
        }
        
        for field, message in required_fields.items():
            if not data.get(field):
                errors.append(message)
        
        # Phone validation
        phone = data.get('customer_phone', '')
        if phone:
            cleaned_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not cleaned_phone.isdigit() or len(cleaned_phone) < 10:
                errors.append('Invalid phone number format')
        
        # Email validation
        email = data.get('customer_email', '')
        if email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append('Invalid email format')
        
        # Service type validation
        valid_service_types = ['HVAC', 'Plumbing', 'Electrical', 'Roofing', 'Flooring', 'Painting', 'Other']
        if data.get('service_type') and data['service_type'] not in valid_service_types:
            errors.append(f'Service type must be one of: {", ".join(valid_service_types)}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _prepare_manual_lead_data(self, request_data, workspace, user):
        """Prepare lead data with enhancements"""
        # Generate unique lead number
        lead_number = f"MANUAL-{str(uuid.uuid4())[:8].upper()}"
        
        # Determine assignment
        assigned_to = None
        if request_data.get('assigned_to_id'):
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                assigned_to = User.objects.get(id=request_data['assigned_to_id'])
            except User.DoesNotExist:
                pass
        elif getattr(user, 'role', 'ADMIN') in ['INVESTOR', 'FM']:
            assigned_to = user
        
        return {
            'workspace': workspace.id,
            'lead_number': lead_number,
            'source': 'MANUAL',
            'status': request_data.get('status', 'NEW'),
            'customer_name': request_data['customer_name'],
            'customer_phone': request_data['customer_phone'],
            'customer_email': request_data.get('customer_email', ''),
            'service_type': request_data['service_type'],
            'location': request_data['location'],
            'description': request_data['description'],
            'created_by': user.id,
            'assigned_to': assigned_to.id if assigned_to else None,
            'ai_contact_preference': request_data.get('preferred_contact', 'CALL').upper()
        }
    
    def _setup_ai_followup(self, lead, request_data):
        """Setup AI follow-up with preferences"""
        contact_preference = request_data.get('preferred_contact', 'call').upper()
        delay_hours = request_data.get('ai_delay_hours', 1)
        
        lead.ai_contacted = False
        lead.ai_contact_preference = contact_preference
        lead.save()
        
        # Schedule AI contact
        LeadActivity.objects.create(
            lead=lead,
            activity_type='AI_TEXT_SENT',
            description=f'AI follow-up scheduled via {contact_preference} in {delay_hours} hours',
            metadata={
                'ai_preference': contact_preference,
                'delay_hours': delay_hours,
                'scheduled_at': (timezone.now() + timezone.timedelta(hours=delay_hours)).isoformat()
            }
        )
    
    def _send_assignment_notification(self, lead):
        """Send notification about lead assignment"""
        # This would integrate with notification system
        LeadActivity.objects.create(
            lead=lead,
            activity_type='NOTE_ADDED',
            description=f'Lead assigned to {lead.assigned_to.email}',
            performed_by=lead.created_by,
            metadata={
                'assignment_type': 'manual',
                'assigned_to_id': lead.assigned_to.id,
                'assigned_to_email': lead.assigned_to.email
            }
        )
    
    def _get_next_steps(self, lead):
        """Provide next steps guidance"""
        steps = [
            'Lead has been created and saved to the system',
        ]
        
        if lead.assigned_to:
            steps.append(f'Lead assigned to {lead.assigned_to.email}')
        else:
            steps.append('Consider assigning the lead to a team member')
        
        if lead.ai_contact_preference:
            steps.append(f'AI follow-up scheduled via {lead.ai_contact_preference}')
        
        steps.append('Monitor lead activities and conversion progress')
        
        return steps


# ==================== Lead Statistics ====================

class LeadStatisticsView(APIView):
    """Enhanced lead pipeline statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Permission check
        user_role = getattr(request.user, 'role', 'ADMIN')
        if user_role not in ['ADMIN', 'INVESTOR', 'FM']:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workspace_id = request.query_params.get('workspace_id')
        
        # Build queryset based on permissions
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
            
            # Validate workspace access for investors
            if user_role == 'INVESTOR':
                try:
                    from .models import InvestorProfile
                    investor_profile = InvestorProfile.objects.get(user=request.user)
                    if investor_profile.workspace != workspace:
                        return Response(
                            {'error': 'Access denied to this workspace'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except InvestorProfile.DoesNotExist:
                    return Response(
                        {'error': 'Investor profile not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            leads = Lead.objects.filter(workspace=workspace)
        else:
            # Role-based global access
            if user_role == 'ADMIN':
                leads = Lead.objects.all()
            elif user_role == 'INVESTOR':
                try:
                    from .models import InvestorProfile
                    investor_profile = InvestorProfile.objects.get(user=request.user)
                    leads = Lead.objects.filter(workspace=investor_profile.workspace)
                except InvestorProfile.DoesNotExist:
                    leads = Lead.objects.none()
            else:  # FM
                leads = Lead.objects.filter(workspace__owner=request.user)
        
        # Date filtering
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            leads = leads.filter(created_at__date__gte=date_from)
        if date_to:
            leads = leads.filter(created_at__date__lte=date_to)
        
        # Enhanced statistics
        total_leads = leads.count()
        
        # Status breakdown
        status_breakdown = leads.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Source breakdown
        source_breakdown = leads.values('source').annotate(
            count=Count('id')
        ).order_by('source')
        
        # Conversion metrics
        converted_leads = leads.filter(status='CONVERTED').count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # AI contact metrics
        ai_contacted = leads.filter(ai_contacted=True).count()
        ai_contact_rate = (ai_contacted / total_leads * 100) if total_leads > 0 else 0
        
        # Assignment metrics
        assigned_leads = leads.filter(assigned_to__isnull=False).count()
        assignment_rate = (assigned_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Recent activity
        recent_leads = leads.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        # Service type breakdown
        service_breakdown = leads.values('service_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'summary': {
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'conversion_rate': round(conversion_rate, 2),
                'ai_contacted': ai_contacted,
                'ai_contact_rate': round(ai_contact_rate, 2),
                'assigned_leads': assigned_leads,
                'assignment_rate': round(assignment_rate, 2),
                'recent_leads_7_days': recent_leads
            },
            'breakdowns': {
                'status': list(status_breakdown),
                'source': list(source_breakdown),
                'service_types': list(service_breakdown)
            },
            'performance_metrics': {
                'avg_time_to_contact': self._calculate_avg_time_to_contact(leads),
                'avg_time_to_conversion': self._calculate_avg_time_to_conversion(leads),
                'top_performing_sources': self._get_top_performing_sources(leads)
            }
        })
    
    def _calculate_avg_time_to_contact(self, leads):
        """Calculate average time from lead creation to first contact"""
        # This would calculate based on lead activities
        # For now, return mock data
        return "2.5 hours"
    
    def _calculate_avg_time_to_conversion(self, leads):
        """Calculate average time from lead to conversion"""
        # This would calculate based on conversion timestamps
        # For now, return mock data
        return "5.2 days"
    
    def _get_top_performing_sources(self, leads):
        """Get sources with highest conversion rates"""
        # This would calculate conversion rates by source
        # For now, return mock data
        return [
            {"source": "ANGI", "conversion_rate": 15.2},
            {"source": "MANUAL", "conversion_rate": 12.8},
            {"source": "WEBSITE", "conversion_rate": 8.5}
        ]