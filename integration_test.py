"""Integration test for the Light AI Model Evaluation Platform."""

import os
import sys
import time
import subprocess
import requests
import threading
from typing import Dict, Any

def start_backend_service():
    """Start the backend service in a separate thread."""
    print("Starting backend service...")
    # Change to backend directory and start the service
    os.chdir("backend")
    backend_process = subprocess.Popen([sys.executable, "main.py"])
    os.chdir("..")
    return backend_process

def start_frontend_service():
    """Start the frontend service in a separate thread."""
    print("Starting frontend service...")
    # Change to eval-ui directory and start the service
    os.chdir("eval-ui")
    frontend_process = subprocess.Popen(["npm", "run", "dev"])
    os.chdir("..")
    return frontend_process

def test_api_endpoints():
    """Test API endpoints."""
    print("Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        print("✓ Root endpoint test passed")
    except Exception as e:
        print(f"✗ Root endpoint test failed: {e}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✓ Health check test passed")
    except Exception as e:
        print(f"✗ Health check test failed: {e}")
    
    # Test API config endpoints
    try:
        # Create a test config
        config_data = {
            "name": "Test API Config",
            "type": "cloud",
            "provider": "openai",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_config": {"api_key": "test-key"},
            "protocol_type": "openai"
        }
        
        response = requests.post(f"{base_url}/api/configs", json=config_data)
        assert response.status_code == 200
        config_id = response.json()["id"]
        print("✓ Create API config test passed")
        
        # List configs
        response = requests.get(f"{base_url}/api/configs")
        assert response.status_code == 200
        print("✓ List API configs test passed")
        
        # Get specific config
        response = requests.get(f"{base_url}/api/configs/{config_id}")
        assert response.status_code == 200
        print("✓ Get API config test passed")
        
        # Update config
        update_data = {"name": "Updated Test API Config"}
        response = requests.put(f"{base_url}/api/configs/{config_id}", json=update_data)
        assert response.status_code == 200
        print("✓ Update API config test passed")
        
        # Delete config
        response = requests.delete(f"{base_url}/api/configs/{config_id}")
        assert response.status_code == 200
        print("✓ Delete API config test passed")
        
    except Exception as e:
        print(f"✗ API config endpoints test failed: {e}")

def test_database_integration():
    """Test database integration."""
    print("Testing database integration...")
    
    try:
        from backend.database import DatabaseManager
        
        # Initialize database manager
        db_manager = DatabaseManager("sqlite:///./test_integration.db")
        
        # Test user creation
        user_data = {
            "id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password_here",
            "role": "user"
        }
        
        user = db_manager.create_user(user_data)
        assert user.username == "testuser"
        print("✓ User creation test passed")
        
        # Test user retrieval
        retrieved_user = db_manager.get_user("test_user_123")
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        print("✓ User retrieval test passed")
        
        # Test API config creation
        config_data = {
            "id": "test_config_123",
            "user_id": "test_user_123",
            "name": "Test Config",
            "type": "cloud",
            "provider": "openai",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_config": "encrypted_auth_data",
            "protocol_type": "openai"
        }
        
        config = db_manager.create_api_config(config_data)
        assert config.name == "Test Config"
        print("✓ API config creation test passed")
        
        # Test API config retrieval
        configs = db_manager.get_api_configs("test_user_123")
        assert len(configs) > 0
        print("✓ API config retrieval test passed")
        
        print("✓ Database integration test passed")
        
    except Exception as e:
        print(f"✗ Database integration test failed: {e}")

def test_opencompass_integration():
    """Test OpenCompass integration."""
    print("Testing OpenCompass integration...")
    
    try:
        from opencompass.models.unified_api import UnifiedAPIModel
        from opencompass.configs.models.unified_api_examples import openai_model, edge_model
        
        # Test model instantiation
        model = UnifiedAPIModel(**openai_model)
        assert model is not None
        print("✓ UnifiedAPIModel instantiation test passed")
        
        # Test adapter creation
        from opencompass.models.unified_api import UnifiedAPIManager
        manager = UnifiedAPIManager()
        
        # Test OpenAI adapter
        openai_config = {
            'api_key': 'test-key',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'model': 'gpt-3.5-turbo'
        }
        openai_adapter = manager.create_adapter('openai', openai_config)
        assert openai_adapter is not None
        print("✓ OpenAI adapter creation test passed")
        
        # Test RESTful adapter
        restful_config = {
            'endpoint': 'http://localhost:8000/api/chat',
            'method': 'POST'
        }
        restful_adapter = manager.create_adapter('restful', restful_config)
        assert restful_adapter is not None
        print("✓ RESTful adapter creation test passed")
        
        print("✓ OpenCompass integration test passed")
        
    except Exception as e:
        print(f"✗ OpenCompass integration test failed: {e}")

def test_storage_integration():
    """Test storage integration."""
    print("Testing storage integration...")
    
    try:
        from backend.storage import StorageManager
        
        # Initialize storage manager
        storage_manager = StorageManager(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        # Test bucket creation
        bucket_name = "integration-test-bucket"
        success = storage_manager.create_bucket(bucket_name)
        assert success
        print("✓ Bucket creation test passed")
        
        # Test data upload
        test_data = {"message": "Hello, storage!", "test": True}
        object_name = "test-data.json"
        success = storage_manager.upload_json(bucket_name, object_name, test_data)
        assert success
        print("✓ Data upload test passed")
        
        # Test data download
        downloaded_data = storage_manager.download_json(bucket_name, object_name)
        assert downloaded_data is not None
        assert downloaded_data["message"] == "Hello, storage!"
        print("✓ Data download test passed")
        
        print("✓ Storage integration test passed")
        
    except Exception as e:
        print(f"✗ Storage integration test failed: {e}")

def run_integration_tests():
    """Run all integration tests."""
    print("=" * 50)
    print("Light AI Model Evaluation Platform Integration Tests")
    print("=" * 50)
    
    # Test individual components
    test_database_integration()
    test_opencompass_integration()
    test_storage_integration()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("=" * 50)
    print("Integration tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    run_integration_tests()