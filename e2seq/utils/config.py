"""Configuration management for E2seq."""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


# Keep the source identifiers in one place so the configuration, API, and
# agent use the same vocabulary.  These are effective defaults only; the
# user-provided default prompt remains intentionally empty.
DEFAULT_ANSWER_APIS = [
    "uniprot", "mygene", "quickgo", "ensembl", "chembl", "pubmed",
    "europepmc", "reactome", "gtex", "hpa", "gwas", "civic",
    "alliance", "opentargets", "clinvar", "cbioportal", "omnipath",
    "intact", "humanbase", "clinicaltrials",
]
DEFAULT_ANSWER_DBS = ["string", "hmdb", "trrust", "gutmgene"]


class LLMConfig(BaseSettings):
    """LLM configuration."""
    provider: str = Field(default="openai")
    api_key: str = Field(default="")
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=163840)
    thinking_enabled: bool = Field(default=False)
    thinking_effort: str = Field(default="high")
    # Custom base URL for the active provider (legacy single-value field)
    base_url: Optional[str] = Field(default=None)
    # Per-provider custom base URLs (e.g. a6api, custom proxies, etc.)
    # Keys: openai | anthropic | gemini | deepseek | siliconflow | sdu | glm | kimi | ollama
    base_urls: Dict[str, str] = Field(default_factory=dict)
    # Encrypted credentials and last selected model for each provider.
    # The legacy api_key/model fields above remain the active profile so
    # existing agent and CLI call sites continue to work unchanged.
    provider_profiles: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    model_config = ConfigDict(env_prefix="E2SEQ_")


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    db_path: str = Field(default="~/.e2seq/databases")
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)

    model_config = ConfigDict(env_prefix="E2SEQ_")


class APIConfig(BaseSettings):
    """External API keys and configuration."""
    # BioGRID does not provide an anonymous public REST key.  Keep this empty
    # until the user supplies their own key; a placeholder must never be sent
    # to the service and then reported as biological zero coverage.
    biogrid_api_key: str = Field(default="")
    biogrid_rate_limit: int = Field(default=10)

    model_config = ConfigDict(env_prefix="E2SEQ_")


class EmbeddingConfig(BaseSettings):
    """Embedding model configuration for RAG."""
    model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    model_dimension: int = Field(default=384)
    normalize: bool = Field(default=True)
    # Keep the provider separate from ``local_only`` for backwards
    # compatibility with older config files and clients.
    provider: str = Field(default="local")  # local | hf_api
    # Stored encrypted when entered from the web UI; environment variables
    # remain supported as an external override.
    hf_api_token: str = Field(default="")
    local_only: bool = Field(default=True)  # historical compatibility field
    model_paths: Dict[str, str] = Field(default_factory=dict)  # {model_id: local_path}
    custom_models: List[Dict[str, Any]] = Field(default_factory=list)  # User-defined models / 用户自定义模型

    model_config = ConfigDict(env_prefix="E2SEQ_")


class AnswerSettingsConfig(BaseSettings):
    """Source policy used for answers created in the future.

    Dataset context is intentionally stored on each dataset/session instead
    of in this global source-settings object.  This prevents one project's
    prompt from silently becoming a hidden instruction for another project.
    """

    enabled_apis: List[str] = Field(default_factory=lambda: list(DEFAULT_ANSWER_APIS))
    enabled_dbs: List[str] = Field(default_factory=lambda: list(DEFAULT_ANSWER_DBS))
    # False preserves the per-dataset source choices made before this setting
    # existed.  Once the user saves this panel, it becomes the answer-time
    # source policy for new answers.
    configured: bool = Field(default=False)

    model_config = ConfigDict(env_prefix="E2SEQ_")


