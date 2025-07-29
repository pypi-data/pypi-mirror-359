# file: /trustloop-python/trustloop/data.py

import json
from datetime import datetime


class DataModule:
    """TrustLoop data loading module"""
    
    def __init__(self, api_client):
        self.api = api_client
        self._cache = {}
        
    def load(self, source):
        """Load data from specified source"""
        sources = {
            "domain-directory": "/api/domain-directory/directory",
            "concept-registry": "/api/concept-registry/ping",
            "testing": "/api/testing/ping",
            "global-status": "/api/global/command-center/status"
        }
        
        if source not in sources:
            available = list(sources.keys())
            raise ValueError(f"Unknown data source '{source}'. Available: {available}")
        
        endpoint = sources[source]
        print(f"Loading {source} data...")
        
        try:
            data = self.api.get(endpoint)
            self._cache[source] = {
                'data': data,
                'loaded_at': datetime.now().isoformat(),
                'source': source
            }
            print(f"✓ Loaded {source} successfully")
            
            # Pretty print the data if it's a dict or list
            if isinstance(data, (dict, list)):
                print("\n" + json.dumps(data, indent=2, ensure_ascii=False))
            
            return data
        except Exception as e:
            print(f"✗ Failed to load {source}: {e}")
            raise
    
    def reload(self, source):
        """Reload data from source (bypasses cache)"""
        return self.load(source)
    
    def list(self):
        """List available data sources"""
        sources = {
            "domain-directory": "Domain directory with all registered domains",
            "concept-registry": "Concept registry data", 
            "testing": "Testing module data",
            "global-status": "Global system status"
        }
        
        print("Available data sources:")
        for source, description in sources.items():
            cached = "✓ cached" if source in self._cache else ""
            print(f"  {source:<20} - {description} {cached}")
        
        return list(sources.keys())
    
    def cached(self):
        """Show cached data info"""
        if not self._cache:
            print("No cached data")
            return {}
        
        print("Cached data:")
        for source, info in self._cache.items():
            print(f"  {source:<20} - loaded at {info['loaded_at']}")
        
        return self._cache