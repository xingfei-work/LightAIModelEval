"""API Configuration Service for managing API configurations."""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from cryptography.fernet import Fernet


class APISecurityManager:
    """Manager for API security operations like encryption/decryption."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize security manager.
        
        Args:
            encryption_key: Optional encryption key. If not provided, a new one will be generated.
        """
        if encryption_key:
            self.cipher_suite = Fernet(encryption_key.encode())
        else:
            # In production, store this key securely
            self.encryption_key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.encryption_key)
            
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext.
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            Encrypted text
        """
        return self.cipher_suite.encrypt(plaintext.encode()).decode()
        
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt encrypted text.
        
        Args:
            encrypted_text: Text to decrypt
            
        Returns:
            Decrypted text
        """
        return self.cipher_suite.decrypt(encrypted_text.encode()).decode()
        
    def mask_key(self, key: str) -> str:
        """Mask API key for display.
        
        Args:
            key: Original key
            
        Returns:
            Masked key (e.g., sk-xxx***xyz)
        """
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:3]}***{key[-3:]}"


class APIConfigService:
    """Service for managing API configurations."""
    
    def __init__(self, security_manager: APISecurityManager):
        """Initialize API configuration service.
        
        Args:
            security_manager: Security manager for encryption/decryption
        """
        self.security_manager = security_manager
        # In production, this would be a database
        self.configs = {}
        
    def create_config(self, user_id: str, config_data: Dict) -> Dict:
        """Create a new API configuration.
        
        Args:
            user_id: ID of the user creating the config
            config_data: Configuration data
            
        Returns:
            Created configuration with ID
        """
        config_id = str(uuid.uuid4())
        
        # Encrypt sensitive fields
        encrypted_config = config_data.copy()
        if 'auth_config' in config_data:
            encrypted_config['auth_config'] = self.security_manager.encrypt(
                json.dumps(config_data['auth_config'])
            )
            
        config = {
            'id': config_id,
            'user_id': user_id,
            'name': config_data.get('name', ''),
            'type': config_data.get('type', 'cloud'),  # cloud or edge
            'provider': config_data.get('provider', ''),
            'endpoint': config_data.get('endpoint', ''),
            'auth_config': encrypted_config.get('auth_config', ''),
            'protocol_type': config_data.get('protocol_type', 'openai'),
            'protocol_config': config_data.get('protocol_config', {}),
            'default_params': config_data.get('default_params', {}),
            'is_active': config_data.get('is_active', True),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.configs[config_id] = config
        return config
        
    def get_config(self, config_id: str, decrypt_auth: bool = False) -> Optional[Dict]:
        """Get API configuration by ID.
        
        Args:
            config_id: Configuration ID
            decrypt_auth: Whether to decrypt auth config
            
        Returns:
            Configuration data or None if not found
        """
        config = self.configs.get(config_id)
        if not config:
            return None
            
        # Return a copy to prevent modification of stored data
        result = config.copy()
        
        # Decrypt auth config if requested
        if decrypt_auth and result.get('auth_config'):
            try:
                decrypted_auth = self.security_manager.decrypt(result['auth_config'])
                result['auth_config'] = json.loads(decrypted_auth)
            except Exception:
                # If decryption fails, return masked version
                result['auth_config'] = {'api_key': '***ENCRYPTED***'}
                
        return result
        
    def list_configs(self, user_id: str) -> List[Dict]:
        """List all configurations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of configurations (without decrypted auth)
        """
        configs = [
            {**config, 'auth_config': self.security_manager.mask_key(config.get('auth_config', ''))}
            for config in self.configs.values() 
            if config.get('user_id') == user_id
        ]
        return configs
        
    def update_config(self, config_id: str, update_data: Dict) -> Optional[Dict]:
        """Update an existing configuration.
        
        Args:
            config_id: Configuration ID
            update_data: Data to update
            
        Returns:
            Updated configuration or None if not found
        """
        if config_id not in self.configs:
            return None
            
        config = self.configs[config_id]
        
        # Handle auth_config encryption
        if 'auth_config' in update_data:
            update_data['auth_config'] = self.security_manager.encrypt(
                json.dumps(update_data['auth_config'])
            )
            
        # Update fields
        for key, value in update_data.items():
            if key in config:
                config[key] = value
                
        config['updated_at'] = datetime.now().isoformat()
        self.configs[config_id] = config
        return config.copy()
        
    def delete_config(self, config_id: str) -> bool:
        """Delete a configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if deleted, False if not found
        """
        if config_id in self.configs:
            del self.configs[config_id]
            return True
        return False
        
    def validate_config(self, config_data: Dict) -> tuple[bool, str]:
        """Validate configuration data.
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['name', 'type', 'endpoint']
        for field in required_fields:
            if not config_data.get(field):
                return False, f"Missing required field: {field}"
                
        # Validate type
        if config_data['type'] not in ['cloud', 'edge']:
            return False, "Invalid type. Must be 'cloud' or 'edge'"
            
        # Validate endpoint
        endpoint = config_data['endpoint']
        if not endpoint.startswith(('http://', 'https://')):
            return False, "Endpoint must start with http:// or https://"
            
        return True, ""


# Example usage
if __name__ == "__main__":
    # Initialize services
    security_manager = APISecurityManager()
    config_service = APIConfigService(security_manager)
    
    # Create a sample configuration
    user_id = "user_123"
    config_data = {
        "name": "OpenAI Production",
        "type": "cloud",
        "provider": "openai",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_config": {
            "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        "protocol_type": "openai",
        "default_params": {
            "temperature": 0.7,
            "max_tokens": 1024
        }
    }
    
    # Create config
    created_config = config_service.create_config(user_id, config_data)
    print("Created config:", created_config['id'])
    
    # List configs
    configs = config_service.list_configs(user_id)
    print("Configs for user:", len(configs))
    
    # Get config with decrypted auth
    retrieved_config = config_service.get_config(created_config['id'], decrypt_auth=True)
    print("Retrieved config with auth:", retrieved_config['name'])