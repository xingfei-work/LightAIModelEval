"""Main entry point for the backend service."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import os
import json

from services.api_config_service import APISecurityManager, APIConfigService
from backend.database import DatabaseManager, User, APIConfig, EvaluationTask
from backend.storage import StorageManager

app = FastAPI(title="Light AI Model Evaluation Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
encryption_key = os.environ.get("ENCRYPTION_KEY") or None
security_manager = APISecurityManager(encryption_key)

# Initialize database
database_url = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")
db_manager = DatabaseManager(database_url)
config_service = APIConfigService(security_manager)

# Initialize storage
storage_manager = StorageManager()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(UserCreate):
    id: str
    created_at: str
    updated_at: str

class APIConfigCreate(BaseModel):
    name: str
    type: str  # 'cloud' or 'edge'
    provider: str
    endpoint: str
    auth_config: Dict
    protocol_type: str
    protocol_config: Optional[Dict] = None
    default_params: Optional[Dict] = None
    is_active: Optional[bool] = True

class APIConfigUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    provider: Optional[str] = None
    endpoint: Optional[str] = None
    auth_config: Optional[Dict] = None
    protocol_type: Optional[str] = None
    protocol_config: Optional[Dict] = None
    default_params: Optional[Dict] = None
    is_active: Optional[bool] = None

class APIConfigResponse(APIConfigCreate):
    id: str
    user_id: str
    created_at: str
    updated_at: str

class EvaluationTaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cloud_config_id: str
    edge_config_id: str
    dataset_info: Dict
    metrics_config: Dict

class EvaluationTaskUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    error_message: Optional[str] = None

class EvaluationTaskResponse(EvaluationTaskCreate):
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str

# Simulate user authentication (in production, use proper auth)
def get_current_user_id() -> str:
    # This is a placeholder - in real implementation, extract from JWT token
    return "user_123"

# API Routes
@app.get("/")
async def root():
    return {"message": "Light AI Model Evaluation Platform API"}

# User routes
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user."""
    user_data = user.dict()
    user_data["id"] = str(uuid.uuid4())
    # TODO: Hash password before storing
    user_data["password_hash"] = user_data.pop("password")
    
    try:
        created_user = db_manager.create_user(user_data)
        return {
            "id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
            "created_at": created_user.created_at.isoformat(),
            "updated_at": created_user.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API Config routes
@app.post("/api/configs", response_model=APIConfigResponse)
async def create_api_config(
    config: APIConfigCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new API configuration."""
    # Convert Pydantic model to dict
    config_data = config.dict()
    config_data["id"] = str(uuid.uuid4())
    config_data["user_id"] = user_id
    
    # Validate config
    is_valid, error_msg = config_service.validate_config(config_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Create config
    created_config = config_service.create_config(user_id, config_data)
    return created_config

@app.get("/api/configs", response_model=List[APIConfigResponse])
async def list_api_configs(user_id: str = Depends(get_current_user_id)):
    """List all API configurations for the current user."""
    configs = config_service.list_configs(user_id)
    return configs

@app.get("/api/configs/{config_id}", response_model=APIConfigResponse)
async def get_api_config(
    config_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific API configuration."""
    config = config_service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Check ownership
    if config.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return config

@app.put("/api/configs/{config_id}", response_model=APIConfigResponse)
async def update_api_config(
    config_id: str,
    config_update: APIConfigUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update an API configuration."""
    # Check if config exists and belongs to user
    existing_config = config_service.get_config(config_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if existing_config.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter out None values
    update_data = {k: v for k, v in config_update.dict().items() if v is not None}
    
    # Validate if updating critical fields
    if any(field in update_data for field in ['type', 'endpoint']):
        temp_config = {**existing_config, **update_data}
        is_valid, error_msg = config_service.validate_config(temp_config)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Update config
    updated_config = config_service.update_config(config_id, update_data)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
        
    return updated_config

@app.delete("/api/configs/{config_id}")
async def delete_api_config(
    config_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an API configuration."""
    # Check if config exists and belongs to user
    existing_config = config_service.get_config(config_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if existing_config.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete config
    success = config_service.delete_config(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration deleted successfully"}

# Evaluation Task routes
@app.post("/api/tasks", response_model=EvaluationTaskResponse)
async def create_evaluation_task(
    task: EvaluationTaskCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new evaluation task."""
    task_data = task.dict()
    task_data["id"] = str(uuid.uuid4())
    task_data["user_id"] = user_id
    task_data["status"] = "pending"
    
    try:
        created_task = db_manager.create_evaluation_task(task_data)
        # Convert datetime objects to strings for response
        dataset_info = created_task.dataset_info
        if isinstance(dataset_info, str):
            dataset_info = json.loads(dataset_info)
            
        metrics_config = created_task.metrics_config
        if isinstance(metrics_config, str):
            metrics_config = json.loads(metrics_config)
            
        return {
            "id": created_task.id,
            "user_id": created_task.user_id,
            "name": created_task.name,
            "description": created_task.description,
            "status": created_task.status,
            "cloud_config_id": created_task.cloud_config_id,
            "edge_config_id": created_task.edge_config_id,
            "dataset_info": dataset_info,
            "metrics_config": metrics_config,
            "created_at": created_task.created_at.isoformat(),
            "updated_at": created_task.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks", response_model=List[EvaluationTaskResponse])
async def list_evaluation_tasks(
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List evaluation tasks."""
    try:
        tasks = db_manager.get_evaluation_tasks(user_id, status)
        response_tasks = []
        for task in tasks:
            dataset_info = task.dataset_info
            if isinstance(dataset_info, str):
                dataset_info = json.loads(dataset_info)
                
            metrics_config = task.metrics_config
            if isinstance(metrics_config, str):
                metrics_config = json.loads(metrics_config)
                
            response_tasks.append({
                "id": task.id,
                "user_id": task.user_id,
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "cloud_config_id": task.cloud_config_id,
                "edge_config_id": task.edge_config_id,
                "dataset_info": dataset_info,
                "metrics_config": metrics_config,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "failed_at": task.failed_at.isoformat() if task.failed_at else None,
                "error_message": task.error_message
            })
        return response_tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=EvaluationTaskResponse)
async def get_evaluation_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific evaluation task."""
    try:
        task = db_manager.get_evaluation_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Check ownership
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        dataset_info = task.dataset_info
        if isinstance(dataset_info, str):
            dataset_info = json.loads(dataset_info)
            
        metrics_config = task.metrics_config
        if isinstance(metrics_config, str):
            metrics_config = json.loads(metrics_config)
            
        return {
            "id": task.id,
            "user_id": task.user_id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "cloud_config_id": task.cloud_config_id,
            "edge_config_id": task.edge_config_id,
            "dataset_info": dataset_info,
            "metrics_config": metrics_config,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "failed_at": task.failed_at.isoformat() if task.failed_at else None,
            "error_message": task.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}", response_model=EvaluationTaskResponse)
async def update_evaluation_task(
    task_id: str,
    task_update: EvaluationTaskUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update an evaluation task."""
    try:
        # Check if task exists and belongs to user
        existing_task = db_manager.get_evaluation_task(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if existing_task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Filter out None values
        update_data = {k: v for k, v in task_update.dict().items() if v is not None}
        
        # Update task
        updated_task = db_manager.update_evaluation_task(task_id, update_data)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        dataset_info = updated_task.dataset_info
        if isinstance(dataset_info, str):
            dataset_info = json.loads(dataset_info)
            
        metrics_config = updated_task.metrics_config
        if isinstance(metrics_config, str):
            metrics_config = json.loads(metrics_config)
            
        return {
            "id": updated_task.id,
            "user_id": updated_task.user_id,
            "name": updated_task.name,
            "description": updated_task.description,
            "status": updated_task.status,
            "cloud_config_id": updated_task.cloud_config_id,
            "edge_config_id": updated_task.edge_config_id,
            "dataset_info": dataset_info,
            "metrics_config": metrics_config,
            "created_at": updated_task.created_at.isoformat() if updated_task.created_at else None,
            "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None,
            "started_at": updated_task.started_at.isoformat() if updated_task.started_at else None,
            "completed_at": updated_task.completed_at.isoformat() if updated_task.completed_at else None,
            "failed_at": updated_task.failed_at.isoformat() if updated_task.failed_at else None,
            "error_message": updated_task.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_evaluation_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an evaluation task."""
    try:
        # Check if task exists and belongs to user
        existing_task = db_manager.get_evaluation_task(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if existing_task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Delete task
        success = db_manager.delete_evaluation_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)