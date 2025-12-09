"""
AI-Assisted Features Module
Job descriptions, checklist suggestions, anomaly detection, smart recommendations
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from decimal import Decimal
import re

from .models import Job, Estimate, EstimateLineItem, JobChecklist, ChecklistStep, Contractor
from authentication.permissions import IsAdminOrFM


# ==================== AI Job Description Generator ====================

class AIGenerateJobDescriptionView(APIView):
    """Generate AI job description based on title and basic info"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        job_title = request.data.get('job_title', '')
        job_type = request.data.get('job_type', '')
        location = request.data.get('location', '')
        
        if not job_title:
            return Response(
                {'error': 'Job title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # AI-generated description based on job type
        description = self._generate_description(job_title, job_type, location)
        
        return Response({
            'job_title': job_title,
            'generated_description': description,
            'suggestions': self._get_description_suggestions(job_title, job_type)
        })

    
    def _generate_description(self, title, job_type, location):
        """Generate detailed job description"""
        title_lower = title.lower()
        
        # Template-based generation
        templates = {
            'bathroom': f"""Complete bathroom renovation project at {location or 'specified location'}.

Scope of Work:
- Remove existing fixtures and tiles
- Install new plumbing fixtures (toilet, sink, shower/tub)
- Tile installation (walls and floor)
- Electrical work (lighting, outlets, ventilation)
- Painting and finishing work
- Final cleanup and inspection

Requirements:
- Licensed plumber for fixture installation
- Certified electrician for electrical work
- Experienced tile installer
- All work must meet local building codes
- Proper ventilation system installation

Timeline: Estimated 2-3 weeks depending on scope
Quality Standards: High-quality materials and workmanship required""",
            
            'kitchen': f"""Complete kitchen remodeling project at {location or 'specified location'}.

Scope of Work:
- Cabinet removal and installation
- Countertop installation (granite/quartz)
- Appliance installation
- Plumbing work (sink, dishwasher connections)
- Electrical work (outlets, lighting, appliances)
- Backsplash installation
- Flooring installation
- Painting and finishing

Requirements:
- Licensed contractors for plumbing and electrical
- Experienced cabinet installers
- Countertop fabrication and installation
- All work must comply with building codes
- Proper ventilation and safety measures

Timeline: Estimated 3-4 weeks
Quality Standards: Premium materials and professional installation""",
            
            'painting': f"""Professional painting project at {location or 'specified location'}.

Scope of Work:
- Surface preparation (cleaning, sanding, patching)
- Primer application where needed
- Paint application (2-3 coats)
- Trim and detail work
- Final touch-ups and cleanup

Requirements:
- Professional grade paint and materials
- Proper surface preparation
- Clean and neat work area
- Protection of furniture and flooring
- Proper ventilation during work

Timeline: Estimated 3-5 days depending on area
Quality Standards: Smooth, even finish with no drips or streaks""",
            
            'plumbing': f"""Plumbing repair/installation project at {location or 'specified location'}.

Scope of Work:
- Inspection of existing plumbing system
- Repair or replacement of fixtures
- Pipe installation/repair as needed
- Leak detection and repair
- Water pressure testing
- Final inspection and testing

Requirements:
- Licensed and insured plumber
- Quality plumbing materials
- Compliance with local plumbing codes
- Proper permits if required
- Warranty on work performed

Timeline: Varies based on scope (1-5 days typical)
Quality Standards: No leaks, proper water pressure, code compliant""",
            
            'electrical': f"""Electrical work project at {location or 'specified location'}.

Scope of Work:
- Electrical system inspection
- Wiring installation/repair
- Outlet and switch installation
- Lighting fixture installation
- Circuit breaker work if needed
- Safety testing and verification

Requirements:
- Licensed and certified electrician
- Code-compliant materials and methods
- Proper permits obtained
- Safety inspections completed
- Warranty on electrical work

Timeline: Varies based on scope (1-3 days typical)
Quality Standards: Safe, code-compliant, properly functioning system""",
            
            'flooring': f"""Flooring installation project at {location or 'specified location'}.

Scope of Work:
- Remove existing flooring if needed
- Subfloor preparation and leveling
- New flooring installation
- Trim and transition installation
- Final cleanup and inspection

Requirements:
- Experienced flooring installer
- Quality flooring materials
- Proper subfloor preparation
- Moisture barrier if needed
- Professional installation techniques

Timeline: Estimated 2-5 days depending on area
Quality Standards: Level, secure, professional appearance""",
            
            'hvac': f"""HVAC installation/repair project at {location or 'specified location'}.

Scope of Work:
- System inspection and assessment
- Equipment installation or repair
- Ductwork installation/repair if needed
- Thermostat installation
- System testing and calibration
- Air quality verification

Requirements:
- Licensed HVAC technician
- Quality HVAC equipment
- Proper sizing and installation
- Code compliance
- Warranty on equipment and labor

Timeline: 1-3 days typical
Quality Standards: Efficient operation, proper temperature control""",
            
            'roofing': f"""Roofing project at {location or 'specified location'}.

Scope of Work:
- Roof inspection and assessment
- Remove old roofing materials if needed
- Repair roof deck if necessary
- Install underlayment and flashing
- Install new roofing material
- Cleanup and final inspection

Requirements:
- Licensed roofing contractor
- Quality roofing materials
- Proper installation techniques
- Weather-appropriate scheduling
- Warranty on materials and labor

Timeline: 2-5 days depending on size
Quality Standards: Watertight, durable, professionally installed""",
        }
        
        # Find matching template
        for key, template in templates.items():
            if key in title_lower:
                return template
        
        # Default generic template
        return f"""Project: {title}
Location: {location or 'To be specified'}

Scope of Work:
- Detailed assessment of project requirements
- Planning and preparation
- Execution of work according to specifications
- Quality control and inspection
- Final cleanup and handover

Requirements:
- Qualified and experienced contractors
- Quality materials and workmanship
- Compliance with all applicable codes and regulations
- Proper safety measures
- Professional project management

Timeline: To be determined based on project scope
Quality Standards: High-quality work meeting industry standards"""
    
    def _get_description_suggestions(self, title, job_type):
        """Get suggestions for improving description"""
        suggestions = [
            "Include specific materials to be used",
            "Add estimated timeline for completion",
            "Specify quality standards expected",
            "List required certifications or licenses",
            "Include safety requirements",
            "Add cleanup and disposal requirements"
        ]
        
        return suggestions


# ==================== AI Checklist Suggestions ====================

class AIGenerateChecklistView(APIView):
    """Generate AI checklist suggestions based on job type"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        job_id = request.data.get('job_id')
        job_title = request.data.get('job_title', '')
        job_type = request.data.get('job_type', '')
        
        if not job_title:
            return Response(
                {'error': 'Job title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate checklist based on job type
        checklist_items = self._generate_checklist(job_title, job_type)
        
        return Response({
            'job_title': job_title,
            'suggested_checklist': checklist_items,
            'total_steps': len(checklist_items)
        })

    
    def _generate_checklist(self, title, job_type):
        """Generate checklist items based on job type"""
        title_lower = title.lower()
        
        checklists = {
            'bathroom': [
                {'step': 1, 'title': 'Initial Site Assessment', 'description': 'Inspect existing bathroom, take measurements, identify issues'},
                {'step': 2, 'title': 'Demolition', 'description': 'Remove old fixtures, tiles, and materials safely'},
                {'step': 3, 'title': 'Plumbing Rough-In', 'description': 'Install/update water supply and drain lines'},
                {'step': 4, 'title': 'Electrical Rough-In', 'description': 'Install wiring for lights, outlets, and ventilation'},
                {'step': 5, 'title': 'Drywall & Waterproofing', 'description': 'Install cement board, waterproof membrane'},
                {'step': 6, 'title': 'Tile Installation', 'description': 'Install floor and wall tiles, grout work'},
                {'step': 7, 'title': 'Fixture Installation', 'description': 'Install toilet, sink, shower/tub, faucets'},
                {'step': 8, 'title': 'Vanity & Cabinet Installation', 'description': 'Install vanity, cabinets, mirrors'},
                {'step': 9, 'title': 'Painting & Finishing', 'description': 'Paint walls, install trim, caulking'},
                {'step': 10, 'title': 'Final Inspection & Cleanup', 'description': 'Test all fixtures, clean thoroughly, final walkthrough'},
            ],
            
            'kitchen': [
                {'step': 1, 'title': 'Initial Assessment', 'description': 'Measure space, assess existing conditions'},
                {'step': 2, 'title': 'Demolition', 'description': 'Remove old cabinets, countertops, appliances'},
                {'step': 3, 'title': 'Plumbing Work', 'description': 'Update water lines, install dishwasher connections'},
                {'step': 4, 'title': 'Electrical Work', 'description': 'Install outlets, lighting, appliance circuits'},
                {'step': 5, 'title': 'Cabinet Installation', 'description': 'Install base and wall cabinets, ensure level'},
                {'step': 6, 'title': 'Countertop Installation', 'description': 'Template, fabricate, install countertops'},
                {'step': 7, 'title': 'Backsplash Installation', 'description': 'Install tile or other backsplash material'},
                {'step': 8, 'title': 'Appliance Installation', 'description': 'Install and connect all appliances'},
                {'step': 9, 'title': 'Flooring Installation', 'description': 'Install new flooring if included'},
                {'step': 10, 'title': 'Final Touches', 'description': 'Install hardware, paint, final cleanup'},
            ],
            
            'painting': [
                {'step': 1, 'title': 'Surface Preparation', 'description': 'Clean walls, fill holes, sand rough areas'},
                {'step': 2, 'title': 'Protection Setup', 'description': 'Cover floors, furniture, tape edges'},
                {'step': 3, 'title': 'Primer Application', 'description': 'Apply primer where needed, let dry'},
                {'step': 4, 'title': 'First Coat', 'description': 'Apply first coat of paint evenly'},
                {'step': 5, 'title': 'Second Coat', 'description': 'Apply second coat after first coat dries'},
                {'step': 6, 'title': 'Trim & Detail Work', 'description': 'Paint trim, doors, detailed areas'},
                {'step': 7, 'title': 'Touch-ups', 'description': 'Fix any missed spots or imperfections'},
                {'step': 8, 'title': 'Cleanup & Inspection', 'description': 'Remove protection, clean area, final inspection'},
            ],
            
            'plumbing': [
                {'step': 1, 'title': 'System Inspection', 'description': 'Inspect existing plumbing, identify issues'},
                {'step': 2, 'title': 'Water Shutoff', 'description': 'Turn off water supply to work area'},
                {'step': 3, 'title': 'Fixture Removal', 'description': 'Remove old fixtures if replacing'},
                {'step': 4, 'title': 'Pipe Work', 'description': 'Install/repair pipes as needed'},
                {'step': 5, 'title': 'Fixture Installation', 'description': 'Install new fixtures properly'},
                {'step': 6, 'title': 'Connection Testing', 'description': 'Test all connections for leaks'},
                {'step': 7, 'title': 'Pressure Testing', 'description': 'Verify proper water pressure'},
                {'step': 8, 'title': 'Final Inspection', 'description': 'Complete inspection, cleanup'},
            ],
            
            'electrical': [
                {'step': 1, 'title': 'Power Shutoff', 'description': 'Turn off power to work area at breaker'},
                {'step': 2, 'title': 'System Assessment', 'description': 'Inspect existing electrical system'},
                {'step': 3, 'title': 'Wiring Installation', 'description': 'Run new wiring as needed'},
                {'step': 4, 'title': 'Outlet/Switch Installation', 'description': 'Install outlets and switches'},
                {'step': 5, 'title': 'Fixture Installation', 'description': 'Install light fixtures'},
                {'step': 6, 'title': 'Breaker Work', 'description': 'Install/update circuit breakers'},
                {'step': 7, 'title': 'Safety Testing', 'description': 'Test all circuits for safety'},
                {'step': 8, 'title': 'Final Inspection', 'description': 'Verify code compliance, cleanup'},
            ],
            
            'flooring': [
                {'step': 1, 'title': 'Area Preparation', 'description': 'Clear room, remove furniture'},
                {'step': 2, 'title': 'Old Flooring Removal', 'description': 'Remove existing flooring if needed'},
                {'step': 3, 'title': 'Subfloor Preparation', 'description': 'Clean, level, repair subfloor'},
                {'step': 4, 'title': 'Underlayment Installation', 'description': 'Install moisture barrier/underlayment'},
                {'step': 5, 'title': 'Flooring Installation', 'description': 'Install new flooring material'},
                {'step': 6, 'title': 'Trim Installation', 'description': 'Install baseboards, transitions'},
                {'step': 7, 'title': 'Final Inspection', 'description': 'Check for level, secure installation'},
                {'step': 8, 'title': 'Cleanup', 'description': 'Clean thoroughly, remove debris'},
            ],
        }
        
        # Find matching checklist
        for key, checklist in checklists.items():
            if key in title_lower:
                return checklist
        
        # Default generic checklist
        return [
            {'step': 1, 'title': 'Project Planning', 'description': 'Review requirements, create work plan'},
            {'step': 2, 'title': 'Site Preparation', 'description': 'Prepare work area, gather materials'},
            {'step': 3, 'title': 'Initial Work', 'description': 'Begin primary work tasks'},
            {'step': 4, 'title': 'Mid-Point Inspection', 'description': 'Review progress, adjust as needed'},
            {'step': 5, 'title': 'Completion of Work', 'description': 'Finish all primary tasks'},
            {'step': 6, 'title': 'Quality Check', 'description': 'Inspect work quality'},
            {'step': 7, 'title': 'Cleanup', 'description': 'Clean work area thoroughly'},
            {'step': 8, 'title': 'Final Inspection', 'description': 'Final walkthrough and approval'},
        ]


# ==================== Anomaly Detection ====================

class DetectPricingAnomaliesView(APIView):
    """Detect unusual pricing in estimates"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        estimate_id = request.data.get('estimate_id')
        
        if not estimate_id:
            return Response(
                {'error': 'Estimate ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate = get_object_or_404(Estimate, id=estimate_id)
        anomalies = []
        
        # Check total amount against similar estimates
        similar_estimates = Estimate.objects.filter(
            workspace=estimate.workspace,
            status__in=['APPROVED', 'SENT']
        ).exclude(id=estimate.id)
        
        if similar_estimates.exists():
            avg_total = similar_estimates.aggregate(Avg('total_amount'))['total_amount__avg']
            
            if avg_total:
                deviation = abs(estimate.total_amount - avg_total) / avg_total * 100
                
                if deviation > 50:  # More than 50% deviation
                    anomalies.append({
                        'type': 'UNUSUAL_TOTAL_AMOUNT',
                        'severity': 'HIGH' if deviation > 100 else 'MEDIUM',
                        'message': f'Total amount ${estimate.total_amount} is {deviation:.1f}% different from average ${avg_total:.2f}',
                        'suggestion': 'Review pricing to ensure accuracy'
                    })
        
        # Check individual line items
        line_items = estimate.line_items.all()
        
        for item in line_items:
            # Check for unusually high unit prices
            if item.unit_price > 10000:
                anomalies.append({
                    'type': 'HIGH_UNIT_PRICE',
                    'severity': 'MEDIUM',
                    'message': f'Line item "{item.description}" has high unit price: ${item.unit_price}',
                    'suggestion': 'Verify unit price is correct'
                })
            
            # Check for zero or negative prices
            if item.unit_price <= 0:
                anomalies.append({
                    'type': 'INVALID_PRICE',
                    'severity': 'HIGH',
                    'message': f'Line item "{item.description}" has invalid price: ${item.unit_price}',
                    'suggestion': 'Update with correct pricing'
                })
            
            # Check for unusual quantities
            if item.quantity > 1000:
                anomalies.append({
                    'type': 'HIGH_QUANTITY',
                    'severity': 'LOW',
                    'message': f'Line item "{item.description}" has high quantity: {item.quantity}',
                    'suggestion': 'Verify quantity is correct'
                })
        
        # Check tax rate
        if estimate.tax_rate > 15 or estimate.tax_rate < 0:
            anomalies.append({
                'type': 'UNUSUAL_TAX_RATE',
                'severity': 'MEDIUM',
                'message': f'Tax rate {estimate.tax_rate}% seems unusual',
                'suggestion': 'Verify tax rate for your location'
            })
        
        return Response({
            'estimate_id': estimate_id,
            'estimate_number': estimate.estimate_number,
            'total_amount': float(estimate.total_amount),
            'anomalies_found': len(anomalies),
            'anomalies': anomalies,
            'status': 'REVIEW_REQUIRED' if anomalies else 'OK'
        })



class DetectMissingJobItemsView(APIView):
    """Detect missing items in job based on job type"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        job_id = request.data.get('job_id')
        
        if not job_id:
            return Response(
                {'error': 'Job ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job = get_object_or_404(Job, id=job_id)
        missing_items = []
        
        # Check for missing customer information
        if not job.customer_name:
            missing_items.append({
                'category': 'CUSTOMER_INFO',
                'severity': 'HIGH',
                'item': 'Customer Name',
                'message': 'Customer name is missing',
                'suggestion': 'Add customer name for proper job tracking'
            })
        
        if not job.customer_email and not job.customer_phone:
            missing_items.append({
                'category': 'CUSTOMER_INFO',
                'severity': 'HIGH',
                'item': 'Customer Contact',
                'message': 'No customer contact information',
                'suggestion': 'Add email or phone number for communication'
            })
        
        if not job.customer_address:
            missing_items.append({
                'category': 'CUSTOMER_INFO',
                'severity': 'MEDIUM',
                'item': 'Customer Address',
                'message': 'Customer address is missing',
                'suggestion': 'Add address for job location reference'
            })
        
        # Check for missing job details
        if not job.description or len(job.description) < 20:
            missing_items.append({
                'category': 'JOB_DETAILS',
                'severity': 'HIGH',
                'item': 'Job Description',
                'message': 'Job description is missing or too brief',
                'suggestion': 'Add detailed description of work to be done'
            })
        
        if not job.estimated_cost:
            missing_items.append({
                'category': 'JOB_DETAILS',
                'severity': 'MEDIUM',
                'item': 'Estimated Cost',
                'message': 'Estimated cost is not set',
                'suggestion': 'Add estimated cost for budgeting'
            })
        
        if not job.due_date:
            missing_items.append({
                'category': 'JOB_DETAILS',
                'severity': 'MEDIUM',
                'item': 'Due Date',
                'message': 'Due date is not set',
                'suggestion': 'Set due date for timeline management'
            })
        
        if not job.start_date:
            missing_items.append({
                'category': 'JOB_DETAILS',
                'severity': 'LOW',
                'item': 'Start Date',
                'message': 'Start date is not set',
                'suggestion': 'Set start date for scheduling'
            })
        
        # Check for missing assignment
        if not job.assigned_to:
            missing_items.append({
                'category': 'ASSIGNMENT',
                'severity': 'HIGH',
                'item': 'Contractor Assignment',
                'message': 'Job is not assigned to any contractor',
                'suggestion': 'Assign job to a qualified contractor'
            })
        
        # Check for missing attachments
        if job.attachments.count() == 0:
            missing_items.append({
                'category': 'DOCUMENTATION',
                'severity': 'LOW',
                'item': 'Job Attachments',
                'message': 'No attachments or photos uploaded',
                'suggestion': 'Add photos or documents for reference'
            })
        
        # Check for missing estimate
        if job.estimates.count() == 0:
            missing_items.append({
                'category': 'DOCUMENTATION',
                'severity': 'MEDIUM',
                'item': 'Estimate',
                'message': 'No estimate created for this job',
                'suggestion': 'Create estimate for customer approval'
            })
        
        # Check for missing checklist
        if job.checklists.count() == 0:
            missing_items.append({
                'category': 'WORKFLOW',
                'severity': 'MEDIUM',
                'item': 'Job Checklist',
                'message': 'No checklist created for this job',
                'suggestion': 'Create checklist for progress tracking'
            })
        
        return Response({
            'job_id': job_id,
            'job_number': job.job_number,
            'job_title': job.title,
            'missing_items_count': len(missing_items),
            'missing_items': missing_items,
            'completeness_score': self._calculate_completeness(job, missing_items),
            'status': 'INCOMPLETE' if missing_items else 'COMPLETE'
        })
    
    def _calculate_completeness(self, job, missing_items):
        """Calculate job completeness percentage"""
        total_checks = 12  # Total number of checks performed
        missing_count = len(missing_items)
        completeness = ((total_checks - missing_count) / total_checks) * 100
        return round(completeness, 1)


# ==================== Smart Recommendations ====================

class SmartRecommendationsView(APIView):
    """Smart recommendations for FM based on historical data"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        recommendations = []
        
        # Recommend contractors based on performance
        top_contractors = self._get_top_contractors()
        if top_contractors:
            recommendations.append({
                'type': 'CONTRACTOR_RECOMMENDATION',
                'priority': 'HIGH',
                'title': 'Top Performing Contractors',
                'message': 'These contractors have excellent ratings and completion records',
                'data': top_contractors
            })
        
        # Identify jobs at risk
        at_risk_jobs = self._get_at_risk_jobs()
        if at_risk_jobs:
            recommendations.append({
                'type': 'AT_RISK_JOBS',
                'priority': 'HIGH',
                'title': 'Jobs Requiring Attention',
                'message': 'These jobs may need immediate attention',
                'data': at_risk_jobs
            })
        
        # Pricing recommendations
        pricing_insights = self._get_pricing_insights()
        if pricing_insights:
            recommendations.append({
                'type': 'PRICING_INSIGHTS',
                'priority': 'MEDIUM',
                'title': 'Pricing Insights',
                'message': 'Average pricing data for common job types',
                'data': pricing_insights
            })
        
        # Workflow optimization
        workflow_tips = self._get_workflow_tips()
        if workflow_tips:
            recommendations.append({
                'type': 'WORKFLOW_OPTIMIZATION',
                'priority': 'LOW',
                'title': 'Workflow Optimization Tips',
                'message': 'Suggestions to improve efficiency',
                'data': workflow_tips
            })
        
        return Response({
            'total_recommendations': len(recommendations),
            'recommendations': recommendations,
            'generated_at': request.user.email
        })
    
    def _get_top_contractors(self):
        """Get top performing contractors"""
        contractors = Contractor.objects.filter(
            status='ACTIVE',
            rating__isnull=False
        ).order_by('-rating', '-total_jobs_completed')[:5]
        
        return [{
            'contractor_email': c.user.email,
            'company_name': c.company_name,
            'rating': float(c.rating) if c.rating else 0,
            'jobs_completed': c.total_jobs_completed,
            'specialization': c.specialization
        } for c in contractors]
    
    def _get_at_risk_jobs(self):
        """Identify jobs that may be at risk"""
        from django.utils import timezone
        from datetime import timedelta
        
        at_risk = []
        
        # Jobs past due date
        overdue_jobs = Job.objects.filter(
            status='IN_PROGRESS',
            due_date__lt=timezone.now().date()
        )[:5]
        
        for job in overdue_jobs:
            at_risk.append({
                'job_number': job.job_number,
                'title': job.title,
                'reason': 'OVERDUE',
                'due_date': str(job.due_date),
                'days_overdue': (timezone.now().date() - job.due_date).days,
                'assigned_to': job.assigned_to.email if job.assigned_to else 'Unassigned'
            })
        
        # Jobs without assignment approaching due date
        unassigned_jobs = Job.objects.filter(
            status='PENDING',
            assigned_to__isnull=True,
            due_date__lte=timezone.now().date() + timedelta(days=7)
        )[:5]
        
        for job in unassigned_jobs:
            at_risk.append({
                'job_number': job.job_number,
                'title': job.title,
                'reason': 'UNASSIGNED_APPROACHING_DUE',
                'due_date': str(job.due_date),
                'days_until_due': (job.due_date - timezone.now().date()).days if job.due_date else None
            })
        
        return at_risk
    
    def _get_pricing_insights(self):
        """Get pricing insights from historical data"""
        insights = []
        
        # Average job costs by status
        completed_jobs = Job.objects.filter(status='COMPLETED', actual_cost__isnull=False)
        
        if completed_jobs.exists():
            avg_cost = completed_jobs.aggregate(Avg('actual_cost'))['actual_cost__avg']
            insights.append({
                'metric': 'Average Completed Job Cost',
                'value': f'${avg_cost:.2f}' if avg_cost else 'N/A',
                'sample_size': completed_jobs.count()
            })
        
        # Average estimate amounts
        approved_estimates = Estimate.objects.filter(status='APPROVED')
        if approved_estimates.exists():
            avg_estimate = approved_estimates.aggregate(Avg('total_amount'))['total_amount__avg']
            insights.append({
                'metric': 'Average Approved Estimate',
                'value': f'${avg_estimate:.2f}' if avg_estimate else 'N/A',
                'sample_size': approved_estimates.count()
            })
        
        return insights
    
    def _get_workflow_tips(self):
        """Get workflow optimization tips"""
        tips = []
        
        # Check for pending estimates
        pending_estimates = Estimate.objects.filter(status='DRAFT').count()
        if pending_estimates > 5:
            tips.append({
                'tip': 'Multiple Draft Estimates',
                'message': f'You have {pending_estimates} draft estimates. Consider reviewing and sending them.',
                'action': 'Review draft estimates'
            })
        
        # Check for unassigned jobs
        unassigned_jobs = Job.objects.filter(assigned_to__isnull=True, status='PENDING').count()
        if unassigned_jobs > 0:
            tips.append({
                'tip': 'Unassigned Jobs',
                'message': f'{unassigned_jobs} jobs are waiting for contractor assignment.',
                'action': 'Assign contractors to pending jobs'
            })
        
        # Check for jobs without checklists
        jobs_without_checklist = Job.objects.filter(
            status='IN_PROGRESS',
            checklists__isnull=True
        ).count()
        
        if jobs_without_checklist > 0:
            tips.append({
                'tip': 'Missing Checklists',
                'message': f'{jobs_without_checklist} active jobs don\'t have checklists.',
                'action': 'Create checklists for better progress tracking'
            })
        
        return tips


class RecommendContractorView(APIView):
    """Recommend best contractor for a specific job"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request):
        job_id = request.data.get('job_id')
        job_title = request.data.get('job_title', '')
        
        if not job_id and not job_title:
            return Response(
                {'error': 'Job ID or job title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get job details
        if job_id:
            job = get_object_or_404(Job, id=job_id)
            job_title = job.title
        
        # Find contractors with relevant specialization
        job_title_lower = job_title.lower()
        relevant_contractors = []
        
        # Get all active contractors
        contractors = Contractor.objects.filter(status='ACTIVE')
        
        for contractor in contractors:
            score = 0
            reasons = []
            
            # Check specialization match
            if contractor.specialization:
                spec_lower = contractor.specialization.lower()
                for keyword in ['bathroom', 'kitchen', 'plumbing', 'electrical', 'painting', 'flooring']:
                    if keyword in job_title_lower and keyword in spec_lower:
                        score += 30
                        reasons.append(f'Specializes in {keyword} work')
                        break
            
            # Rating score
            if contractor.rating:
                score += float(contractor.rating) * 10
                reasons.append(f'High rating: {contractor.rating}/5.0')
            
            # Experience score (jobs completed)
            if contractor.total_jobs_completed > 10:
                score += 20
                reasons.append(f'Experienced: {contractor.total_jobs_completed} jobs completed')
            elif contractor.total_jobs_completed > 5:
                score += 10
                reasons.append(f'{contractor.total_jobs_completed} jobs completed')
            
            # Check current workload
            active_jobs = Job.objects.filter(
                assigned_to=contractor.user,
                status='IN_PROGRESS'
            ).count()
            
            if active_jobs == 0:
                score += 15
                reasons.append('Currently available')
            elif active_jobs < 3:
                score += 5
                reasons.append(f'Light workload ({active_jobs} active jobs)')
            else:
                score -= 10
                reasons.append(f'Busy ({active_jobs} active jobs)')
            
            if score > 0:
                relevant_contractors.append({
                    'contractor_id': contractor.id,
                    'contractor_email': contractor.user.email,
                    'company_name': contractor.company_name,
                    'specialization': contractor.specialization,
                    'rating': float(contractor.rating) if contractor.rating else 0,
                    'jobs_completed': contractor.total_jobs_completed,
                    'active_jobs': active_jobs,
                    'match_score': score,
                    'reasons': reasons
                })
        
        # Sort by score
        relevant_contractors.sort(key=lambda x: x['match_score'], reverse=True)
        
        return Response({
            'job_title': job_title,
            'recommended_contractors': relevant_contractors[:5],
            'total_matches': len(relevant_contractors)
        })
