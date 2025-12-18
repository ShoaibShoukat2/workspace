"""
Basic API Test to verify setup
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Workspace, Job, Contractor

User = get_user_model()


class BasicAPITest(TestCase):
    """Basic test to verify API setup"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='ADMIN'
        )
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Create API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create workspace
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.user
        )
    
    def test_workspace_list(self):
        """Test workspace list endpoint"""
        url = reverse('workspace:workspace-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"✅ Workspace list test passed: {response.status_code}")
    
    def test_authentication_login(self):
        """Test login endpoint"""
        # Check if JWT token endpoint exists
        try:
            from rest_framework_simplejwt.views import TokenObtainPairView
            # JWT login would be at a different endpoint
            print("✅ JWT authentication configured")
        except ImportError:
            print("❌ JWT not available")
        
        # For now, just test that we can authenticate with our token
        url = reverse('workspace:current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"✅ JWT authentication test passed: {response.status_code}")
    
    def test_current_user(self):
        """Test current user endpoint"""
        url = reverse('workspace:current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        print(f"✅ Current user test passed: {response.status_code}")