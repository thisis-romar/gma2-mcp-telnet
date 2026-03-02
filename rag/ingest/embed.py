"""Abstract embedding interface and zero-vector stub for testing."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Implementations must supply model_name, dimensions, embed_one, and embed_many.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier for the embedding model."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Dimensionality of the embedding vectors."""
        ...

    @abstractmethod
    def embed_one(self, text: str) -> list[float]:
        """Embed a single text string."""
        ...

    @abstractmethod
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings."""
        ...


class ZeroVectorProvider(EmbeddingProvider):
    """Stub provider that returns zero vectors. For testing and development."""

    def __init__(self, dimensions: int = 384) -> None:
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return "zero-vector-stub"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_one(self, text: str) -> list[float]:
        return [0.0] * self._dimensions

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * self._dimensions for _ in texts]
