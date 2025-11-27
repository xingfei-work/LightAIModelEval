"""Database models and access layer using SQLAlchemy."""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from typing import Optional, Dict, List

Base = declarative_base()

class User(Base):
    """User model."""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'user'), default='user', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    api_configs = relationship("APIConfig", back_populates="user")
    evaluation_tasks = relationship("EvaluationTask", back_populates="user")


class APIConfig(Base):
    """API configuration model."""
    __tablename__ = 'api_configs'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum('cloud', 'edge'), nullable=False)  # cloud or edge
    provider = Column(String(50), nullable=False)
    endpoint = Column(Text, nullable=False)
    auth_config = Column(Text, nullable=False)  # Encrypted auth config
    protocol_type = Column(String(20), nullable=False)  # openai, restful, jsonrpc, etc.
    protocol_config = Column(Text)  # JSON string of protocol configuration
    default_params = Column(Text)   # JSON string of default parameters
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_configs")


class EvaluationTask(Base):
    """Evaluation task model."""
    __tablename__ = 'evaluation_tasks'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum('pending', 'running', 'completed', 'failed', 'cancelled'), 
                   default='pending', nullable=False)
    cloud_config_id = Column(String(36), ForeignKey('api_configs.id'))
    edge_config_id = Column(String(36), ForeignKey('api_configs.id'))
    dataset_info = Column(Text, nullable=False)  # JSON string of dataset information
    metrics_config = Column(Text, nullable=False)  # JSON string of metrics configuration
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="evaluation_tasks")


