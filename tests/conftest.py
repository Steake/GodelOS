"""
Pytest Configuration for GödelOS Test Suite

Global pytest configuration, fixtures, and setup for all test suites.
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import common fixtures
from tests.utils.fixtures import *

# Configure asyncio for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_backend: mark test as requiring running backend"
    )
    config.addinivalue_line(
        "markers", "requires_frontend: mark test as requiring running frontend"
    )


# Global fixtures for test environment
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Create test directories if they don't exist
    test_dirs = [
        "test_output",
        "test_logs",
        "test_storage"
    ]
    
    for test_dir in test_dirs:
        test_path = project_root / test_dir
        test_path.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after all tests
    import shutil
    for test_dir in test_dirs:
        test_path = project_root / test_dir
        if test_path.exists():
            shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "backend_url": "http://localhost:8000",
        "frontend_url": "http://localhost:3000",
        "websocket_url": "ws://localhost:8000/ws/cognitive-stream",
        "timeout": 10,
        "slow_timeout": 30,
        "performance_thresholds": {
            "api_response_ms": 2000,
            "query_processing_ms": 5000,
            "websocket_latency_ms": 100
        }
    }


# Skip markers for different test conditions
def pytest_runtest_setup(item):
    """Set up individual test runs with conditional skipping."""
    # Skip backend tests if backend is not available
    if "requires_backend" in [mark.name for mark in item.iter_markers()]:
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code not in [200, 503]:
                pytest.skip("Backend not available")
        except:
            pytest.skip("Backend not accessible")
    
    # Skip frontend tests if frontend is not available
    if "requires_frontend" in [mark.name for mark in item.iter_markers()]:
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code >= 500:
                pytest.skip("Frontend not available")
        except:
            pytest.skip("Frontend not accessible")


# Collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add markers based on file path
        if "backend" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "frontend" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["concurrent", "load", "stress", "performance"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark tests requiring services
        if any(keyword in str(item.fspath) for keyword in ["integration", "e2e"]):
            item.add_marker(pytest.mark.requires_backend)