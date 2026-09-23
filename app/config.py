"""Runtime configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings shared by the API and future processing components."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="development", validation_alias="ECHOMIND_ENVIRONMENT")
    log_level: str = Field(default="INFO", validation_alias="ECHOMIND_LOG_LEVEL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", validation_alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", validation_alias="NEO4J_USERNAME")
    neo4j_password: str = Field(
        default="echomind-local-password", validation_alias="NEO4J_PASSWORD", repr=False
    )
    documents_path: Path = Field(default=Path("data/documents"), validation_alias="DOCUMENTS_PATH")
    extractions_path: Path = Field(
        default=Path("data/extractions"), validation_alias="EXTRACTIONS_PATH"
    )
    llm_provider: str = Field(default="openai", validation_alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY", repr=False)
    openai_model: str | None = Field(default=None, validation_alias="OPENAI_MODEL")
    embedding_provider: str = Field(default="openai", validation_alias="EMBEDDING_PROVIDER")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_embedding_dimensions: int = Field(
        default=1536,
        validation_alias="OPENAI_EMBEDDING_DIMENSIONS",
        gt=0,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide immutable settings instance."""
    return Settings()
