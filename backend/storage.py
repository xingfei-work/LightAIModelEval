"""Object storage integration with MinIO."""

import io
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from minio import Minio
from minio.error import S3Error


class StorageManager:
    """Storage manager for handling object storage operations with MinIO."""
    
    def __init__(self, 
                 endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 secure: bool = True):
        """Initialize storage manager.
        
        Args:
            endpoint: MinIO endpoint (e.g., 'localhost:9000')
            access_key: Access key for MinIO
            secret_key: Secret key for MinIO
            secure: Use HTTPS if True, HTTP if False
        """
        # Use environment variables if not provided
        endpoint = endpoint or os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        access_key = access_key or os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        secret_key = secret_key or os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
    def create_bucket(self, bucket_name: str) -> bool:
        """Create a bucket if it doesn't exist.
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            True if created or already exists, False on error
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
            return True
        except S3Error as e:
            print(f"Error creating bucket {bucket_name}: {e}")
            return False
            
    def upload_file(self, 
                   bucket_name: str,
                   object_name: str,
                   file_path: str,
                   content_type: str = 'application/octet-stream') -> bool:
        """Upload a file to storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            file_path: Path to the local file
            content_type: MIME type of the file
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        try:
            self.create_bucket(bucket_name)
            self.client.fput_object(
                bucket_name, object_name, file_path, content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Error uploading file {file_path}: {e}")
            return False
            
    def upload_data(self,
                   bucket_name: str,
                   object_name: str,
                   data: bytes,
                   content_type: str = 'application/octet-stream') -> bool:
        """Upload data to storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            data: Data to upload
            content_type: MIME type of the data
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        try:
            self.create_bucket(bucket_name)
            self.client.put_object(
                bucket_name, object_name, io.BytesIO(data), len(data),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Error uploading data: {e}")
            return False
            
    def upload_json(self,
                   bucket_name: str,
                   object_name: str,
                   json_data: Dict[Any, Any]) -> bool:
        """Upload JSON data to storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            json_data: JSON data to upload
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        try:
            json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')
            return self.upload_data(
                bucket_name, object_name, json_bytes, 'application/json'
            )
        except Exception as e:
            print(f"Error serializing or uploading JSON data: {e}")
            return False
            
    def download_file(self,
                     bucket_name: str,
                     object_name: str,
                     file_path: str) -> bool:
        """Download a file from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            file_path: Path to save the downloaded file
            
        Returns:
            True if downloaded successfully, False otherwise
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            with open(file_path, 'wb') as file_data:
                for data in response.stream(32*1024):
                    file_data.write(data)
            response.close()
            response.release_conn()
            return True
        except S3Error as e:
            print(f"Error downloading file {object_name}: {e}")
            return False
            
    def download_data(self,
                     bucket_name: str,
                     object_name: str) -> Optional[bytes]:
        """Download data from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            
        Returns:
            Data bytes if downloaded successfully, None otherwise
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.data
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading data {object_name}: {e}")
            return None
            
    def download_json(self,
                     bucket_name: str,
                     object_name: str) -> Optional[Dict[Any, Any]]:
        """Download JSON data from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object in storage
            
        Returns:
            JSON data if downloaded successfully, None otherwise
        """
        try:
            data = self.download_data(bucket_name, object_name)
            if data:
                return json.loads(data.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Error parsing JSON data: {e}")
            return None
            
    def list_objects(self, bucket_name: str, prefix: str = '') -> list:
        """List objects in a bucket.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Prefix to filter objects
            
        Returns:
            List of object names
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects: {e}")
            return []
            
    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """Delete an object from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting object {object_name}: {e}")
            return False
            
    def upload_evaluation_logs(self,
                              task_id: str,
                              logs: list) -> bool:
        """Upload evaluation logs for a task.
        
        Args:
            task_id: Task ID
            logs: List of log entries
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        bucket_name = "evaluation-logs"
        object_name = f"task-{task_id}/logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        log_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "logs": logs
        }
        
        return self.upload_json(bucket_name, object_name, log_data)
        
    def upload_evaluation_results(self,
                                task_id: str,
                                results: Dict[Any, Any]) -> bool:
        """Upload evaluation results for a task.
        
        Args:
            task_id: Task ID
            results: Evaluation results
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        bucket_name = "evaluation-results"
        object_name = f"task-{task_id}/results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        result_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        return self.upload_json(bucket_name, object_name, result_data)


# Example usage
if __name__ == "__main__":
    # Initialize storage manager
    storage_manager = StorageManager()
    
    # Example: Upload some test data
    test_data = {
        "message": "Hello, MinIO!",
        "timestamp": datetime.now().isoformat()
    }
    
    success = storage_manager.upload_json("test-bucket", "test-data.json", test_data)
    if success:
        print("Test data uploaded successfully")
    else:
        print("Failed to upload test data")