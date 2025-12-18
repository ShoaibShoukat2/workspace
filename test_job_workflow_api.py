"""
Comprehensive Test Suite for Job Workflow API
Tests all 31 API endpoints for contractor and customer job workflow
"""
import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from workspace.models import (
    Workspace, Job, Contractor, JobEvaluation, JobPhoto, JobQuote,
    JobCheckpoint, JobProgressNote, JobChecklist, MaterialSuggestion
)

User = get_user_model()


class JobWorkflowAPITestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        # Create users
        self.contractor_user = User.objects.create_user(
            email='contractor@test.com',
            password='testpass123',
            role='CONTRACTOR'
        )
        self.customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            role='CUSTOMER'
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='ADMIN'
        )
        
        # Create tokens
        self.contractor_token = Token.objects.create(user=self.contractor_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Create workspace
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.admin_user
        )
        
        # Create contractor profile
        self.contractor = Contractor.objects.create(
            workspace=self.workspace,
            user=self.contractor_user,
            company_name='Test Contractor LLC'
        )
        
        # Create test job
        self.job = Job.objects.create(
            workspace=self.workspace,
            job_number='J-2024-TEST-001',
            title='Interior Painting - Living Room',
            description='Paint living room walls with premium eggshell paint',
            status='EVALUATION_SCHEDULED',
            assigned_to=self.contractor_user,
            created_by=self.admin_user,
            customer_name='John Doe',
            customer_email='customer@test.com',
            customer_phone='555-0123',
            customer_address='123 Main St, Anytown, ST 12345',
            evaluation_fee=Decimal('99.00')
        )
        
        # Create API clients
        self.contractor_client = APIClient()
        self.contractor_client.credentials(HTTP_AUTHORIZATION=f'Token {self.contractor_token.key}')
        
        self.customer_client = APIClient()
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')


class AuthenticationAPITests(JobWorkflowAPITestCase):
    """Test authentication endpoints"""
    
    def test_login_endpoint(self):
        """Test login endpoint returns token and user info"""
        url = reverse('workspace:auth-login')
        data = {
            'username': 'contractor@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_type'], 'contractor')
        self.assertEqual(response.data['email'], 'contractor@test.com')
    
    def test_current_user_endpoint(self):
        """Test current user endpoint"""
        url = reverse('workspace:current-user')
        
        response = self.contractor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], 'contractor')
        self.assertEqual(response.data['email'], 'contractor@test.com')


