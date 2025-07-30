# terrakio_admin/__init__.py
"""
Terrakio Admin API Client

An admin API client for Terrakio.
"""

__version__ = "0.3.8"

from terrakio_core import AsyncClient as CoreAsyncClient
from terrakio_core import SyncClient as CoreSyncClient
from terrakio_core.endpoints.group_management import AdminGroupManagement

class AsyncClient(CoreAsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = AdminGroupManagement(self)

class SyncClient(CoreSyncClient):
    """Synchronous version of the Terrakio Admin API client with full admin permissions."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = AdminGroupManagement(self)

__all__ = ['AsyncClient', 'SyncClient']