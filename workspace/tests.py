from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Workspace, Job, Estimate, Contractor, Payout, ComplianceData
from .utils import generate_job_number, generate_estimate_number, generate_payout_number

User = get_user_model()


class WorkspaceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_workspace_creation(self):
        """Test workspace creation with unique ID"""
        workspace = Workspace.objects.create(
            name='Test Workspace',
            workspace_type='PROJECT',
            owner=self.user
        )
        self.assertIsNotNone(workspace.workspace_id)
        self.assertEqual(workspace.name, 'Test Workspace')
        self.assertEqual(workspace.owner, self.user)
    
    def test_workspace_id_uniqueness(self):
        """Test that workspace IDs are unique"""
        workspace1 = Workspace.objects.create(
            name='Workspace 1',
            owner=self.user
        )
        workspace2 = Workspace.objects.create(
            name='Workspace 2',
            owner=self.user
        )
        self.assertNotEqual(workspace1.workspace_id, workspace2.workspace_id)


class JobModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.user
        )
    
    def test_job_creation(self):
        """Test job creation"""
        job_number = generate_job_number(self.workspace.workspace_id)
        job = Job.objects.create(
            workspace=self.workspace,
            job_number=job_number,
            title='Test Job',
            description='Test Description',
            created_by=self.user
        )
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.status, 'PENDING')
        self.assertIn('JOB-', job.job_number)


class ContractorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='contractor@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.user
        )
    
    def test_contractor_creation(self):
        """Test contractor creation"""
        contractor = Contractor.objects.create(
            workspace=self.workspace,
            user=self.user,
            company_name='Test Company',
            hourly_rate=50.00
        )
        self.assertEqual(contractor.company_name, 'Test Company')
        self.assertEqual(contractor.status, 'ACTIVE')
        self.assertEqual(contractor.total_jobs_completed, 0)


class ComplianceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='contractor@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.user
        )
        self.contractor = Contractor.objects.create(
            workspace=self.workspace,
            user=self.user
        )
    
    def test_compliance_expiry_check(self):
        """Test compliance expiry checking"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create expired compliance
        expired_compliance = ComplianceData.objects.create(
            workspace=self.workspace,
            contractor=self.contractor,
            compliance_type='LICENSE',
            document_name='Test License',
            expiry_date=timezone.now().date() - timedelta(days=1)
        )
        self.assertTrue(expired_compliance.is_expired)
        
        # Create expiring soon compliance
        expiring_compliance = ComplianceData.objects.create(
            workspace=self.workspace,
            contractor=self.contractor,
            compliance_type='INSURANCE',
            document_name='Test Insurance',
            expiry_date=timezone.now().date() + timedelta(days=15)
        )
        self.assertTrue(expiring_compliance.is_expiring_soon)