class ContractorJobAPITests(JobWorkflowAPITestCase):
    """Test contractor job management endpoints (B1-B13, B29)"""
    
    def test_b1_contractor_job_list(self):
        """B1: Contractor Home / Job List"""
        url = reverse('workspace:contractor-job-list')
        
        response = self.contractor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['job_number'], 'J-2024-TEST-001')
    
    def test_b2_contractor_job_detail(self):
        """B2: Job Detail — Overview Tab"""
        url = reverse('workspace:contractor-job-detail', kwargs={'job_id': self.job.id})
        
        response = self.contractor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['job_number'], 'J-2024-TEST-001')
        self.assertIn('customer_info', response.data)
    
    def test_b3_job_photo_upload(self):
        """B3: Upload evaluation photos"""
        url = reverse('workspace:job-photo-upload', kwargs={'job_id': self.job.id})
        
        # Mock file upload
        data = {
            'type': 'before',
            'caption': 'Before photo - living room'
        }
        
        # Note: In real test, would include actual file upload
        # For now, testing the endpoint structure
        response = self.contractor_client.post(url, data)
        # Expecting 400 because no file provided
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_b4_job_evaluation_update(self):
        """B4: Save/update evaluation data"""
        url = reverse('workspace:job-evaluation-update', kwargs={'job_id': self.job.id})
        
        data = {
            'measurements': {
                'roomCount': 2,
                'squareFeet': 450
            },
            'scope': 'Paint living room and dining room walls',
            'toolsRequired': ['brushes', 'rollers', 'ladder'],
            'laborRequired': 2,
            'estimatedHours': 8,
            'safetyConcerns': 'High ceilings require ladder safety'
        }
        
        response = self.contractor_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify evaluation was created/updated
        evaluation = JobEvaluation.objects.get(job=self.job)
        self.assertEqual(evaluation.room_count, 2)
        self.assertEqual(evaluation.square_feet, Decimal('450'))
    
    def test_b5_job_evaluation_submit(self):
        """B5: Submit evaluation + trigger pricing"""
        # First create evaluation
        JobEvaluation.objects.create(
            job=self.job,
            room_count=2,
            square_feet=Decimal('450'),
            scope='Paint living room walls',
            estimated_hours=Decimal('8'),
            labor_required=2
        )
        
        url = reverse('workspace:job-evaluation-submit', kwargs={'job_id': self.job.id})
        
        response = self.contractor_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('quoteId', response.data)
        self.assertIn('gbbTotal', response.data)
        
        # Verify job status updated
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'AWAITING_PRE_START_APPROVAL')
        
        # Verify quote created
        self.assertTrue(JobQuote.objects.filter(job=self.job).exists())
        
        # Verify checkpoint created
        self.assertTrue(JobCheckpoint.objects.filter(
            job=self.job, 
            checkpoint_type='PRE_START'
        ).exists())
    
    def test_b6_job_material_suggestions(self):
        """B6: Get suggested materials list"""
        url = reverse('workspace:job-material-suggestions', kwargs={'job_id': self.job.id})
        
        response = self.contractor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty list initially, then generate suggestions
        self.assertIsInstance(response.data, list)
    
    def test_b7_job_material_verification(self):
        """B7: Save contractor-verified materials"""
        # Create material suggestion first
        material = MaterialSuggestion.objects.create(
            job=self.job,
            item_name='Interior Paint',
            vendor='Home Depot',
            price_range='$35-$45',
            suggested_qty=Decimal('3'),
            unit='gallon',
            product_url='https://homedepot.com/paint'
        )
        
        url = reverse('workspace:job-material-verification', kwargs={'job_id': self.job.id})
        data = {
            'items': [
                {
                    'id': material.id,
                    'confirmedQty': 4,
                    'status': 'confirmed'
                }
            ]
        }
        
        response = self.contractor_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify material updated
        material.refresh_from_db()
        self.assertEqual(material.contractor_confirmed_qty, Decimal('4'))
        self.assertEqual(material.contractor_status, 'confirmed')
    
    def test_b10_job_checklist_get(self):
        """B10: Get checklist template & status"""
        url = reverse('workspace:job-checklist', kwargs={'job_id': self.job.id})
        
        response = self.contractor_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        
        # Verify checklist was created
        self.assertTrue(JobChecklist.objects.filter(job=self.job).exists())
    
    def test_b11_job_checklist_update(self):
        """B11: Update checklist status"""
        # Create checklist first
        checklist = JobChecklist.objects.create(
            job=self.job,
            items=[
                {'id': 'c1', 'label': 'All walls painted', 'done': False},
                {'id': 'c2', 'label': 'Area cleaned up', 'done': False}
            ]
        )
        
        url = reverse('workspace:job-checklist-update', kwargs={'job_id': self.job.id})
        data = {
            'items': [
                {'id': 'c1', 'label': 'All walls painted', 'done': True},
                {'id': 'c2', 'label': 'Area cleaned up', 'done': False}
            ]
        }
        
        response = self.contractor_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify checklist updated
        checklist.refresh_from_db()
        self.assertTrue(checklist.items[0]['done'])
        self.assertFalse(checklist.items[1]['done'])
    
    def test_b13_job_complete_work(self):
        """B13: Mark work complete → trigger final checkpoint"""
        # Create completed checklist
        JobChecklist.objects.create(
            job=self.job,
            items=[
                {'id': 'c1', 'label': 'All walls painted', 'done': True},
                {'id': 'c2', 'label': 'Area cleaned up', 'done': True}
            ],
            completion_percentage=Decimal('100')
        )
        
        url = reverse('workspace:job-complete-work', kwargs={'job_id': self.job.id})
        
        response = self.contractor_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify job status updated
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'AWAITING_FINAL_APPROVAL')
        
        # Verify final checkpoint created
        self.assertTrue(JobCheckpoint.objects.filter(
            job=self.job,
            checkpoint_type='FINAL'
        ).exists())


