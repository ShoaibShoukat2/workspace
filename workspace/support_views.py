from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum
import uuid

from .models import (
    SupportTicket, SupportMessage, Workspace, Contractor, CustomerProfile
)
from .serializers import (
    SupportTicketSerializer, SupportMessageSerializer
)
from authentication.permissions import IsContractor, IsCustomer, IsAdmin


# ==================== Support Ticket Management ====================

class CreateSupportTicketView(APIView):
    """Create a new support ticket"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        subject = request.data.get('subject')
        description = request.data.get('description')
        category = request.data.get('category', 'GENERAL')
        priority = request.data.get('priority', 'MEDIUM')
        workspace_id = request.data.get('workspace_id')
        
        if not subject or not description:
            return Response(
                {'error': 'Subject and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get workspace
        workspace = None
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        else:
            # Try to get user's primary workspace
            if hasattr(request.user, 'contractor_profiles'):
                contractor = request.user.contractor_profiles.first()
                if contractor:
                    workspace = contractor.workspace
            elif hasattr(request.user, 'customer_profile'):
                workspace = request.user.customer_profile.workspace
        
        if not workspace:
            return Response(
                {'error': 'Workspace is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate ticket number
        ticket_number = f"TICK-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket
        ticket = SupportTicket.objects.create(
            ticket_number=ticket_number,
            user=request.user,
            workspace=workspace,
            subject=subject,
            description=description,
            category=category,
            priority=priority
        )
        
        # Create initial message
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=description,
            is_internal=False
        )
        
        return Response({
            'ticket_number': ticket_number,
            'message': 'Support ticket created successfully',
            'ticket': SupportTicketSerializer(ticket).data
        }, status=status.HTTP_201_CREATED)


class SupportTicketListView(generics.ListAPIView):
    """List user's support tickets"""
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by user's tickets
        queryset = SupportTicket.objects.filter(user=user).order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset


class SupportTicketDetailView(APIView):
    """Get support ticket details with messages"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, ticket_number):
        ticket = get_object_or_404(
            SupportTicket,
            ticket_number=ticket_number,
            user=request.user
        )
        
        # Get messages
        messages = SupportMessage.objects.filter(
            ticket=ticket,
            is_internal=False  # Only show non-internal messages to users
        ).order_by('created_at')
        
        ticket_data = SupportTicketSerializer(ticket).data
        ticket_data['messages'] = SupportMessageSerializer(messages, many=True).data
        
        return Response(ticket_data)


class AddSupportMessageView(APIView):
    """Add message to support ticket"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ticket_number):
        ticket = get_object_or_404(
            SupportTicket,
            ticket_number=ticket_number,
            user=request.user
        )
        
        message_text = request.data.get('message')
        if not message_text:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create message
        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
            is_internal=False
        )
        
        # Update ticket status if it was resolved
        if ticket.status == 'RESOLVED':
            ticket.status = 'OPEN'
            ticket.save()
        
        return Response({
            'message': 'Message added successfully',
            'message_data': SupportMessageSerializer(message).data
        })


# ==================== Admin Support Management ====================

class AdminSupportTicketsView(generics.ListAPIView):
    """Admin view of all support tickets"""
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = SupportTicket.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by assigned admin
        assigned_filter = self.request.query_params.get('assigned_to')
        if assigned_filter:
            queryset = queryset.filter(assigned_to__email=assigned_filter)
        
        # Filter by workspace
        workspace_filter = self.request.query_params.get('workspace')
        if workspace_filter:
            queryset = queryset.filter(workspace__workspace_id=workspace_filter)
        
        return queryset


class AdminSupportTicketDetailView(APIView):
    """Admin detailed view of support ticket"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, ticket_number):
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        
        # Get all messages (including internal)
        messages = SupportMessage.objects.filter(ticket=ticket).order_by('created_at')
        
        ticket_data = SupportTicketSerializer(ticket).data
        ticket_data['messages'] = SupportMessageSerializer(messages, many=True).data
        
        return Response(ticket_data)
    
    def patch(self, request, ticket_number):
        """Update ticket status, priority, or assignment"""
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        
        # Update fields
        if 'status' in request.data:
            ticket.status = request.data['status']
            if request.data['status'] == 'RESOLVED':
                ticket.resolved_at = timezone.now()
        
        if 'priority' in request.data:
            ticket.priority = request.data['priority']
        
        if 'assigned_to' in request.data:
            if request.data['assigned_to']:
                from authentication.models import User
                assigned_user = get_object_or_404(User, email=request.data['assigned_to'])
                ticket.assigned_to = assigned_user
            else:
                ticket.assigned_to = None
        
        ticket.save()
        
        return Response({
            'message': 'Ticket updated successfully',
            'ticket': SupportTicketSerializer(ticket).data
        })


class AdminAddSupportMessageView(APIView):
    """Admin add message to support ticket"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, ticket_number):
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        
        message_text = request.data.get('message')
        is_internal = request.data.get('is_internal', False)
        
        if not message_text:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create message
        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
            is_internal=is_internal
        )
        
        # Update ticket status
        if ticket.status == 'OPEN':
            ticket.status = 'IN_PROGRESS'
            ticket.save()
        
        return Response({
            'message': 'Message added successfully',
            'message_data': SupportMessageSerializer(message).data
        })


# ==================== Support Statistics ====================

