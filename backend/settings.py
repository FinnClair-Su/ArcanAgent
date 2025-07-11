"""
ArcanAgent Backend Settings
Global configuration using Pydantic Settings
"""

from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://arcanagent:password@localhost:5432/arcanagent",
        description="PostgreSQL database URL"
    )
    NEO4J_URI: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j database URI"
    )
    NEO4J_USERNAME: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(default="password", description="Neo4j password")
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis URL for caching"
    )
    
    # MCP Configuration
    MCP_SERVER_HOST: str = Field(default="localhost", description="MCP server host")
    MCP_SERVER_PORT: int = Field(default=8080, description="MCP server port")
    MCP_CLIENT_TIMEOUT: int = Field(default=30, description="MCP client timeout in seconds")
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    
    # Vector Database Configuration
    VECTOR_DB_TYPE: str = Field(default="faiss", description="Vector database type")
    PINECONE_API_KEY: Optional[str] = Field(default=None, description="Pinecone API key")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, description="Pinecone environment")
    
    # Application Configuration
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    SECRET_KEY: str = Field(default="your-secret-key-here", description="Application secret key")
    JWT_SECRET: str = Field(default="your-jwt-secret-here", description="JWT secret key")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    
    # External Integrations
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    
    # Monitoring Configuration
    ENABLE_TELEMETRY: bool = Field(default=True, description="Enable telemetry")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")
    
    # Agent Configuration
    MAX_AGENTS: int = Field(default=22, description="Maximum number of agents")
    AGENT_TIMEOUT: int = Field(default=60, description="Agent timeout in seconds")
    
    # GRAG Configuration
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model for GRAG"
    )
    VECTOR_DIMENSION: int = Field(default=384, description="Vector dimension")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, description="Similarity threshold")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()