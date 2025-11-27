"""Unified API model for both cloud and edge APIs."""

import json
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Union

from opencompass.utils.logging import get_logger

from .base_api import BaseAPIModel


class BaseAPIAdapter(ABC):
    """Base class for API adapters."""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = get_logger()
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional arguments for the API call
            
        Returns:
            The generated response
        """
        pass
        
    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """Validate the API configuration.
        
        Args:
            config: The API configuration
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        pass


class OpenAIAdapter(BaseAPIAdapter):
    """OpenAI API adapter."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.endpoint = config.get('endpoint', 'https://api.openai.com/v1/chat/completions')
        self.model = config.get('model', 'gpt-3.5-turbo')
        
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        import requests
        
        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            **kwargs
        }
        
        try:
            response = requests.post(
                self.endpoint, 
                headers=headers, 
                json=data,
                timeout=(5, 30)  # (connect_timeout, read_timeout)
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
            
    def validate_config(self, config: Dict) -> bool:
        """Validate OpenAI API configuration."""
        required_fields = ['api_key']
        for field in required_fields:
            if field not in config or not config[field]:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True


class RESTfulAdapter(BaseAPIAdapter):
    """RESTful API adapter for edge models."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.endpoint = config.get('endpoint', '')
        self.method = config.get('method', 'POST')
        self.headers = config.get('headers', {})
        self.request_mapping = config.get('request_mapping', {})
        self.response_mapping = config.get('response_mapping', {})
        
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using RESTful API."""
        import requests
        
        # Prepare request data
        request_data = self._prepare_request(prompt, **kwargs)
        
        try:
            if self.method.upper() == 'GET':
                response = requests.get(
                    self.endpoint,
                    params=request_data,
                    headers=self.headers,
                    timeout=(5, 30)
                )
            else:
                response = requests.post(
                    self.endpoint,
                    json=request_data,
                    headers=self.headers,
                    timeout=(5, 30)
                )
                
            response.raise_for_status()
            result = response.json()
            return self._parse_response(result)
        except Exception as e:
            self.logger.error(f"RESTful API call failed: {e}")
            raise
            
    def _prepare_request(self, prompt: str, **kwargs) -> Dict:
        """Prepare request data according to mapping."""
        request_data = {}
        
        # Apply request mapping
        for source_key, target_key in self.request_mapping.items():
            if source_key == 'prompt':
                self._set_nested_value(request_data, target_key, prompt)
            elif source_key in kwargs:
                self._set_nested_value(request_data, target_key, kwargs[source_key])
                
        # Add any additional parameters not in mapping
        for key, value in kwargs.items():
            if key not in self.request_mapping:
                request_data[key] = value
                
        return request_data
        
    def _parse_response(self, response: Dict) -> str:
        """Parse response data according to mapping."""
        result = response
        
        # Navigate through response mapping to extract result
        for key in self.response_mapping.get('result', '').split('.'):
            if key and isinstance(result, dict) and key in result:
                result = result[key]
            else:
                break
                
        return str(result) if result else ""
        
    def _set_nested_value(self, data: Dict, key_path: str, value):
        """Set nested dictionary value using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    def validate_config(self, config: Dict) -> bool:
        """Validate RESTful API configuration."""
        required_fields = ['endpoint']
        for field in required_fields:
            if field not in config or not config[field]:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True


class UnifiedAPIManager:
    """Manager for different API adapters."""
    
    def __init__(self):
        self.adapters = {
            'openai': OpenAIAdapter,
            'restful': RESTfulAdapter
        }
        self.logger = get_logger()
        
    def create_adapter(self, adapter_type: str, config: Dict) -> BaseAPIAdapter:
        """Create an API adapter instance.
        
        Args:
            adapter_type: Type of adapter to create
            config: Configuration for the adapter
            
        Returns:
            An instance of the requested adapter
        """
        if adapter_type not in self.adapters:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
            
        adapter_class = self.adapters[adapter_type]
        adapter = adapter_class(config)
        
        if not adapter.validate_config(config):
            raise ValueError("Invalid configuration for adapter")
            
        return adapter


class UnifiedAPIModel(BaseAPIModel):
    """Unified API model that can work with both cloud and edge APIs."""
    
    is_api: bool = True
    
    def __init__(self,
                 path: str,
                 config: Dict,
                 query_per_second: int = 2,
                 max_seq_len: int = 2048,
                 meta_template: Optional[Dict] = None,
                 retry: int = 2,
                 generation_kwargs: Optional[Dict] = None):
        super().__init__(path=path,
                         max_seq_len=max_seq_len,
                         meta_template=meta_template,
                         retry=retry,
                         generation_kwargs=generation_kwargs)
                         
        self.logger = get_logger()
        self.query_per_second = query_per_second
        self.config = config
        
        # Create adapter
        manager = UnifiedAPIManager()
        self.adapter = manager.create_adapter(
            config.get('adapter_type', 'openai'), 
            config
        )
        
    def generate(self, 
                 inputs: List[str], 
                 max_out_len: int = 512,
                 **kwargs) -> List[str]:
        """Generate results given a list of inputs.
        
        Args:
            inputs: A list of input prompts
            max_out_len: Maximum output length
            **kwargs: Additional arguments for generation
            
        Returns:
            A list of generated responses
        """
        results = []
        
        if self.query_per_second > 0:
            # Use thread pool for parallel requests
            with ThreadPoolExecutor(max_workers=self.query_per_second) as executor:
                future_to_index = {
                    executor.submit(self._generate_single, input_text, max_out_len, **kwargs): i 
                    for i, input_text in enumerate(inputs)
                }
                
                # Collect results in order
                results = [None] * len(inputs)
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        results[index] = future.result()
                    except Exception as e:
                        self.logger.error(f"Error generating response for input {index}: {e}")
                        results[index] = ""
                        
        else:
            # Sequential generation
            for input_text in inputs:
                try:
                    result = self._generate_single(input_text, max_out_len, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error generating response: {e}")
                    results.append("")
                    
        return results
        
    def _generate_single(self, prompt: str, max_out_len: int, **kwargs) -> str:
        """Generate a single response."""
        # Merge generation_kwargs with passed kwargs
        generation_kwargs = self.generation_kwargs.copy() if self.generation_kwargs else {}
        generation_kwargs.update(kwargs)
        generation_kwargs['max_tokens'] = max_out_len
        
        # Retry mechanism
        for attempt in range(self.retry + 1):
            try:
                return self.adapter.generate(prompt, **generation_kwargs)
            except Exception as e:
                if attempt == self.retry:
                    raise e
                else:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return ""  # Should not reach here