class SupportStatisticsView(APIView):
    """Support system statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Ticket counts by status
        status_counts = SupportTicket.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Ticket counts by priority
        priority_counts = SupportTicket.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # Average resolution time
        resolved_tickets = SupportTicket.objects.filter(
            status='RESOLVED',
            resolved_at__isnull=False
        )
        
        avg_resolution_hours = 0
        if resolved_tickets.exists():
            total_hours = sum([
                (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                for ticket in resolved_tickets
            ])
            avg_resolution_hours = total_hours / resolved_tickets.count()
        
        # Tickets by workspace
        workspace_counts = SupportTicket.objects.values(
            'workspace__name',
            'workspace__workspace_id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent activity
        recent_tickets = SupportTicket.objects.order_by('-created_at')[:10]
        recent_activity = [{
            'ticket_number': ticket.ticket_number,
            'subject': ticket.subject,
            'user_email': ticket.user.email,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at
        } for ticket in recent_tickets]
        
        return Response({
            'summary': {
                'total_tickets': SupportTicket.objects.count(),
                'open_tickets': SupportTicket.objects.filter(status='OPEN').count(),
                'in_progress_tickets': SupportTicket.objects.filter(status='IN_PROGRESS').count(),
                'resolved_tickets': SupportTicket.objects.filter(status='RESOLVED').count(),
                'average_resolution_hours': round(avg_resolution_hours, 2)
            },
            'status_breakdown': list(status_counts),
            'priority_breakdown': list(priority_counts),
            'workspace_breakdown': list(workspace_counts),
            'recent_activity': recent_activity
        })


# ==================== FAQ and Automated Support ====================

class SupportFAQView(APIView):
    """Frequently Asked Questions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # This would typically come from a database or CMS
        # For now, we'll return static FAQ data
        
        contractor_faqs = [
            {
                'question': 'How do I accept a job assignment?',
                'answer': 'Go to your dashboard and click on "Job Assignments". You\'ll see pending assignments where you can click "Accept" or "Reject".',
                'category': 'JOB_MANAGEMENT'
            },
            {
                'question': 'How do I upload photos for job completion?',
                'answer': 'In the job detail page, go to the checklist section. Each step allows you to upload photos and videos as proof of completion.',
                'category': 'JOB_COMPLETION'
            },
            {
                'question': 'When will I get paid?',
                'answer': 'Payments are processed after job completion and verification. You can check your wallet balance and request payouts from the Wallet section.',
                'category': 'PAYMENTS'
            },
            {
                'question': 'How do I update my compliance documents?',
                'answer': 'Go to the Compliance section in your dashboard to upload and manage your licenses, insurance, and other required documents.',
                'category': 'COMPLIANCE'
            }
        ]
        
        customer_faqs = [
            {
                'question': 'How can I track my technician?',
                'answer': 'Once a technician is assigned and en route, you\'ll see live GPS tracking on your job detail page with estimated arrival time.',
                'category': 'JOB_TRACKING'
            },
            {
                'question': 'How do I report an issue with work?',
                'answer': 'In your job detail page, click "Report Issue" to file a complaint or concern about the work performed.',
                'category': 'ISSUES'
            },
            {
                'question': 'Can I reschedule my appointment?',
                'answer': 'Contact support to reschedule your appointment. We\'ll work with you and the technician to find a suitable time.',
                'category': 'SCHEDULING'
            }
        ]
        
        # Filter by user role
        if hasattr(request.user, 'contractor_profiles') and request.user.contractor_profiles.exists():
            faqs = contractor_faqs
        else:
            faqs = customer_faqs
        
        # Filter by category if provided
        category_filter = request.query_params.get('category')
        if category_filter:
            faqs = [faq for faq in faqs if faq['category'] == category_filter]
        
        return Response({
            'faqs': faqs,
            'categories': list(set([faq['category'] for faq in faqs]))
        })


class SupportGuidedHelpView(APIView):
    """Guided help system"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        issue_type = request.query_params.get('issue_type')
        
        # Guided help flows based on issue type
        help_flows = {
            'job_assignment': {
                'title': 'Job Assignment Help',
                'steps': [
                    'Check your email for job assignment notification',
                    'Log into your contractor dashboard',
                    'Go to "Job Assignments" section',
                    'Review job details carefully',
                    'Click "Accept" if you can complete the job',
                    'If you need to reject, provide a reason'
                ],
                'related_faqs': ['How do I accept a job assignment?']
            },
            'payment_issue': {
                'title': 'Payment Issue Help',
                'steps': [
                    'Check your wallet balance in the dashboard',
                    'Verify job completion status',
                    'Ensure all compliance documents are approved',
                    'Check if payout request was submitted',
                    'Contact support if payment is overdue'
                ],
                'related_faqs': ['When will I get paid?']
            },
            'job_tracking': {
                'title': 'Job Tracking Help',
                'steps': [
                    'Open your job detail page',
                    'Check if technician is assigned',
                    'Look for "Tracking" section with live updates',
                    'GPS location shows when technician is en route',
                    'You\'ll receive notifications for status changes'
                ],
                'related_faqs': ['How can I track my technician?']
            }
        }
        
        if issue_type and issue_type in help_flows:
            return Response(help_flows[issue_type])
        else:
            return Response({
                'available_flows': list(help_flows.keys()),
                'flows': help_flows
            })