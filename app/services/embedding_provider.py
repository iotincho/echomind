"""Port for generating vectors without coupling use cases to one provider."""

from typing import Protocol

from app.embeddings.contracts import EmbeddingSpec, EmbeddingVector


class EmbeddingProviderError(RuntimeError):
    """Raised when a configured provider cannot generate embeddings."""


class EmbeddingProvider(Protocol):
    """Provider port implemented by OpenAI today and local engines later."""

    spec: EmbeddingSpec

    def embed(self, texts: list[str]) -> list[EmbeddingVector]:
        """Create one vector for each non-empty input, in the original order."""


class UnavailableEmbeddingProvider:
    """Placeholder for a configured local provider not implemented yet."""

    def __init__(self, provider: str, model: str, dimensions: int) -> None:
        self.spec = EmbeddingSpec(provider=provider, model=model, dimensions=dimensions)

    def embed(self, texts: list[str]) -> list[EmbeddingVector]:
        raise EmbeddingProviderError(f"Embedding provider {self.spec.provider} is not implemented")