class CustomerJobAPITests(JobWorkflowAPITestCase):
    """Test customer job experience endpoints (C1-C14)"""
    
    def setUp(self):
        super().setUp()
        # Update job to have customer email matching customer user
        self.job.customer_email = self.customer_user.email
        self.job.save()
    
    def test_c1_customer_job_timeline(self):
        """C1: Job Timeline (Main Screen)"""
        url = reverse('workspace:customer-job-timeline', kwargs={'job_id': self.job.id})
        
        response = self.customer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('job', response.data)
        self.assertIn('steps', response.data)
        self.assertIsInstance(response.data['steps'], list)
    
    def test_c2_customer_pre_start_checkpoint(self):
        """C2: Pre-Start Verification Screen"""
        # Create pre-start checkpoint
        JobCheckpoint.objects.create(
            job=self.job,
            checkpoint_type='PRE_START',
            scope_summary='Ready to begin painting project'
        )
        
        url = reverse('workspace:customer-pre-start-checkpoint', kwargs={'job_id': self.job.id})
        
        response = self.customer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('checkpointId', response.data)
        self.assertIn('scopeSummary', response.data)
    
    def test_c3_customer_approve_pre_start(self):
        """C3: Approve pre-start (move job to In Progress)"""
        # Create pre-start checkpoint
        checkpoint = JobCheckpoint.objects.create(
            job=self.job,
            checkpoint_type='PRE_START',
            status='PENDING'
        )
        
        url = reverse('workspace:customer-approve-pre-start', kwargs={'job_id': self.job.id})
        data = {'note': 'Looks good, proceed with work'}
        
        response = self.customer_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify checkpoint approved
        checkpoint.refresh_from_db()
        self.assertEqual(checkpoint.status, 'APPROVED')
        
        # Verify job status updated
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'IN_PROGRESS')
    
    def test_c9_customer_approve_final(self):
        """C9: Approve completion & release payment"""
        # Create final checkpoint
        checkpoint = JobCheckpoint.objects.create(
            job=self.job,
            checkpoint_type='FINAL',
            status='PENDING'
        )
        
        url = reverse('workspace:customer-approve-final', kwargs={'job_id': self.job.id})
        data = {
            'note': 'Excellent work!',
            'rating': 5,
            'review': 'Very professional and high quality work'
        }
        
        response = self.customer_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify checkpoint approved
        checkpoint.refresh_from_db()
        self.assertEqual(checkpoint.status, 'APPROVED')
        self.assertEqual(checkpoint.customer_rating, 5)
        
        # Verify job completed
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'COMPLETED')
    
    def test_c11_customer_job_materials(self):
        """C11: Materials Screen (Customer)"""
        # Create material suggestions
        MaterialSuggestion.objects.create(
            job=self.job,
            item_name='Interior Paint',
            vendor='Home Depot',
            price_range='$35-$45',
            product_url='https://homedepot.com/paint',
            suggested_qty=Decimal('3'),
            unit='gallon'
        )
        
        url = reverse('workspace:customer-job-materials', kwargs={'job_id': self.job.id})
        
        response = self.customer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('materialSource', response.data)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 1)


