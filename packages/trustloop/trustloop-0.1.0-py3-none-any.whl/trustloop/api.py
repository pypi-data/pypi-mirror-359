# file: /trustloop-python/trustloop/api.py

import json
import urllib.request
import urllib.parse
import urllib.error


class TrustLoopAPI:
    """TrustLoop API client for making HTTP requests"""
    
    def __init__(self, base_url="http://localhost:4000"):
        self.base_url = base_url
        
    def get(self, endpoint):
        """Make GET request to TrustLoop API"""
        try:
            url = f"{self.base_url}{endpoint}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return data
        except urllib.error.HTTPError as e:
            error_data = e.read().decode()
            try:
                error_json = json.loads(error_data)
                raise Exception(f"API Error {e.code}: {error_json.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP Error {e.code}: {error_data}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def post(self, endpoint, data=None):
        """Make POST request to TrustLoop API"""
        try:
            url = f"{self.base_url}{endpoint}"
            req_data = json.dumps(data).encode() if data else None
            req = urllib.request.Request(url, data=req_data)
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_data = e.read().decode()
            try:
                error_json = json.loads(error_data)
                raise Exception(f"API Error {e.code}: {error_json.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP Error {e.code}: {error_data}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


class APIModule:
    """Direct API access module"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def get(self, endpoint):
        """Make direct GET request"""
        print(f"GET {endpoint}")
        return self.api.get(endpoint)
    
    def post(self, endpoint, data=None):
        """Make direct POST request"""
        print(f"POST {endpoint}")
        return self.api.post(endpoint, data)