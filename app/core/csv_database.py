"""
CSV Database replacement
Simple CSV-based storage instead of SQLAlchemy
"""
from typing import AsyncGenerator
from app.data.csv_data import csv_manager

class CSVSession:
    """Mock database session that works with CSV files"""
    
    def __init__(self):
        self.csv_manager = csv_manager
    
    async def execute(self, query):
        """Mock execute method"""
        # This is a placeholder - in real implementation, 
        # we'd parse the query and execute against CSV
        pass
    
    async def commit(self):
        """Mock commit method"""
        pass
    
    async def rollback(self):
        """Mock rollback method"""
        pass
    
    async def close(self):
        """Mock close method"""
        pass

async def get_db() -> AsyncGenerator[CSVSession, None]:
    """Get database session (CSV-based)"""
    session = CSVSession()
    try:
        yield session
    finally:
        await session.close()