class MetricsResult(Base):
    """Metrics result model."""
    __tablename__ = 'metrics_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey('evaluation_tasks.id'), nullable=False)
    metric_type = Column(String(50), nullable=False)  # accuracy, latency, throughput, etc.
    cloud_value = Column(Float)  
    edge_value = Column(Float)
    diff_value = Column(Float)
    details = Column(Text)  # JSON string of additional details
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TaskLog(Base):
    """Task log model."""
    __tablename__ = 'task_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey('evaluation_tasks.id'), nullable=False)
    log_level = Column(Enum('debug', 'info', 'warning', 'error'), nullable=False)
    message = Column(Text, nullable=False)
    extra_data = Column(Text)  # JSON string of extra data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SystemConfig(Base):
    """System configuration model."""
    __tablename__ = 'system_configs'
    
    id = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self, database_url: str = "sqlite:///./test.db"):
        """Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        
    def get_db_session(self):
        """Get database session."""
        return self.SessionLocal()
        
    def create_user(self, user_data: Dict) -> User:
        """Create a new user.
        
        Args:
            user_data: User data
            
        Returns:
            Created user object
        """
        db = self.get_db_session()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        db = self.get_db_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
            
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        db = self.get_db_session()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
            
    def create_api_config(self, config_data: Dict) -> APIConfig:
        """Create a new API configuration.
        
        Args:
            config_data: API configuration data
            
        Returns:
            Created API configuration object
        """
        db = self.get_db_session()
        try:
            # Convert dict fields to JSON strings
            if 'protocol_config' in config_data and isinstance(config_data['protocol_config'], dict):
                config_data['protocol_config'] = json.dumps(config_data['protocol_config'])
                
            if 'default_params' in config_data and isinstance(config_data['default_params'], dict):
                config_data['default_params'] = json.dumps(config_data['default_params'])
                
            config = APIConfig(**config_data)
            db.add(config)
            db.commit()
            db.refresh(config)
            return config
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def get_api_configs(self, user_id: str) -> List[APIConfig]:
        """Get API configurations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of API configuration objects
        """
        db = self.get_db_session()
        try:
            return db.query(APIConfig).filter(APIConfig.user_id == user_id).all()
        finally:
            db.close()
            
    def get_api_config(self, config_id: str) -> Optional[APIConfig]:
        """Get API configuration by ID.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            API configuration object or None if not found
        """
        db = self.get_db_session()
        try:
            return db.query(APIConfig).filter(APIConfig.id == config_id).first()
        finally:
            db.close()
            
    def update_api_config(self, config_id: str, update_data: Dict) -> Optional[APIConfig]:
        """Update an API configuration.
        
        Args:
            config_id: Configuration ID
            update_data: Data to update
            
        Returns:
            Updated API configuration object or None if not found
        """
        db = self.get_db_session()
        try:
            config = db.query(APIConfig).filter(APIConfig.id == config_id).first()
            if not config:
                return None
                
            # Convert dict fields to JSON strings
            if 'protocol_config' in update_data and isinstance(update_data['protocol_config'], dict):
                update_data['protocol_config'] = json.dumps(update_data['protocol_config'])
                
            if 'default_params' in update_data and isinstance(update_data['default_params'], dict):
                update_data['default_params'] = json.dumps(update_data['default_params'])
                
            for key, value in update_data.items():
                setattr(config, key, value)
                
            config.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(config)
            return config
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def delete_api_config(self, config_id: str) -> bool:
        """Delete an API configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if deleted, False if not found
        """
        db = self.get_db_session()
        try:
            config = db.query(APIConfig).filter(APIConfig.id == config_id).first()
            if not config:
                return False
                
            db.delete(config)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def create_evaluation_task(self, task_data: Dict) -> EvaluationTask:
        """Create a new evaluation task.
        
        Args:
            task_data: Task data
            
        Returns:
            Created evaluation task object
        """
        db = self.get_db_session()
        try:
            # Convert dict fields to JSON strings
            if 'dataset_info' in task_data and isinstance(task_data['dataset_info'], dict):
                task_data['dataset_info'] = json.dumps(task_data['dataset_info'])
                
            if 'metrics_config' in task_data and isinstance(task_data['metrics_config'], dict):
                task_data['metrics_config'] = json.dumps(task_data['metrics_config'])
                
            task = EvaluationTask(**task_data)
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def get_evaluation_tasks(self, user_id: str, status: Optional[str] = None) -> List[EvaluationTask]:
        """Get evaluation tasks for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of evaluation task objects
        """
        db = self.get_db_session()
        try:
            query = db.query(EvaluationTask).filter(EvaluationTask.user_id == user_id)
            if status:
                query = query.filter(EvaluationTask.status == status)
            return query.all()
        finally:
            db.close()
            
    def get_evaluation_task(self, task_id: str) -> Optional[EvaluationTask]:
        """Get evaluation task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Evaluation task object or None if not found
        """
        db = self.get_db_session()
        try:
            return db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
        finally:
            db.close()
            
    def update_evaluation_task(self, task_id: str, update_data: Dict) -> Optional[EvaluationTask]:
        """Update an evaluation task.
        
        Args:
            task_id: Task ID
            update_data: Data to update
            
        Returns:
            Updated evaluation task object or None if not found
        """
        db = self.get_db_session()
        try:
            task = db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
            if not task:
                return None
                
            # Convert dict fields to JSON strings
            if 'dataset_info' in update_data and isinstance(update_data['dataset_info'], dict):
                update_data['dataset_info'] = json.dumps(update_data['dataset_info'])
                
            if 'metrics_config' in update_data and isinstance(update_data['metrics_config'], dict):
                update_data['metrics_config'] = json.dumps(update_data['metrics_config'])
                
            for key, value in update_data.items():
                setattr(task, key, value)
                
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            return task
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def delete_evaluation_task(self, task_id: str) -> bool:
        """Delete an evaluation task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False if not found
        """
        db = self.get_db_session()
        try:
            task = db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
            if not task:
                return False
                
            db.delete(task)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def create_metrics_result(self, result_data: Dict) -> MetricsResult:
        """Create a new metrics result.
        
        Args:
            result_data: Result data
            
        Returns:
            Created metrics result object
        """
        db = self.get_db_session()
        try:
            result = MetricsResult(**result_data)
            db.add(result)
            db.commit()
            db.refresh(result)
            return result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    def get_metrics_results(self, task_id: str) -> List[MetricsResult]:
        """Get metrics results for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of metrics result objects
        """
        db = self.get_db_session()
        try:
            return db.query(MetricsResult).filter(MetricsResult.task_id == task_id).all()
        finally:
            db.close()


# Example usage
if __name__ == "__main__":
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a sample user
    user_data = {
        "id": "user_123",
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password_here",
        "role": "user"
    }
    
    try:
        user = db_manager.create_user(user_data)
        print(f"Created user: {user.username}")
    except Exception as e:
        print(f"Error creating user: {e}")