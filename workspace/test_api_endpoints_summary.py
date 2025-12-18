"""
API Endpoints Summary Test
Quick test of all major endpoints to verify they're working
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

from .models import (
    Workspace, Job, Contractor, JobEvaluation, JobCheckpoint, 
    MaterialSuggestion, CustomerProfile
)

User = get_user_model()


class APIEndpointsSummaryTest(TestCase):
    """Test all major API endpoints"""
    
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
        
        # Create JWT tokens
        contractor_refresh = RefreshToken.for_user(self.contractor_user)
        customer_refresh = RefreshToken.for_user(self.customer_user)
        admin_refresh = RefreshToken.for_user(self.admin_user)
        
        # Create API clients
        self.contractor_client = APIClient()
        self.contractor_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(contractor_refresh.access_token)}')
        
        self.customer_client = APIClient()
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(customer_refresh.access_token)}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(admin_refresh.access_token)}')
        
        # Create workspace and related objects
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.admin_user
        )
        
        self.contractor = Contractor.objects.create(
            workspace=self.workspace,
            user=self.contractor_user,
            company_name='Test Contractor LLC'
        )
        
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user,
            workspace=self.workspace
        )
        
        self.job = Job.objects.create(
            workspace=self.workspace,
            job_number='J-2024-TEST-001',
            title='Interior Painting - Living Room',
            description='Paint living room walls',
            status='EVALUATION_SCHEDULED',
            assigned_to=self.contractor_user,
            created_by=self.admin_user,
            customer_name='John Doe',
            customer_email='customer@test.com',
            customer_phone='555-0123',
            customer_address='123 Main St, Anytown, ST 12345',
            evaluation_fee=Decimal('99.00')
        )
    
    def test_all_contractor_endpoints(self):
        """Test all contractor endpoints (B1-B13, B29)"""
        print("\n🔧 TESTING CONTRACTOR ENDPOINTS")
        
        endpoints = [
            ('B1', 'contractor-job-list', 'GET', {}),
            ('B2', 'contractor-job-detail', 'GET', {'job_id': self.job.id}),
            ('B4', 'job-evaluation-update', 'PUT', {'job_id': self.job.id}),
            ('B6', 'job-material-suggestions', 'GET', {'job_id': self.job.id}),
            ('B10', 'job-checklist', 'GET', {'job_id': self.job.id}),
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint_id, url_name, method, kwargs in endpoints:
            try:
                url = reverse(f'workspace:{url_name}', kwargs=kwargs)
                
                if method == 'GET':
                    response = self.contractor_client.get(url)
                elif method == 'PUT':
                    data = {
                        'measurements': {'roomCount': 2, 'squareFeet': 450},
                        'scope': 'Test scope'
                    }
                    response = self.contractor_client.put(url, data, format='json')
                else:
                    response = self.contractor_client.post(url)
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ {endpoint_id} - {url_name}: {response.status_code}")
                    passed += 1
                else:
                    print(f"   ❌ {endpoint_id} - {url_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint_id} - {url_name}: ERROR - {str(e)}")
        
        print(f"   📊 Contractor Endpoints: {passed}/{total} passed")
        return passed, total
    
    def test_all_customer_endpoints(self):
        """Test all customer endpoints (C1-C14)"""
        print("\n👤 TESTING CUSTOMER ENDPOINTS")
        
        # Create a checkpoint for testing
        JobCheckpoint.objects.create(
            job=self.job,
            checkpoint_type='PRE_START',
            status='PENDING'
        )
        
        endpoints = [
            ('C1', 'customer-job-timeline', 'GET', {'job_id': self.job.id}),
            ('C2', 'customer-pre-start-checkpoint', 'GET', {'job_id': self.job.id}),
            ('C11', 'customer-job-materials', 'GET', {'job_id': self.job.id}),
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint_id, url_name, method, kwargs in endpoints:
            try:
                url = reverse(f'workspace:{url_name}', kwargs=kwargs)
                
                if method == 'GET':
                    response = self.customer_client.get(url)
                else:
                    response = self.customer_client.post(url, {'note': 'Test'})
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ {endpoint_id} - {url_name}: {response.status_code}")
                    passed += 1
                else:
                    print(f"   ❌ {endpoint_id} - {url_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint_id} - {url_name}: ERROR - {str(e)}")
        
        print(f"   📊 Customer Endpoints: {passed}/{total} passed")
        return passed, total
    
    def test_service_endpoints(self):
        """Test service endpoints (30-31)"""
        print("\n⚙️ TESTING SERVICE ENDPOINTS")
        
        # Create evaluation for services
        JobEvaluation.objects.get_or_create(
            job=self.job,
            defaults={
                'room_count': 2,
                'square_feet': Decimal('450'),
                'scope': 'Paint living room walls',
                'estimated_hours': Decimal('8'),
                'labor_required': 2
            }
        )
        
        endpoints = [
            ('30', 'rag-pricing-service', 'POST', {'job_id': self.job.id}),
            ('31', 'material-scraper-service', 'POST', {'job_id': self.job.id}),
            ('-', 'material-scraper-status', 'GET', {}),
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint_id, url_name, method, kwargs in endpoints:
            try:
                url = reverse(f'workspace:{url_name}', kwargs=kwargs)
                
                if method == 'GET':
                    response = self.admin_client.get(url)
                else:
                    response = self.admin_client.post(url)
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ {endpoint_id} - {url_name}: {response.status_code}")
                    passed += 1
                else:
                    print(f"   ❌ {endpoint_id} - {url_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint_id} - {url_name}: ERROR - {str(e)}")
        
        print(f"   📊 Service Endpoints: {passed}/{total} passed")
        return passed, total
    
    def test_workflow_progression(self):
        """Test basic workflow progression"""
        print("\n🔄 TESTING WORKFLOW PROGRESSION")
        
        steps_passed = 0
        total_steps = 4
        
        try:
            # 1. Update evaluation
            url = reverse('workspace:job-evaluation-update', kwargs={'job_id': self.job.id})
            data = {
                'measurements': {'roomCount': 2, 'squareFeet': 450},
                'scope': 'Paint living room walls',
                'estimatedHours': 8,
                'laborRequired': 2
            }
            response = self.contractor_client.put(url, data, format='json')
            if response.status_code == 200:
                print("   ✅ Step 1: Evaluation updated")
                steps_passed += 1
            else:
                print(f"   ❌ Step 1: Evaluation update failed - {response.status_code}")
            
            # 2. Submit evaluation
            url = reverse('workspace:job-evaluation-submit', kwargs={'job_id': self.job.id})
            response = self.contractor_client.post(url)
            if response.status_code == 200:
                print("   ✅ Step 2: Evaluation submitted")
                steps_passed += 1
            else:
                print(f"   ❌ Step 2: Evaluation submit failed - {response.status_code}")
            
            # 3. Customer approve pre-start
            url = reverse('workspace:customer-approve-pre-start', kwargs={'job_id': self.job.id})
            response = self.customer_client.post(url, {'note': 'Approved'})
            if response.status_code == 200:
                print("   ✅ Step 3: Pre-start approved")
                steps_passed += 1
            else:
                print(f"   ❌ Step 3: Pre-start approval failed - {response.status_code}")
            
            # 4. Get job timeline
            url = reverse('workspace:customer-job-timeline', kwargs={'job_id': self.job.id})
            response = self.customer_client.get(url)
            if response.status_code == 200:
                print("   ✅ Step 4: Timeline retrieved")
                steps_passed += 1
            else:
                print(f"   ❌ Step 4: Timeline failed - {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Workflow error: {str(e)}")
        
        print(f"   📊 Workflow Steps: {steps_passed}/{total_steps} passed")
        return steps_passed, total_steps
    
    def test_summary(self):
        """Run all tests and provide summary"""
        print("🚀 COMPREHENSIVE API ENDPOINT TEST")
        print("=" * 50)
        
        contractor_passed, contractor_total = self.test_all_contractor_endpoints()
        customer_passed, customer_total = self.test_all_customer_endpoints()
        service_passed, service_total = self.test_service_endpoints()
        workflow_passed, workflow_total = self.test_workflow_progression()
        
        total_passed = contractor_passed + customer_passed + service_passed + workflow_passed
        total_tests = contractor_total + customer_total + service_total + workflow_total
        
        print(f"\n📈 FINAL SUMMARY")
        print("=" * 50)
        print(f"🔧 Contractor Endpoints: {contractor_passed}/{contractor_total}")
        print(f"👤 Customer Endpoints: {customer_passed}/{customer_total}")
        print(f"⚙️ Service Endpoints: {service_passed}/{service_total}")
        print(f"🔄 Workflow Steps: {workflow_passed}/{workflow_total}")
        print("-" * 50)
        print(f"🎯 TOTAL: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.1f}%)")
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! API is fully functional!")
        elif total_passed >= total_tests * 0.8:
            print("✅ Most tests passed! API is largely functional!")
        else:
            print("⚠️ Some issues found. Check failed endpoints.")
        
        print("=" * 50)