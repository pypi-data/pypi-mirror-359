# file: /trustloop-python/trustloop/__init__.py

"""
TrustLoop Python Client

A Python client library for interacting with TrustLoop servers.
Provides easy access to TrustLoop APIs for data loading, domain management, and more.

Usage:
    import trustloop as tl
    
    # Load data from TrustLoop server
    data = tl.data.load("domain-directory")
    
    # List domains
    domains = tl.domains.list()
    
    # Make direct API calls
    result = tl.api.get("/api/testing/ping")
"""

from .api import TrustLoopAPI, APIModule
from .data import DataModule
from .domains import DomainsModule
from .eventbus import EventBusModule

__version__ = "0.1.0"
__author__ = "TrustLoop"
__email__ = "hello@trustloop.com"


class TrustLoop:
    """Main TrustLoop interface"""
    
    def __init__(self, base_url="http://localhost:4000"):
        """
        Initialize TrustLoop client
        
        Args:
            base_url (str): Base URL of the TrustLoop server
        """
        self._api = TrustLoopAPI(base_url)
        self.data = DataModule(self._api)
        self.domains = DomainsModule(self._api)
        self.api = APIModule(self._api)
        self.eventbus = EventBusModule(self._api)
    
    def help(self):
        """Display TrustLoop help"""
        help_text = """
🚀 TrustLoop Python Interface (tl)

USAGE:
  tl.help()                     Show this help
  
DATA MODULE:
  tl.data.load(source)          Load data from source
  tl.data.reload(source)        Reload data (fresh fetch)
  tl.data.list()                List available data sources
  tl.data.cached()              Show cached data info
  
  Example: data = tl.data.load("domain-directory")

DOMAINS MODULE:
  tl.domains.list()             List all domains
  tl.domains.get(domain, ns, db) Get specific domain
  tl.domains.check_exists(...)  Check if domain exists
  
  Example: domains = tl.domains.list()

API MODULE:
  tl.api.get(endpoint)          Direct GET request
  tl.api.post(endpoint, data)   Direct POST request
  
  Example: result = tl.api.get("/api/testing/ping")

EVENTBUS MODULE:
  tl.eventbus.emit(event, data) Emit EventBus event
  
  Example: tl.eventbus.emit("test-event", {"key": "value"})

QUICK START:
  1. tl.data.list()                    # See available data
  2. domains = tl.data.load("domain-directory")  # Load domain data
  3. print(domains[0]["domain"])       # Access domain info
  4. tl.domains.list()                 # Alternative domain access
"""
        print(help_text)
    
    def __repr__(self):
        return "TrustLoop Interface - Use tl.help() for commands"


# Create a default instance for convenience
# This allows users to do: import trustloop as tl
# and immediately use tl.data.load(), etc.
data = None
domains = None  
api = None
eventbus = None
help = None

def _initialize_default_instance():
    """Initialize the default module-level instance"""
    global data, domains, api, eventbus, help
    
    if data is None:  # Only initialize once
        default_tl = TrustLoop()
        data = default_tl.data
        domains = default_tl.domains
        api = default_tl.api
        eventbus = default_tl.eventbus
        help = default_tl.help

# Initialize on import
_initialize_default_instance()

# Export the main class and default instances
__all__ = [
    'TrustLoop',
    'data', 
    'domains',
    'api', 
    'eventbus',
    'help',
    '__version__'
]