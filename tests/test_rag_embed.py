"""Tests for the RAG embedding interface."""

import pytest

from rag.ingest.embed import EmbeddingProvider, ZeroVectorProvider


class TestZeroVectorProvider:
    def test_model_name(self):
        p = ZeroVectorProvider()
        assert p.model_name == "zero-vector-stub"

    def test_default_dimensions(self):
        p = ZeroVectorProvider()
        assert p.dimensions == 384

    def test_custom_dimensions(self):
        p = ZeroVectorProvider(dimensions=128)
        assert p.dimensions == 128

    def test_embed_one_returns_zeros(self):
        p = ZeroVectorProvider(dimensions=3)
        result = p.embed_one("hello world")
        assert result == [0.0, 0.0, 0.0]

    def test_embed_one_correct_length(self):
        p = ZeroVectorProvider(dimensions=256)
        result = p.embed_one("test")
        assert len(result) == 256

    def test_embed_many(self):
        p = ZeroVectorProvider(dimensions=3)
        results = p.embed_many(["a", "b", "c"])
        assert len(results) == 3
        for r in results:
            assert r == [0.0, 0.0, 0.0]

    def test_embed_many_empty(self):
        p = ZeroVectorProvider(dimensions=3)
        results = p.embed_many([])
        assert results == []


class TestEmbeddingProviderABC:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            EmbeddingProvider()  # type: ignore[abstract]

    def test_subclass_must_implement_all(self):
        class PartialProvider(EmbeddingProvider):
            @property
            def model_name(self) -> str:
                return "partial"

            @property
            def dimensions(self) -> int:
                return 10

            # Missing embed_one and embed_many

        with pytest.raises(TypeError):
            PartialProvider()  # type: ignore[abstract]
