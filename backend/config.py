"""
ArcanAgent Configuration System

Pydantic-based configuration system inspired by NagaAgent's successful design.
Supports both JSON files and environment variables with type safety and validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class SystemConfig(BaseModel):
    """System configuration settings."""
    version: str = Field(default="0.1.0", description="ArcanAgent version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    knowledge_base_path: str = Field(default="./knowledge_base", description="Path to knowledge base")
    enable_structured_logging: bool = Field(default=True, description="Enable structured logging")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class APIConfig(BaseModel):
    """API server configuration."""
    host: str = Field(default="127.0.0.1", description="API server host")
    port: int = Field(default=8000, ge=1, le=65535, description="API server port")
    enable_docs: bool = Field(default=True, description="Enable API documentation")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    request_timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")


class OpenAIConfig(BaseModel):
    """OpenAI LLM configuration."""
    api_key: str = Field(default="sk-your-openai-api-key-here", description="OpenAI API key")
    base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=1, le=8192, description="Maximum tokens")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")


class AnthropicConfig(BaseModel):
    """Anthropic Claude configuration."""
    api_key: str = Field(default="sk-ant-your-anthropic-api-key-here", description="Anthropic API key")
    model: str = Field(default="claude-3-sonnet-20240229", description="Claude model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=1, le=8192, description="Maximum tokens")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")


class LLMConfig(BaseModel):
    """Large Language Model configuration."""
    default_provider: str = Field(default="openai", description="Default LLM provider")
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    
    @field_validator('default_provider')
    @classmethod
    def validate_provider(cls, v):
        valid_providers = ['openai', 'anthropic']
        if v not in valid_providers:
            raise ValueError(f'LLM provider must be one of: {valid_providers}')
        return v


class LearningConfig(BaseModel):
    """Learning system configuration."""
    max_sessions: int = Field(default=10, ge=1, le=100, description="Maximum concurrent sessions")
    session_timeout_minutes: int = Field(default=60, ge=1, le=1440, description="Session timeout")
    enable_session_persistence: bool = Field(default=True, description="Enable session persistence")
    zpd_analysis_depth: int = Field(default=3, ge=1, le=10, description="ZPD analysis depth")
    cognitive_load_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Cognitive load threshold")
    enable_adaptive_difficulty: bool = Field(default=True, description="Enable adaptive difficulty")


class ArcanaAgentConfig(BaseModel):
    """Individual Arcana Agent configuration."""
    enabled: bool = Field(default=True, description="Enable this agent")
    description: str = Field(default="", description="Agent description")
    
    # Agent-specific settings can be added here
    class Config:
        extra = 'allow'  # Allow additional fields for agent-specific config


class AgentsConfig(BaseModel):
    """Agents system configuration."""
    max_tool_call_loops: int = Field(default=5, ge=1, le=20, description="Maximum tool call loops")
    tool_call_timeout: int = Field(default=30, ge=1, le=300, description="Tool call timeout")
    enable_agent_logging: bool = Field(default=True, description="Enable agent logging")
    
    # Individual Arcana Agents
    arcana_agents: Dict[str, ArcanaAgentConfig] = Field(
        default_factory=lambda: {
            "the_high_priestess": ArcanaAgentConfig(
                description="Knowledge state assessment and cognitive analysis"
            ),
            "the_hermit": ArcanaAgentConfig(
                description="Learning path planning and ZPD identification"
            ),
            "the_magician": ArcanaAgentConfig(
                description="Personalized content generation and bidirectional linking"
            ),
            "justice": ArcanaAgentConfig(
                description="Understanding assessment and learning effectiveness evaluation"
            ),
            "the_empress": ArcanaAgentConfig(
                description="Knowledge integration and memory consolidation"
            )
        }
    )


class ContextEngineeringConfig(BaseModel):
    """Context engineering configuration following the 6 core principles."""
    kv_cache_enabled: bool = Field(default=True, description="Enable KV-Cache optimization")
    static_prompt_caching: bool = Field(default=True, description="Enable static prompt caching")
    max_context_tokens: int = Field(default=8000, ge=1000, le=32000, description="Maximum context tokens")
    enable_context_compression: bool = Field(default=True, description="Enable context compression")
    compression_ratio: float = Field(default=0.7, ge=0.1, le=1.0, description="Context compression ratio")
    external_memory_threshold: int = Field(default=2000, ge=100, le=10000, description="External memory threshold")
    
    # Context diversity settings
    context_diversity: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_template_variation": True,
            "response_template_count": 3,
            "avoid_pattern_repetition": True
        }
    )


class BidirectionalLinksConfig(BaseModel):
    """Bidirectional links configuration."""
    max_links_per_note: int = Field(default=100, ge=1, le=1000, description="Maximum links per note")
    link_analysis_depth: int = Field(default=3, ge=1, le=10, description="Link analysis depth")
    enable_link_caching: bool = Field(default=True, description="Enable link caching")
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    
    # Density calculation settings
    density_calculation: Dict[str, Any] = Field(
        default_factory=lambda: {
            "algorithm": "weighted_degree",
            "normalization_factor": 10.0,
            "include_incoming_weight": 0.6,
            "include_outgoing_weight": 0.4
        }
    )
    
    # Context selection thresholds
    context_selection: Dict[str, Any] = Field(
        default_factory=lambda: {
            "full_text_threshold": 0.8,
            "summary_threshold": 0.5,
            "title_only_threshold": 0.2,
            "max_full_text_notes": 3,
            "max_summary_notes": 5,
            "max_title_notes": 10
        }
    )


class KnowledgeProcessingConfig(BaseModel):
    """Knowledge processing configuration."""
    markdown_extensions: List[str] = Field(
        default=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite", 
            "markdown.extensions.toc",
            "pymdownx.arithmatex",
            "pymdownx.betterem",
            "pymdownx.caret",
            "pymdownx.mark",
            "pymdownx.tilde"
        ],
        description="Markdown extensions to enable"
    )
    
    note_processing: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_generate_summaries": True,
            "summary_max_length": 200,
            "extract_key_concepts": True,
            "analyze_cognitive_complexity": True
        }
    )
    
    obsidian_compatibility: Dict[str, bool] = Field(
        default_factory=lambda: {
            "preserve_yaml_frontmatter": True,
            "support_wikilinks": True,
            "support_embedded_files": True,
            "support_tags": True,
            "support_aliases": True
        }
    )


class PerformanceConfig(BaseModel):
    """Performance and optimization configuration."""
    file_processing: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_file_size_mb": 10,
            "enable_async_io": True,
            "io_timeout_seconds": 10,
            "max_concurrent_files": 5
        }
    )
    
    caching: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_memory_cache": True,
            "memory_cache_size_mb": 100,
            "enable_disk_cache": True,
            "disk_cache_path": "./cache",
            "cache_cleanup_interval_hours": 24
        }
    )


class SecurityConfig(BaseModel):
    """Security configuration."""
    enable_cors: bool = Field(default=True, description="Enable CORS")
    max_request_size_mb: int = Field(default=50, ge=1, le=1000, description="Maximum request size")
    enable_input_validation: bool = Field(default=True, description="Enable input validation")
    sanitize_file_paths: bool = Field(default=True, description="Sanitize file paths")
    allowed_file_extensions: List[str] = Field(
        default=[".md", ".txt", ".json"],
        description="Allowed file extensions"
    )


class ArcanAgentConfig(BaseSettings):
    """Main ArcanAgent configuration class."""
    
    # Core configuration sections
    system: SystemConfig = Field(default_factory=SystemConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    learning: LearningConfig = Field(default_factory=LearningConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    context_engineering: ContextEngineeringConfig = Field(default_factory=ContextEngineeringConfig)
    bidirectional_links: BidirectionalLinksConfig = Field(default_factory=BidirectionalLinksConfig)
    knowledge_processing: KnowledgeProcessingConfig = Field(default_factory=KnowledgeProcessingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
        extra = 'ignore'
    
    def __init__(self, **kwargs):
        # Load from JSON file if it exists
        config_data = self._load_json_config()
        if config_data:
            # Merge JSON config with kwargs and env vars
            kwargs = {**config_data, **kwargs}
        
        super().__init__(**kwargs)
        
        # Post-initialization setup
        self._setup_directories()
        self._validate_configuration()
    
    def _load_json_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file."""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config.json: {e}")
        return None
    
    def _setup_directories(self):
        """Create necessary directories."""
        # Knowledge base directory
        kb_path = Path(self.system.knowledge_base_path)
        if not kb_path.exists():
            kb_path.mkdir(parents=True, exist_ok=True)
        
        # Logs directory
        logs_path = Path("logs")
        logs_path.mkdir(exist_ok=True)
        
        # Cache directory
        cache_path = Path(self.performance.caching.get("disk_cache_path", "./cache"))
        cache_path.mkdir(exist_ok=True)
    
    def _validate_configuration(self):
        """Validate configuration after loading."""
        # Check LLM API keys
        if self.llm.default_provider == "openai":
            if (not self.llm.openai.api_key or 
                self.llm.openai.api_key.startswith("sk-your-")):
                print("Warning: OpenAI API key not configured")
        
        elif self.llm.default_provider == "anthropic":
            if (not self.llm.anthropic.api_key or 
                self.llm.anthropic.api_key.startswith("sk-ant-your-")):
                print("Warning: Anthropic API key not configured")
    
    def save_to_file(self, filename: str = "config_backup.json"):
        """Save current configuration to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2, exclude_none=True))


# Global configuration instance
def load_config() -> ArcanAgentConfig:
    """Load and return the global configuration."""
    return ArcanAgentConfig()


# Create global config instance
config = load_config()


# Utility functions for backward compatibility
def get_llm_config():
    """Get the current LLM configuration."""
    if config.llm.default_provider == "openai":
        return config.llm.openai
    elif config.llm.default_provider == "anthropic":
        return config.llm.anthropic
    else:
        raise ValueError(f"Unknown LLM provider: {config.llm.default_provider}")


def get_knowledge_base_path() -> Path:
    """Get the knowledge base path as a Path object."""
    return Path(config.system.knowledge_base_path)