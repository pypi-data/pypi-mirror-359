# file: /trustloop-python/tests/test_trustloop.py

import pytest
import sys
import os

# Add the parent directory to the path so we can import trustloop
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trustloop
from trustloop import TrustLoop


def test_import():
    """Test that trustloop can be imported"""
    assert trustloop is not None
    assert hasattr(trustloop, 'data')
    assert hasattr(trustloop, 'domains')
    assert hasattr(trustloop, 'api')
    assert hasattr(trustloop, 'eventbus')
    assert hasattr(trustloop, 'help')


def test_trustloop_class():
    """Test TrustLoop class instantiation"""
    tl = TrustLoop()
    assert tl is not None
    assert hasattr(tl, 'data')
    assert hasattr(tl, 'domains')
    assert hasattr(tl, 'api')
    assert hasattr(tl, 'eventbus')
    

def test_custom_base_url():
    """Test TrustLoop with custom base URL"""
    custom_url = "http://example.com:8080"
    tl = TrustLoop(base_url=custom_url)
    assert tl._api.base_url == custom_url


def test_data_module():
    """Test data module availability"""
    assert hasattr(trustloop.data, 'load')
    assert hasattr(trustloop.data, 'list')
    assert hasattr(trustloop.data, 'cached')
    assert hasattr(trustloop.data, 'reload')


def test_domains_module():
    """Test domains module availability"""
    assert hasattr(trustloop.domains, 'list')
    assert hasattr(trustloop.domains, 'get')
    assert hasattr(trustloop.domains, 'check_exists')


def test_api_module():
    """Test API module availability"""
    assert hasattr(trustloop.api, 'get')
    assert hasattr(trustloop.api, 'post')


def test_eventbus_module():
    """Test EventBus module availability"""
    assert hasattr(trustloop.eventbus, 'emit')


def test_version():
    """Test version is available"""
    assert hasattr(trustloop, '__version__')
    assert trustloop.__version__ == "0.1.0"


def test_help_function():
    """Test help function"""
    # This should not raise an exception
    trustloop.help()


if __name__ == "__main__":
    pytest.main([__file__])