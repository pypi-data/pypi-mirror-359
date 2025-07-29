# file: /trustloop-python/trustloop/domains.py

import urllib.parse


class DomainsModule:
    """TrustLoop domains module"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def list(self):
        """List all domains"""
        try:
            print("Fetching domain directory...")
            data = self.api.get("/api/domain-directory/directory")
            
            if isinstance(data, list):
                print(f"Found {len(data)} domains:")
                for domain in data:
                    print(f"  {domain.get('domain', 'N/A')}/{domain.get('namespace', 'N/A')}/{domain.get('databaseName', 'N/A')} (id: {domain.get('id', 'N/A')})")
                return data
            else:
                print(f"Domain data: {data}")
                return data
        except Exception as e:
            print(f"Failed to list domains: {e}")
            raise
    
    def get(self, domain, namespace, database, id=None):
        """Get specific domain"""
        try:
            endpoint = f"/api/domain-directory/domains/{domain}/{namespace}/{database}"
            if id:
                endpoint += f"/{id}"
            
            print(f"Fetching domain: {domain}/{namespace}/{database}")
            data = self.api.get(endpoint)
            print(f"✓ Found domain: {data}")
            return data
        except Exception as e:
            print(f"Failed to get domain {domain}/{namespace}/{database}: {e}")
            raise
    
    def check_exists(self, domain, namespace, database_name):
        """Check if domain exists"""
        try:
            params = urllib.parse.urlencode({
                'domain': domain,
                'namespace': namespace, 
                'databaseName': database_name
            })
            endpoint = f"/api/domain-directory/domains/check?{params}"
            data = self.api.get(endpoint)
            return data
        except Exception as e:
            print(f"Failed to check domain existence: {e}")
            raise