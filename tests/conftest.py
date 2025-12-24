"""
Test Configuration and Fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user"""
    from app.models.auth import User
    from app.core.security import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        role="CUSTOMER",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user"""
    from app.models.auth import User
    from app.core.security import get_password_hash
    
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword"),
        role="ADMIN",
        is_active=True,
        is_verified=True,
        is_staff=True,
        is_superuser=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers for test user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
async def admin_headers(client: AsyncClient, admin_user):
    """Get authentication headers for admin user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "adminpassword"
        }
    )
    
    assert response.status_code == 200
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def sample_workspace_data():
    """Sample workspace data for testing"""
    return {
        "name": "Test Workspace",
        "workspace_type": "PROJECT",
        "description": "A test workspace for unit tests"
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "title": "Test Job",
        "description": "A test job for unit tests",
        "priority": "MEDIUM",
        "location": "Test Location",
        "customer_name": "Test Customer",
        "customer_email": "customer@example.com",
        "customer_phone": "123-456-7890"
    }