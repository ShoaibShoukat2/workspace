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
    """List and create leads"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
            queryset = Lead.objects.filter(workspace=workspace)
        else:
            queryset = Lead.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by source
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(source=source_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        # Generate lead number
        lead_number = f"LEAD-{str(uuid.uuid4())[:8].upper()}"
        
        lead = serializer.save(
            workspace=workspace,
            lead_number=lead_number,
            created_by=self.request.user
        )
        
        # Create initial activity
        LeadActivity.objects.create(
            lead=lead,
            activity_type='NOTE_ADDED',
            description='Lead created manually',
            performed_by=self.request.user
        )
        
        # Trigger AI follow-up if enabled
        if lead.source == 'MANUAL':
            self._trigger_ai_followup(lead)
    
    def _trigger_ai_followup(self, lead):
        """Trigger AI voice agent follow-up"""
        # This would integrate with AI voice agent system
        # For now, just mark that AI should contact
        lead.ai_contacted = False
        lead.save()


class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete lead"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    queryset = Lead.objects.all()
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        lead = serializer.save()
        
        # Log status change
        if old_status != lead.status:
            LeadActivity.objects.create(
                lead=lead,
                activity_type='STATUS_CHANGED',
                description=f'Status changed from {old_status} to {lead.status}',
                performed_by=self.request.user
            )


class LeadActivitiesView(generics.ListCreateAPIView):
    """List and create lead activities"""
    serializer_class = LeadActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        lead_id = self.kwargs.get('lead_id')
        return LeadActivity.objects.filter(lead_id=lead_id).order_by('-created_at')
    
    def perform_create(self, serializer):
        lead_id = self.kwargs.get('lead_id')
        lead = get_object_or_404(Lead, id=lead_id)
        serializer.save(
            lead=lead,
            performed_by=self.request.user
        )


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
    """Sync leads from Angi"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
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
            
            # Fetch leads from Angi API
            leads_data = self._fetch_angi_leads(connection)
            
            created_count = 0
            updated_count = 0
            
            for lead_data in leads_data:
                lead, created = self._create_or_update_lead(lead_data, workspace, connection)
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            # Update last sync time
            connection.last_sync = timezone.now()
            connection.save()
            
            return Response({
                'message': 'Angi leads synced successfully',
                'created': created_count,
                'updated': updated_count,
                'total_processed': len(leads_data)
            })
            
        except AngiConnection.DoesNotExist:
            return Response(
                {'error': 'No active Angi connection found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to sync leads: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _fetch_angi_leads(self, connection):
        """Fetch leads from Angi API"""
        # Mock implementation - replace with actual Angi API call
        return [
            {
                'id': 'angi_lead_123',
                'customer_name': 'John Doe',
                'customer_phone': '+1234567890',
                'customer_email': 'john@example.com',
                'service_type': 'HVAC Repair',
                'location': '123 Main St, City, State 12345',
                'description': 'Air conditioning not working properly',
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
    
    def _create_or_update_lead(self, lead_data, workspace, connection):
        """Create or update lead from Angi data"""
        lead, created = Lead.objects.update_or_create(
            angi_lead_id=lead_data['id'],
            workspace=workspace,
            defaults={
                'lead_number': f"ANGI-{lead_data['id'][-8:].upper()}",
                'source': 'ANGI',
                'customer_name': lead_data['customer_name'],
                'customer_phone': lead_data['customer_phone'],
                'customer_email': lead_data.get('customer_email', ''),
                'service_type': lead_data['service_type'],
                'location': lead_data['location'],
                'description': lead_data['description'],
                'angi_connection': connection
            }
        )
        
        if created:
            # Create initial activity
            LeadActivity.objects.create(
                lead=lead,
                activity_type='NOTE_ADDED',
                description='Lead imported from Angi',
                metadata={'angi_lead_id': lead_data['id']}
            )
            
            # Trigger AI follow-up
            self._trigger_ai_followup(lead)
        
        return lead, created
    
    def _trigger_ai_followup(self, lead):
        """Trigger AI voice agent follow-up for new lead"""
        # This would integrate with AI voice agent system
        lead.ai_contacted = False
        lead.save()


# ==================== Lead Statistics ====================

class LeadStatisticsView(APIView):
    """Lead pipeline statistics"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        workspace_id = request.query_params.get('workspace_id')
        
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
            leads = Lead.objects.filter(workspace=workspace)
        else:
            leads = Lead.objects.all()
        
        # Date filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            leads = leads.filter(created_at__date__gte=date_from)
        if date_to:
            leads = leads.filter(created_at__date__lte=date_to)
        
        # Statistics
        total_leads = leads.count()
        
        # By status
        status_breakdown = leads.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # By source
        source_breakdown = leads.values('source').annotate(
            count=Count('id')
        ).order_by('source')
        
        # Conversion rate
        converted_leads = leads.filter(status='CONVERTED').count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # AI contact stats
        ai_contacted = leads.filter(ai_contacted=True).count()
        ai_contact_rate = (ai_contacted / total_leads * 100) if total_leads > 0 else 0
        
        return Response({
            'summary': {
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'conversion_rate': round(conversion_rate, 2),
                'ai_contacted': ai_contacted,
                'ai_contact_rate': round(ai_contact_rate, 2)
            },
            'status_breakdown': list(status_breakdown),
            'source_breakdown': list(source_breakdown)
        })