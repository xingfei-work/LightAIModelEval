"""Tests for the Unified API model."""

import unittest
from unittest.mock import patch, Mock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opencompass.models.unified_api import (
    BaseAPIAdapter, 
    OpenAIAdapter, 
    RESTfulAdapter, 
    UnifiedAPIManager,
    UnifiedAPIModel
)


class TestBaseAPIAdapter(unittest.TestCase):
    """Test cases for BaseAPIAdapter."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseAPIAdapter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseAPIAdapter({})


class TestOpenAIAdapter(unittest.TestCase):
    """Test cases for OpenAIAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'api_key': 'test-key',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'model': 'gpt-3.5-turbo'
        }
        self.adapter = OpenAIAdapter(self.config)
        
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.api_key, 'test-key')
        self.assertEqual(self.adapter.endpoint, 'https://api.openai.com/v1/chat/completions')
        self.assertEqual(self.adapter.model, 'gpt-3.5-turbo')
        
    def test_validate_config_success(self):
        """Test successful configuration validation."""
        self.assertTrue(self.adapter.validate_config(self.config))
        
    def test_validate_config_missing_api_key(self):
        """Test configuration validation with missing API key."""
        invalid_config = self.config.copy()
        del invalid_config['api_key']
        self.assertFalse(self.adapter.validate_config(invalid_config))


class TestRESTfulAdapter(unittest.TestCase):
    """Test cases for RESTfulAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'endpoint': 'http://localhost:8000/api/chat',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'request_mapping': {
                'prompt': 'input.text',
                'max_tokens': 'params.max_tokens'
            },
            'response_mapping': {
                'result': 'data.result'
            }
        }
        self.adapter = RESTfulAdapter(self.config)
        
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.endpoint, 'http://localhost:8000/api/chat')
        self.assertEqual(self.adapter.method, 'POST')
        self.assertEqual(self.adapter.headers, {'Content-Type': 'application/json'})
        
    def test_validate_config_success(self):
        """Test successful configuration validation."""
        self.assertTrue(self.adapter.validate_config(self.config))
        
    def test_validate_config_missing_endpoint(self):
        """Test configuration validation with missing endpoint."""
        invalid_config = self.config.copy()
        del invalid_config['endpoint']
        self.assertFalse(self.adapter.validate_config(invalid_config))
        
    def test_set_nested_value(self):
        """Test setting nested dictionary values."""
        data = {}
        self.adapter._set_nested_value(data, 'a.b.c', 'value')
        self.assertEqual(data, {'a': {'b': {'c': 'value'}}})
        
    def test_prepare_request(self):
        """Test preparing request data."""
        request_data = self.adapter._prepare_request(
            "Test prompt", 
            max_tokens=100
        )
        expected = {
            'input': {'text': 'Test prompt'},
            'params': {'max_tokens': 100}
        }
        self.assertEqual(request_data, expected)


class TestUnifiedAPIManager(unittest.TestCase):
    """Test cases for UnifiedAPIManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = UnifiedAPIManager()
        
    def test_create_openai_adapter(self):
        """Test creating OpenAI adapter."""
        config = {'api_key': 'test-key'}
        adapter = self.manager.create_adapter('openai', config)
        self.assertIsInstance(adapter, OpenAIAdapter)
        
    def test_create_restful_adapter(self):
        """Test creating RESTful adapter."""
        config = {'endpoint': 'http://localhost:8000/api/chat'}
        adapter = self.manager.create_adapter('restful', config)
        self.assertIsInstance(adapter, RESTfulAdapter)
        
    def test_create_unsupported_adapter(self):
        """Test creating unsupported adapter."""
        config = {}
        with self.assertRaises(ValueError):
            self.manager.create_adapter('unsupported', config)


class TestUnifiedAPIModel(unittest.TestCase):
    """Test cases for UnifiedAPIModel."""
    
    @patch('opencompass.models.unified_api.UnifiedAPIManager')
    def setUp(self, mock_manager):
        """Set up test fixtures."""
        # Mock the adapter
        self.mock_adapter = Mock()
        mock_manager.return_value.create_adapter.return_value = self.mock_adapter
        
        self.config = {
            'adapter_type': 'openai',
            'api_key': 'test-key'
        }
        
        self.model = UnifiedAPIModel(
            path='test-model',
            config=self.config,
            query_per_second=1
        )
        
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.model.path, 'test-model')
        self.assertEqual(self.model.config, self.config)
        
    def test_generate_single_input(self):
        """Test generating response for single input."""
        self.mock_adapter.generate.return_value = "Test response"
        
        results = self.model.generate(["Hello world"])
        self.assertEqual(results, ["Test response"])
        self.mock_adapter.generate.assert_called_once()
        
    def test_generate_multiple_inputs(self):
        """Test generating responses for multiple inputs."""
        self.mock_adapter.generate.side_effect = ["Response 1", "Response 2"]
        
        results = self.model.generate(["Hello", "World"])
        self.assertEqual(results, ["Response 1", "Response 2"])
        self.assertEqual(self.mock_adapter.generate.call_count, 2)


if __name__ == '__main__':
    unittest.main()