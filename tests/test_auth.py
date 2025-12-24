"""
Authentication Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "password2": "newpassword123",
            "role": "CUSTOMER"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "registration successful" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "anotheruser",
            "email": test_user.email,
            "password": "password123",
            "password2": "password123",
            "role": "CUSTOMER"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test getting current user info"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "role" in data


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers):
    """Test updating user profile"""
    response = await client.patch(
        "/api/v1/auth/profile",
        headers=auth_headers,
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "555-0123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["first_name"] == "Updated"
    assert data["user"]["last_name"] == "Name"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, auth_headers):
    """Test changing password"""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "old_password": "testpassword",
            "new_password": "newtestpassword123",
            "new_password2": "newtestpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "password changed" in data["message"].lower()


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers):
    """Test user logout"""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "logout successful" in data["message"].lower()


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without auth"""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_only_endpoint(client: AsyncClient, auth_headers, admin_headers):
    """Test admin-only endpoint access"""
    # Regular user should be denied
    response = await client.get(
        "/api/v1/auth/users",
        headers=auth_headers
    )
    assert response.status_code == 403
    
    # Admin user should have access
    response = await client.get(
        "/api/v1/auth/users",
        headers=admin_headers
    )
    assert response.status_code == 200