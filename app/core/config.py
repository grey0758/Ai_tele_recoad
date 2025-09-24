from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="AI Tele", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    computer_config_id: str = Field(default="", description="Computer config ID")
    
    # Database
    database_url: str = Field(default="sqlite:///./ai_tele.db", description="Database connection URL")
    
    # SSH Tunnel Configuration
    ssh_host: Optional[str] = Field(default=None, description="SSH server host")
    ssh_port: int = Field(default=22, description="SSH server port")
    ssh_username: Optional[str] = Field(default=None, description="SSH username")
    ssh_password: Optional[str] = Field(default=None, description="SSH password")
    ssh_key_path: Optional[str] = Field(default=None, description="SSH private key path")
    ssh_remote_host: str = Field(default="localhost", description="Remote database host")
    ssh_remote_port: int = Field(default=3306, description="Remote database port")
    ssh_local_port: int = Field(default=3307, description="Local tunnel port")
    
    # Database
    db_username: Optional[str] = Field(default=None, description="Database username")
    db_password: Optional[str] = Field(default=None, description="Database password")
    db_host: Optional[str] = Field(default=None, description="Database host")
    db_port: Optional[str] = Field(default=None, description="Database port")
    db_name: Optional[str] = Field(default=None, description="Database name")
    
    # OpenAI Configuration
    openai_url: Optional[str] = Field(default=None, description="OpenAI URL")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], description="Allowed CORS origins")
    
    # File Upload
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    
    # Server Configuration
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_username: Optional[str] = Field(default="default", description="Redis username")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Redis SSL")
    redis_decode_responses: bool = Field(default=True, description="Redis decode responses")

    # EventBus Configuration
    worker_count: int = Field(default=4, description="Number of event processing workers")
    max_queue_size: int = Field(default=1000, description="Maximum size of each event queue")
    dead_letter_queue_size: int = Field(default=100, description="Maximum size of dead letter queue")
    default_wait_for_result: bool = Field(default=True, description="Default wait for result")
    default_timeout: float = Field(default=30.0, description="Default event timeout in seconds")
    max_retry_count: int = Field(default=3, description="Maximum number of event retries")
    retry_delay: float = Field(default=1.0, description="Base delay between retries in seconds")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    enable_persistence: bool = Field(default=True, description="Enable event persistence to disk")
    persistence_path: str = Field(default="./logs/events", description="Path for event persistence")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