class E2seqConfig:
    """Main configuration class."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".e2seq" / "config.yaml"
        self.config_dir = Path.home() / ".e2seq"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "logs").mkdir(exist_ok=True)
        (self.config_dir / "databases").mkdir(exist_ok=True)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration."""
        file_config = {}
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}

        self.llm = LLMConfig(**file_config.get("llm", {}))
        # Backward-compatible in-memory migration from the historical
        # single-provider configuration.
        if self.llm.provider and self.llm.api_key and self.llm.provider not in self.llm.provider_profiles:
            self.llm.provider_profiles[self.llm.provider] = {
                "api_key": self.llm.api_key,
                "model": self.llm.model,
                "base_url": self.llm.base_url or self.get_provider_base_url(self.llm.provider) or "",
            }
        database_config = dict(file_config.get("database", {}) or {})
        # Deployment environments may need the mutable state/vector database
        # outside the user's home directory (for example, a service account
        # whose home is read-only).  Environment configuration is an explicit
        # runtime override and therefore must win over the persisted path.
        env_db_path = os.environ.get("E2SEQ_DB_PATH", "").strip()
        if env_db_path:
            database_config["db_path"] = env_db_path
        self.database = DatabaseConfig(**database_config)
        self.api = APIConfig(**file_config.get("api", {}))
        self.embedding = EmbeddingConfig(**file_config.get("embedding", {}))
        # Migrate the historical global prompt field out of the source
        # settings.  Prompts now belong to each dataset/session, so an old
        # config value must never be loaded or applied as hidden context.
        answer_settings = dict(file_config.get("answer_settings", {}) or {})
        answer_settings.pop("default_prompt", None)
        self.answer_settings = AnswerSettingsConfig(**answer_settings)

    def save(self) -> None:
        """Save configuration."""
        config_dict = {
            "llm": {
                "provider": self.llm.provider,
                "api_key": self.llm.api_key,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "base_url": self.llm.base_url,
                "base_urls": dict(self.llm.base_urls or {}),
                "provider_profiles": dict(self.llm.provider_profiles or {}),
                "thinking_enabled": self.llm.thinking_enabled,
                "thinking_effort": self.llm.thinking_effort,
            },
            "database": {
                "db_path": self.database.db_path,
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
                "provider": self.embedding.provider,
                "hf_api_token": self.embedding.hf_api_token,
                "local_only": self.embedding.local_only,
                "model_paths": self.embedding.model_paths,
                "custom_models": self.embedding.custom_models,
            },
            "answer_settings": {
                "enabled_apis": list(self.answer_settings.enabled_apis or []),
                "enabled_dbs": list(self.answer_settings.enabled_dbs or []),
                "configured": bool(self.answer_settings.configured),
            },
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False)

    def set_provider_base_url(self, provider: str, base_url: Optional[str]) -> None:
        """Set/clear per-provider custom base URL. Empty string clears the entry."""
        if not isinstance(self.llm.base_urls, dict):
            self.llm.base_urls = {}
        if base_url:
            self.llm.base_urls[provider] = base_url.strip()
        else:
            self.llm.base_urls.pop(provider, None)
        self.save()

    def get_provider_base_url(self, provider: str) -> Optional[str]:
        """Return custom base URL for provider, or None if not set."""
        bu = (self.llm.base_urls or {}).get(provider)
        return bu if bu else None

    def get_provider_profile(self, provider: str) -> Dict[str, str]:
        """Return a provider profile, including legacy active configuration."""
        profile = dict((self.llm.provider_profiles or {}).get(provider, {}))
        if not profile and self.llm.provider == provider:
            profile = {
                "api_key": self.llm.api_key,
                "model": self.llm.model,
                "base_url": self.llm.base_url or self.get_provider_base_url(provider) or "",
            }
        return profile

    def set_provider_profile(
        self,
        provider: str,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
    ) -> None:
        """Persist one provider profile without changing the active provider."""
        if not isinstance(self.llm.provider_profiles, dict):
            self.llm.provider_profiles = {}
        existing = self.get_provider_profile(provider)
        self.llm.provider_profiles[provider] = {
            "api_key": api_key or existing.get("api_key", ""),
            "model": model or existing.get("model", ""),
            "base_url": (base_url if base_url is not None else existing.get("base_url", "")) or "",
        }
        if base_url is not None:
            if base_url:
                self.llm.base_urls[provider] = base_url
            else:
                self.llm.base_urls.pop(provider, None)
        self.save()

    def clear_provider_profile(self, provider: str) -> None:
        """Remove one stored provider profile."""
        if isinstance(self.llm.provider_profiles, dict):
            self.llm.provider_profiles.pop(provider, None)
        if isinstance(self.llm.base_urls, dict):
            self.llm.base_urls.pop(provider, None)
        self.save()

    def update_llm(self, provider: str, api_key: str, model: str,
                   base_url: Optional[str] = None,
                   thinking_enabled: Optional[bool] = None,
                   thinking_effort: Optional[str] = None) -> None:
        """Update LLM configuration.

        For the ``custom`` provider, ``base_url`` is stored in the dedicated
        ``llm.base_url`` field so it is used when the agent initializes.
        For other providers, it goes into the per-provider ``base_urls`` dict.
        """
        self.llm.provider = provider
        self.llm.api_key = api_key
        self.llm.model = model
        if thinking_enabled is not None:
            self.llm.thinking_enabled = bool(thinking_enabled)
        if thinking_effort is not None and str(thinking_effort).strip():
            self.llm.thinking_effort = str(thinking_effort).strip().lower()
        if provider == "custom":
            self.llm.base_url = base_url
        elif base_url is not None:
            self.set_provider_base_url(provider, base_url)
            self.llm.base_url = self.get_provider_base_url(provider)
        else:
            self.llm.base_url = self.get_provider_base_url(provider)
        if not isinstance(self.llm.provider_profiles, dict):
            self.llm.provider_profiles = {}
        self.llm.provider_profiles[provider] = {
            "api_key": api_key,
            "model": model,
            "base_url": self.llm.base_url or "",
        }
        self.save()

    def update_embedding(self, model_name: str, model_dimension: int = None,
                        normalize: bool = None, local_only: bool = None,
                        model_paths: Dict[str, str] = None,
                        custom_models: List[Dict[str, Any]] = None,
                        provider: str = None,
                        hf_api_token: str = None) -> None:
        """Update embedding configuration and clear cached models."""
        self.embedding.model_name = model_name
        if model_dimension is not None:
            self.embedding.model_dimension = model_dimension
        if normalize is not None:
            self.embedding.normalize = normalize
        if provider is not None:
            provider = str(provider).strip().lower()
            if provider not in {"local", "hf_api"}:
                raise ValueError("Embedding provider must be 'local' or 'hf_api'.")
            self.embedding.provider = provider
            # Keep the historical field synchronized for older callers and
            # config readers that still inspect local_only.
            self.embedding.local_only = provider == "local"
        elif local_only is not None:
            # Legacy callers may still update local_only. Do not silently
            # switch an explicitly configured HF API provider in that case.
            self.embedding.local_only = local_only
        if hf_api_token is not None:
            self.embedding.hf_api_token = hf_api_token
        if model_paths is not None:
            self.embedding.model_paths = model_paths
        if custom_models is not None:
            self.embedding.custom_models = custom_models
        self.save()
        # Clear both the embedding-function cache and lazy model config.
        from e2seq.data.vector_store import clear_embedding_cache
        clear_embedding_cache()


_config: Optional[E2seqConfig] = None


def get_config() -> E2seqConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = E2seqConfig()
    return _config
