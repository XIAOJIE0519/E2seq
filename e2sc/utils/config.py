"""Configuration management for E2sc."""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


def _get_project_root() -> Path:
    """Get project root directory by detecting project markers.
    
    Looks for markers like 'start.py', 'e2sc/' directory, or 'pyproject.toml'
    in the current directory or parent directories.
    """
    # Start from the location of this config module
    current = Path(__file__).resolve().parent  # e2sc/utils/
    current = current.parent  # e2sc/
    current = current.parent  # project root
    
    # Check for project markers
    markers = ['start.py', 'e2sc', 'pyproject.toml', 'E2SC_TECHNICAL_DESIGN.md']
    for marker in markers:
        if (current / marker).exists():
            return current
    
    # Fallback: try current working directory
    cwd = Path.cwd()
    for marker in markers:
        if (cwd / marker).exists():
            return cwd
    
    # Last fallback: return the directory containing this file
    return current


def _resolve_db_path(path_str: str, project_root: Path, default_subdir: str) -> Path:
    """Resolve database/config path, supporting relative paths.
    
    Args:
        path_str: Path string from config (may be relative or absolute)
        project_root: Project root directory
        default_subdir: Default subdirectory under project root
        
    Returns:
        Resolved absolute Path
    """
    path = Path(path_str)
    
    # If it's an absolute path, use it as-is
    if path.is_absolute():
        return path
    
    # If it starts with ~, expand home
    if path_str.startswith('~'):
        return path.expanduser()
    
    # Otherwise, treat as relative to project root
    resolved = project_root / path
    return resolved.resolve()


class LLMConfig(BaseSettings):
    """LLM configuration."""
    provider: str = Field(default="openai")
    api_key: str = Field(default="")
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=163840)
    
    class Config:
        env_prefix = "E2SC_"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    db_path: str = Field(default="databases")  # 相对于项目根目录
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)
    
    class Config:
        env_prefix = "E2SC_"


class APIConfig(BaseSettings):
    """External API keys and configuration."""
    biogrid_api_key: str = Field(default="biological")
    biogrid_rate_limit: int = Field(default=10)

    class Config:
        env_prefix = "E2SC_"


class EmbeddingConfig(BaseSettings):
    """Embedding model configuration for RAG."""
    model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    model_dimension: int = Field(default=384)
    normalize: bool = Field(default=True)
    local_only: bool = Field(default=True)  # 优先使用本地模型
    model_paths: Dict[str, str] = Field(default_factory=dict)  # {model_id: local_path}
    custom_models: List[Dict[str, Any]] = Field(default_factory=list)  # 用户新增模型

    class Config:
        env_prefix = "E2SC_"


class E2scConfig:
    """Main configuration class."""

    # Class-level project root cache
    _project_root: Optional[Path] = None

    def __init__(self, config_path: Optional[Path] = None):
        # Determine project root once per class
        if E2scConfig._project_root is None:
            E2scConfig._project_root = _get_project_root()
        
        self.project_root = E2scConfig._project_root
        
        # Use project-local .e2sc directory
        self.config_dir = self.project_root / ".e2sc"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "logs").mkdir(exist_ok=True)
        
        # Resolve database path relative to project root
        self._resolved_db_dir = _resolve_db_path(
            self._get_default_db_path(),
            self.project_root,
            "databases"
        )
        self._resolved_db_dir.mkdir(parents=True, exist_ok=True)
        
        # Config file path
        if config_path is None:
            config_path = self.config_dir / "config.yaml"
        self.config_path = Path(config_path)
        
        self._load_config()

    def _get_default_db_path(self) -> str:
        """Get default database path, preferring project-local directories."""
        # Check if 'database' directory exists in project root (for CSV source files)
        if self.project_root / "database" != self.project_root:
            return "database"
        return "databases"

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve a path string relative to project root."""
        return _resolve_db_path(path_str, self.project_root, "databases")

    def _load_config(self) -> None:
        """Load configuration."""
        file_config = {}
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}

        # Resolve database path from config or use default
        db_path_from_config = file_config.get("database", {}).get("db_path", None)
        if db_path_from_config:
            # 尝试将用户配置转为绝对路径
            resolved = self._resolve_path(db_path_from_config)
            self._resolved_db_dir = resolved
            self._resolved_db_dir.mkdir(parents=True, exist_ok=True)

        self.llm = LLMConfig(**file_config.get("llm", {}))
        self.database = DatabaseConfig(**file_config.get("database", {}))
        self.api = APIConfig(**file_config.get("api", {}))
        self.embedding = EmbeddingConfig(**file_config.get("embedding", {}))

        # 用 resolved 路径覆盖（用于运行时）
        self.database.db_path = str(self._resolved_db_dir)

    def _get_relative_path(self, absolute_path: Path) -> str:
        """Convert absolute path to relative path from project root.
        
        Returns the relative path if it's under project root,
        otherwise returns the absolute path as-is.
        """
        try:
            rel = absolute_path.relative_to(self.project_root)
            # 返回Unix风格相对路径（使用正斜杠）
            return str(rel).replace('\\', '/')
        except ValueError:
            # 不在项目根目录下，返回绝对路径
            return str(absolute_path)

    @property
    def resolved_db_path(self) -> Path:
        """Get resolved database directory path."""
        return self._resolved_db_dir

    @property
    def resolved_config_path(self) -> Path:
        """Get resolved config file path."""
        return self.config_path

    def save(self) -> None:
        """Save configuration with relative paths for portability."""
        # 使用相对路径保存，便于项目移动
        db_path_for_save = self._get_relative_path(self._resolved_db_dir)

        config_dict = {
            "llm": {
                "provider": self.llm.provider,
                "api_key": self.llm.api_key,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
            },
            "database": {
                "db_path": db_path_for_save,  # 保存为相对路径
                "cache_enabled": self.database.cache_enabled,
                "cache_ttl": self.database.cache_ttl,
            },
            "api": {
                "biogrid_api_key": self.api.biogrid_api_key,
                "biogrid_rate_limit": self.api.biogrid_rate_limit,
            },
            "embedding": {
                "model_name": self.embedding.model_name,
                "model_dimension": self.embedding.model_dimension,
                "normalize": self.embedding.normalize,
                "local_only": self.embedding.local_only,
                "model_paths": self.embedding.model_paths,
                "custom_models": self.embedding.custom_models,
            },
        }
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False)

    def update_llm(self, provider: str, api_key: str, model: str) -> None:
        """Update LLM configuration."""
        self.llm.provider = provider
        self.llm.api_key = api_key
        self.llm.model = model
        self.save()

    def update_embedding(self, model_name: str, model_dimension: int = None,
                        normalize: bool = None, local_only: bool = None,
                        model_paths: Dict[str, str] = None,
                        custom_models: List[Dict[str, Any]] = None) -> None:
        """Update embedding configuration and clear cached models."""
        self.embedding.model_name = model_name
        if model_dimension is not None:
            self.embedding.model_dimension = model_dimension
        if normalize is not None:
            self.embedding.normalize = normalize
        if local_only is not None:
            self.embedding.local_only = local_only
        if model_paths is not None:
            self.embedding.model_paths = model_paths
        if custom_models is not None:
            self.embedding.custom_models = custom_models
        self.save()
        # 清除缓存，使新模型生效
        from e2sc.data.vector_store import clear_embedding_cache
        clear_embedding_cache()


_config: Optional[E2scConfig] = None


def get_config() -> E2scConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = E2scConfig()
    return _config