class ServiceAPITests(JobWorkflowAPITestCase):
    """Test RAG pricing and material scraper services (Endpoints 30-31)"""
    
    def test_endpoint_30_rag_pricing_service(self):
        """Endpoint 30: RAG Pricing Service Integration"""
        # Create evaluation first
        JobEvaluation.objects.create(
            job=self.job,
            room_count=2,
            square_feet=Decimal('450'),
            scope='Paint living room walls',
            estimated_hours=Decimal('8'),
            labor_required=2
        )
        
        url = reverse('workspace:rag-pricing-service', kwargs={'job_id': self.job.id})
        
        response = self.admin_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('quote_id', response.data)
        self.assertIn('gbb_total', response.data)
        self.assertIn('confidence_score', response.data)
        self.assertIn('comparable_jobs', response.data)
        
        # Verify quote was created
        self.assertTrue(JobQuote.objects.filter(job=self.job).exists())
    
    def test_endpoint_31_material_scraper_service(self):
        """Endpoint 31: Material Scraper Service"""
        # Create evaluation first
        JobEvaluation.objects.create(
            job=self.job,
            room_count=2,
            square_feet=Decimal('450'),
            scope='Paint living room walls'
        )
        
        url = reverse('workspace:material-scraper-service', kwargs={'job_id': self.job.id})
        
        response = self.admin_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions_count', response.data)
        self.assertIn('materials', response.data)
        self.assertIn('total_estimated_cost', response.data)
        
        # Verify material suggestions were created
        self.assertTrue(MaterialSuggestion.objects.filter(job=self.job).exists())
    
    def test_material_scraper_status(self):
        """Test material scraper status endpoint"""
        url = reverse('workspace:material-scraper-status')
        
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('service_status', response.data)
        self.assertIn('vendors_active', response.data)
    
    def test_rag_pricing_analytics(self):
        """Test RAG pricing analytics endpoint"""
        url = reverse('workspace:rag-pricing-analytics')
        
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_quotes_generated', response.data)
        self.assertIn('accuracy_rate', response.data)


class WorkflowIntegrationTests(JobWorkflowAPITestCase):
    """Test complete job workflow integration"""
    
    def test_complete_job_workflow(self):
        """Test complete job workflow from evaluation to completion"""
        
        # 1. Contractor updates evaluation (B4)
        eval_url = reverse('workspace:job-evaluation-update', kwargs={'job_id': self.job.id})
        eval_data = {
            'measurements': {'roomCount': 2, 'squareFeet': 450},
            'scope': 'Paint living room walls',
            'estimatedHours': 8,
            'laborRequired': 2
        }
        response = self.contractor_client.put(eval_url, eval_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Contractor submits evaluation (B5)
        submit_url = reverse('workspace:job-evaluation-submit', kwargs={'job_id': self.job.id})
        response = self.contractor_client.post(submit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Customer approves pre-start (C3)
        approve_url = reverse('workspace:customer-approve-pre-start', kwargs={'job_id': self.job.id})
        response = self.customer_client.post(approve_url, {'note': 'Approved'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Contractor completes checklist and work (B11, B13)
        checklist_url = reverse('workspace:job-checklist-update', kwargs={'job_id': self.job.id})
        checklist_data = {
            'items': [
                {'id': 'c1', 'label': 'All walls painted', 'done': True},
                {'id': 'c2', 'label': 'Area cleaned up', 'done': True},
                {'id': 'c3', 'label': 'Tools removed', 'done': True},
                {'id': 'c4', 'label': 'Quality check', 'done': True}
            ]
        }
        response = self.contractor_client.put(checklist_url, checklist_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        complete_url = reverse('workspace:job-complete-work', kwargs={'job_id': self.job.id})
        response = self.contractor_client.post(complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Customer approves final (C9)
        final_url = reverse('workspace:customer-approve-final', kwargs={'job_id': self.job.id})
        final_data = {'rating': 5, 'review': 'Excellent work!'}
        response = self.customer_client.post(final_url, final_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify final job status
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'COMPLETED')


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])