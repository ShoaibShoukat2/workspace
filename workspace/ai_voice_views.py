"""
AI Voice Agent System Views
Lead handling, conversation management, and Twilio integration
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

# Twilio imports - install with: pip install twilio
try:
    from twilio.rest import Client
    from twilio.twiml import VoiceResponse, MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    # Mock classes for development
    class Client:
        def __init__(self, *args, **kwargs):
            pass
    class VoiceResponse:
        def __init__(self):
            pass
        def say(self, *args, **kwargs):
            pass
        def dial(self, *args, **kwargs):
            pass
        def __str__(self):
            return '<Response></Response>'
    class MessagingResponse:
        def __init__(self):
            pass

from .models import (
    Lead, AIConversation, TwilioIntegration, CommunicationLog, 
    Workspace, LeadActivity
)
from .serializers import (
    AIConversationSerializer, CommunicationLogSerializer, TwilioIntegrationSerializer
)
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== AI Voice Agent Management ====================

class TriggerAIContactView(APIView):
    """Trigger AI voice agent to contact a lead"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        
        if lead.ai_contacted:
            return Response(
                {'error': 'Lead has already been contacted by AI'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get Twilio integration for workspace
            twilio_integration = TwilioIntegration.objects.get(
                workspace=lead.workspace
            )
            
            # Send initial text message
            result = self._send_initial_text(lead, twilio_integration)
            
            # Create AI conversation record
            conversation = AIConversation.objects.create(
                lead=lead,
                conversation_type='INITIAL_CONTACT',
                phone_number=lead.customer_phone,
                preferred_method='TEXT'  # Start with text
            )
            
            # Mark lead as contacted
            lead.ai_contacted = True
            lead.save()
            
            # Log activity
            LeadActivity.objects.create(
                lead=lead,
                activity_type='AI_TEXT_SENT',
                description='AI sent initial contact text message',
                metadata={'conversation_id': conversation.id}
            )
            
            return Response({
                'message': 'AI contact initiated successfully',
                'conversation': AIConversationSerializer(conversation).data,
                'twilio_result': result
            })
            
        except TwilioIntegration.DoesNotExist:
            return Response(
                {'error': 'Twilio integration not configured for this workspace'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to initiate AI contact: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_initial_text(self, lead, twilio_integration):
        """Send initial text message to lead"""
        client = Client(twilio_integration.account_sid, twilio_integration.auth_token)
        
        message_body = f"""Hi {lead.customer_name}! This is Apex regarding your {lead.service_type} request. 

Would you prefer to:
1. Schedule a quick call
2. Continue via text

Reply 1 for call or 2 for text. Thanks!"""
        
        try:
            message = client.messages.create(
                body=message_body,
                from_=twilio_integration.phone_number,
                to=lead.customer_phone
            )
            
            # Log communication
            CommunicationLog.objects.create(
                workspace=lead.workspace,
                lead=lead,
                message_type='SMS_OUTBOUND',
                status='SENT',
                from_number=twilio_integration.phone_number,
                to_number=lead.customer_phone,
                message_body=message_body,
                twilio_sid=message.sid
            )
            
            return {
                'status': 'success',
                'message_sid': message.sid,
                'message_status': message.status
            }
            
        except Exception as e:
            # Log failed communication
            CommunicationLog.objects.create(
                workspace=lead.workspace,
                lead=lead,
                message_type='SMS_OUTBOUND',
                status='FAILED',
                from_number=twilio_integration.phone_number,
                to_number=lead.customer_phone,
                message_body=message_body,
                error_message=str(e)
            )
            
            raise e


class AIConversationListView(generics.ListAPIView):
    """List AI conversations"""
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = AIConversation.objects.all().order_by('-created_at')
        
        # Filter by lead
        lead_id = self.request.query_params.get('lead_id')
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by conversation type
        conversation_type = self.request.query_params.get('type')
        if conversation_type:
            queryset = queryset.filter(conversation_type=conversation_type)
        
        return queryset


class AIConversationDetailView(generics.RetrieveAPIView):
    """Get AI conversation details"""
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    queryset = AIConversation.objects.all()


# ==================== Twilio Webhook Handlers ====================

class TwilioSMSWebhookView(APIView):
    """Handle incoming SMS from Twilio"""
    permission_classes = []  # Public webhook
    
    def post(self, request):
        # Get Twilio data
        from_number = request.data.get('From')
        to_number = request.data.get('To')
        message_body = request.data.get('Body', '').strip()
        message_sid = request.data.get('MessageSid')
        
        try:
            # Find the lead and conversation
            lead = Lead.objects.filter(customer_phone=from_number).first()
            if not lead:
                return Response({'error': 'Lead not found'}, status=404)
            
            # Get active conversation
            conversation = AIConversation.objects.filter(
                lead=lead,
                status__in=['INITIATED', 'IN_PROGRESS']
            ).first()
            
            if not conversation:
                # Create new conversation
                conversation = AIConversation.objects.create(
                    lead=lead,
                    conversation_type='FOLLOW_UP',
                    phone_number=from_number,
                    preferred_method='TEXT',
                    status='IN_PROGRESS'
                )
            
            # Log incoming message
            CommunicationLog.objects.create(
                workspace=lead.workspace,
                lead=lead,
                ai_conversation=conversation,
                message_type='SMS_INBOUND',
                status='RECEIVED',
                from_number=from_number,
                to_number=to_number,
                message_body=message_body,
                twilio_sid=message_sid
            )
            
            # Process AI response
            ai_response = self._process_ai_response(conversation, message_body)
            
            # Send AI response
            if ai_response:
                self._send_ai_response(conversation, ai_response)
            
            return Response({'status': 'processed'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def _process_ai_response(self, conversation, customer_message):
        """Process customer message and generate AI response"""
        customer_message_lower = customer_message.lower()
        
        # Update conversation data
        conversation.customer_responses.append({
            'message': customer_message,
            'timestamp': timezone.now().isoformat()
        })
        
        # Simple AI logic (replace with actual AI/NLP)
        if '1' in customer_message or 'call' in customer_message_lower:
            # Customer wants a call
            conversation.preferred_method = 'CALL'
            conversation.save()
            
            # Schedule call
            self._schedule_ai_call(conversation)
            
            return f"Perfect! I'll call you in the next few minutes to discuss your {conversation.lead.service_type} needs. Thanks!"
            
        elif '2' in customer_message or 'text' in customer_message_lower:
            # Customer wants to continue via text
            conversation.preferred_method = 'TEXT'
            conversation.save()
            
            return f"Great! Let's continue via text. Can you tell me more about your {conversation.lead.service_type} needs? What specific work are you looking to have done?"
            
        elif any(word in customer_message_lower for word in ['schedule', 'appointment', 'when', 'time']):
            # Customer asking about scheduling
            return "I'd be happy to help schedule an appointment! What days and times work best for you? We typically have availability Monday-Friday 8am-6pm and Saturday 9am-4pm."
            
        elif any(word in customer_message_lower for word in ['price', 'cost', 'estimate', 'quote']):
            # Customer asking about pricing
            return "We provide free estimates! Our team will assess your specific needs and provide a detailed quote. Would you like to schedule a time for our specialist to visit and provide an estimate?"
            
        else:
            # General response
            return "Thanks for that information! To better assist you, would you like to schedule a quick call to discuss your project details, or would you prefer I connect you with one of our specialists for a free estimate?"
    
    def _send_ai_response(self, conversation, response_text):
        """Send AI response via SMS"""
        try:
            twilio_integration = TwilioIntegration.objects.get(
                workspace=conversation.lead.workspace
            )
            
            client = Client(twilio_integration.account_sid, twilio_integration.auth_token)
            
            message = client.messages.create(
                body=response_text,
                from_=twilio_integration.phone_number,
                to=conversation.phone_number
            )
            
            # Update conversation
            conversation.ai_responses.append({
                'message': response_text,
                'timestamp': timezone.now().isoformat()
            })
            conversation.save()
            
            # Log communication
            CommunicationLog.objects.create(
                workspace=conversation.lead.workspace,
                lead=conversation.lead,
                ai_conversation=conversation,
                message_type='SMS_OUTBOUND',
                status='SENT',
                from_number=twilio_integration.phone_number,
                to_number=conversation.phone_number,
                message_body=response_text,
                twilio_sid=message.sid
            )
            
        except Exception as e:
            print(f"Failed to send AI response: {e}")
    
    def _schedule_ai_call(self, conversation):
        """Schedule AI call to customer"""
        # This would integrate with actual AI calling system
        # For now, just update the conversation
        conversation.conversation_type = 'APPOINTMENT_SCHEDULING'
        conversation.save()
        
        # Log activity
        LeadActivity.objects.create(
            lead=conversation.lead,
            activity_type='AI_CALL_MADE',
            description='AI call scheduled based on customer preference',
            metadata={'conversation_id': conversation.id}
        )


class TwilioVoiceWebhookView(APIView):
    """Handle incoming voice calls from Twilio"""
    permission_classes = []  # Public webhook
    
    def post(self, request):
        from_number = request.data.get('From')
        to_number = request.data.get('To')
        call_sid = request.data.get('CallSid')
        
        try:
            # Find the lead
            lead = Lead.objects.filter(customer_phone=from_number).first()
            
            # Create TwiML response
            response = VoiceResponse()
            
            if lead:
                # AI voice response for known lead
                response.say(
                    f"Hello {lead.customer_name}! Thank you for calling Apex. "
                    f"I understand you're interested in {lead.service_type}. "
                    f"Let me connect you with one of our specialists who can help you right away.",
                    voice='alice'
                )
                
                # Forward to human agent (replace with actual number)
                response.dial('+1234567890')  # Apex office number
                
                # Log the call
                if lead:
                    CommunicationLog.objects.create(
                        workspace=lead.workspace,
                        lead=lead,
                        message_type='VOICE_INBOUND',
                        status='RECEIVED',
                        from_number=from_number,
                        to_number=to_number,
                        twilio_sid=call_sid
                    )
            else:
                # Unknown caller
                response.say(
                    "Thank you for calling Apex. Please hold while we connect you with our team.",
                    voice='alice'
                )
                response.dial('+1234567890')  # Apex office number
            
            return Response(str(response), content_type='application/xml')
            
        except Exception as e:
            # Fallback response
            response = VoiceResponse()
            response.say("We're sorry, but we're experiencing technical difficulties. Please try calling back later.")
            return Response(str(response), content_type='application/xml')


# ==================== Twilio Integration Management ====================

class TwilioIntegrationView(APIView):
    """Manage Twilio integration settings"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        workspace_id = request.query_params.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        try:
            integration = TwilioIntegration.objects.get(workspace=workspace)
            return Response(TwilioIntegrationSerializer(integration).data)
        except TwilioIntegration.DoesNotExist:
            return Response({
                'configured': False,
                'message': 'Twilio integration not configured'
            })
    
    def post(self, request):
        """Configure Twilio integration"""
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        
        account_sid = request.data.get('account_sid')
        auth_token = request.data.get('auth_token')
        phone_number = request.data.get('phone_number')
        
        if not all([account_sid, auth_token, phone_number]):
            return Response(
                {'error': 'account_sid, auth_token, and phone_number are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Test Twilio credentials
        try:
            client = Client(account_sid, auth_token)
            # Test by fetching account info
            account = client.api.accounts(account_sid).fetch()
            
            # Create or update integration
            integration, created = TwilioIntegration.objects.update_or_create(
                workspace=workspace,
                defaults={
                    'account_sid': account_sid,
                    'auth_token': auth_token,
                    'phone_number': phone_number,
                    'sms_enabled': request.data.get('sms_enabled', True),
                    'voice_enabled': request.data.get('voice_enabled', True),
                    'recording_enabled': request.data.get('recording_enabled', False)
                }
            )
            
            return Response({
                'message': 'Twilio integration configured successfully',
                'integration': TwilioIntegrationSerializer(integration).data,
                'account_name': account.friendly_name
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to configure Twilio: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CommunicationLogView(generics.ListAPIView):
    """List communication logs"""
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = CommunicationLog.objects.all().order_by('-created_at')
        
        # Filter by lead
        lead_id = self.request.query_params.get('lead_id')
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)
        
        # Filter by message type
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset


# ==================== AI Analytics ====================

class AIPerformanceAnalyticsView(APIView):
    """AI voice agent performance analytics"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        workspace_id = request.query_params.get('workspace_id')
        
        if workspace_id:
            workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
            conversations = AIConversation.objects.filter(lead__workspace=workspace)
            communications = CommunicationLog.objects.filter(workspace=workspace)
        else:
            conversations = AIConversation.objects.all()
            communications = CommunicationLog.objects.all()
        
        # Date filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            conversations = conversations.filter(created_at__date__gte=date_from)
            communications = communications.filter(created_at__date__gte=date_from)
        if date_to:
            conversations = conversations.filter(created_at__date__lte=date_to)
            communications = communications.filter(created_at__date__lte=date_to)
        
        # Conversation statistics
        total_conversations = conversations.count()
        completed_conversations = conversations.filter(status='COMPLETED').count()
        appointments_scheduled = conversations.filter(appointment_scheduled=True).count()
        
        # Communication statistics
        total_messages = communications.filter(message_type__in=['SMS_OUTBOUND', 'SMS_INBOUND']).count()
        total_calls = communications.filter(message_type__in=['VOICE_OUTBOUND', 'VOICE_INBOUND']).count()
        
        # Success rates
        completion_rate = (completed_conversations / total_conversations * 100) if total_conversations > 0 else 0
        appointment_rate = (appointments_scheduled / total_conversations * 100) if total_conversations > 0 else 0
        
        # Response time analysis
        response_times = []
        for conversation in conversations.filter(status='COMPLETED'):
            if conversation.customer_responses and conversation.ai_responses:
                # Calculate average response time (simplified)
                response_times.append(30)  # Mock 30 seconds average
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return Response({
            'summary': {
                'total_conversations': total_conversations,
                'completed_conversations': completed_conversations,
                'appointments_scheduled': appointments_scheduled,
                'completion_rate': round(completion_rate, 2),
                'appointment_rate': round(appointment_rate, 2),
                'avg_response_time_seconds': round(avg_response_time, 2)
            },
            'communication_stats': {
                'total_messages': total_messages,
                'total_calls': total_calls,
                'outbound_messages': communications.filter(message_type='SMS_OUTBOUND').count(),
                'inbound_messages': communications.filter(message_type='SMS_INBOUND').count()
            }
        })