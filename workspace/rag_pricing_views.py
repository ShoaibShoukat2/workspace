"""
RAG Pricing Service Views
AI-powered pricing using Retrieval Augmented Generation
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import json
import uuid
from decimal import Decimal

from .models import Job, JobEvaluation, JobQuote, MaterialSuggestion
from authentication.permissions import IsContractor, IsAdminOrFM


class RAGPricingServiceView(APIView):
    """Endpoint 30: RAG Pricing Service Integration"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, job_id):
        """Generate AI-powered pricing using RAG system"""
        job = get_object_or_404(Job, id=job_id)
        
        try:
            evaluation = job.evaluation
        except JobEvaluation.DoesNotExist:
            return Response(
                {'error': 'Job evaluation required for pricing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract context for RAG system
        context = {
            'location': job.customer_address,
            'scope': evaluation.scope,
            'measurements': evaluation.measurements_data,
            'room_count': evaluation.room_count,
            'square_feet': float(evaluation.square_feet) if evaluation.square_feet else 0,
            'labor_required': evaluation.labor_required,
            'estimated_hours': float(evaluation.estimated_hours) if evaluation.estimated_hours else 0,
            'tools_required': evaluation.tools_required,
            'safety_concerns': evaluation.safety_concerns
        }
        
        # Call RAG pricing service (mock implementation)
        pricing_result = self._call_rag_pricing_service(context)
        
        # Create quote
        quote_id = f"RAG-{str(uuid.uuid4())[:8].upper()}"
        
        quote = JobQuote.objects.create(
            job=job,
            quote_id=quote_id,
            gbb_total=pricing_result['gbb_total'],
            evaluation_fee=job.evaluation_fee,
            total_after_credit=pricing_result['gbb_total'] - job.evaluation_fee,
            line_items=pricing_result['line_items'],
            generation_context=context
        )
        
        return Response({
            'quote_id': quote.quote_id,
            'gbb_total': float(quote.gbb_total),
            'evaluation_fee': float(quote.evaluation_fee),
            'total_after_credit': float(quote.total_after_credit),
            'line_items': quote.line_items,
            'confidence_score': pricing_result.get('confidence_score', 0.85),
            'comparable_jobs': pricing_result.get('comparable_jobs', [])
        })
    
    def _call_rag_pricing_service(self, context):
        """Mock RAG pricing service call"""
        # In production, this would call actual RAG/AI service
        
        base_rate = 75  # $75/hour base rate
        hours = context.get('estimated_hours', 8)
        square_feet = context.get('square_feet', 500)
        room_count = context.get('room_count', 2)
        
        # Calculate pricing based on context
        labor_cost = hours * base_rate
        
        # Area-based pricing adjustments
        if square_feet > 1000:
            labor_cost *= 1.2
        elif square_feet < 200:
            labor_cost *= 0.9
        
        # Room complexity adjustment
        if room_count > 3:
            labor_cost *= 1.1
        
        # Material overhead (20%)
        material_overhead = labor_cost * 0.2
        
        # Profit margin (15%)
        profit_margin = labor_cost * 0.15
        
        gbb_total = labor_cost + material_overhead + profit_margin
        
        line_items = [
            {
                'category': 'Labor',
                'description': f'Professional painting - {hours} hours',
                'quantity': hours,
                'rate': base_rate,
                'amount': labor_cost
            },
            {
                'category': 'Materials & Overhead',
                'description': 'Material costs and project overhead',
                'quantity': 1,
                'rate': material_overhead,
                'amount': material_overhead
            },
            {
                'category': 'Profit Margin',
                'description': 'Business profit and contingency',
                'quantity': 1,
                'rate': profit_margin,
                'amount': profit_margin
            }
        ]
        
        return {
            'gbb_total': Decimal(str(round(gbb_total, 2))),
            'line_items': line_items,
            'confidence_score': 0.87,
            'comparable_jobs': [
                {'job_id': 'J-2024-001', 'similarity': 0.92, 'price': gbb_total * 0.95},
                {'job_id': 'J-2024-015', 'similarity': 0.88, 'price': gbb_total * 1.05}
            ]
        }


class RAGPricingAnalyticsView(APIView):
    """Analytics for RAG pricing accuracy"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        """Get RAG pricing analytics"""
        # Mock analytics data
        return Response({
            'total_quotes_generated': 156,
            'average_confidence_score': 0.84,
            'accuracy_rate': 0.91,
            'price_variance': {
                'mean': 0.08,
                'std_dev': 0.12
            },
            'performance_by_category': {
                'interior_painting': {'accuracy': 0.93, 'count': 89},
                'exterior_painting': {'accuracy': 0.87, 'count': 45},
                'mixed_projects': {'accuracy': 0.89, 'count': 22}
            }
        })