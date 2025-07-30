"""
OpenAI and Azure OpenAI client management for embeddings.
"""

import logging
from os import environ
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from ..utils.env_config import read_env_config, set_env

OpenAIClientType = TypeVar("OpenAIClientType")

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
except ImportError:
    # Create mock classes for when OpenAI is not available
    class _MockAzureOpenAI:
        pass

    class _MockOpenAI:
        pass

    class _MockAsyncAzureOpenAI:
        pass

    class _MockAsyncOpenAI:
        pass

    AzureOpenAI = _MockAzureOpenAI  # type: ignore
    OpenAI = _MockOpenAI  # type: ignore
    AsyncAzureOpenAI = _MockAsyncAzureOpenAI  # type: ignore
    AsyncOpenAI = _MockAsyncOpenAI  # type: ignore

logger = logging.getLogger(__name__)


def is_azure() -> bool:
    """Check if the environment is configured for Azure OpenAI.

    Returns:
        bool: True if the AZURE_OPENAI_ENABLED environment variable is set to '1' or 'true'
        (case-insensitive), False otherwise.
    """
    value = environ.get("AZURE_OPENAI_ENABLED", "0").lower()
    azure = value in ("1", "true", "yes")
    if azure:
        logger.debug("Azure OpenAI support is enabled via AZURE_OPENAI_ENABLED.")
    else:
        logger.debug(
            "Azure OpenAI support is disabled (AZURE_OPENAI_ENABLED not set or false). "
            "Using OpenAI environment variables."
        )
    return azure


def build_openai_client(env_prefix: str = "EMBEDDING", **kwargs: Any) -> OpenAI:
    """Build OpenAI or AzureOpenAI client based on environment variables for embeddings.

    Args:
        env_prefix (str, optional): The prefix for the environment variables. Defaults to "EMBEDDING".
        **kwargs (Any): Additional keyword arguments for the OpenAI or AzureOpenAI client.

    Returns:
        OpenAI: The configured OpenAI or AzureOpenAI client instance.
    """
    env = read_env_config(env_prefix)

    # Extract OpenAI-specific parameters from environment
    client_kwargs = {}
    if "OPENAI_API_KEY" in env:
        client_kwargs["api_key"] = env["OPENAI_API_KEY"]
    if "OPENAI_ORGANIZATION" in env:
        client_kwargs["organization"] = env["OPENAI_ORGANIZATION"]

    # Extract Azure-specific parameters
    if "AZURE_OPENAI_API_KEY" in env:
        client_kwargs["api_key"] = env["AZURE_OPENAI_API_KEY"]
    if "AZURE_OPENAI_ENDPOINT" in env:
        client_kwargs["azure_endpoint"] = env["AZURE_OPENAI_ENDPOINT"]
    if "AZURE_OPENAI_API_VERSION" in env:
        client_kwargs["api_version"] = env["AZURE_OPENAI_API_VERSION"]

    # Merge with provided kwargs (kwargs take precedence)
    client_kwargs.update(kwargs)

    with set_env(**env):
        if is_azure():
            return AzureOpenAI(**client_kwargs)
        else:
            return OpenAI(**client_kwargs)


def build_langchain_embeddings(**kwargs):
    """Build LangChain embeddings for semantic chunking.

    Args:
        **kwargs: Additional arguments for embeddings initialization.

    Returns:
        Embeddings instance for LangChain.
    """
    try:
        from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

        if is_azure():
            return AzureOpenAIEmbeddings(**kwargs)
        else:
            return OpenAIEmbeddings(**kwargs)
    except ImportError:
        # Mock implementation for demo purposes
        class MockEmbeddings:
            def embed_documents(self, texts):
                return [[0.1, 0.2, 0.3] for _ in texts]

            def embed_query(self, text):
                return [0.1, 0.2, 0.3]

        return MockEmbeddings()


class BaseEmbeddingsClient:
    """Base class for OpenAI embeddings."""

    def __init__(self) -> None:
        self.client: Optional[Union[AzureOpenAI, OpenAI]] = None


class EmbeddingClient(BaseEmbeddingsClient):
    """Client for generating embeddings using OpenAI or Azure OpenAI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        azure_enabled: bool = False,
        **kwargs,
    ):
        """Initialize the embedding client.

        Args:
            api_key: OpenAI API key
            model: Embedding model to use
            azure_enabled: Whether to use Azure OpenAI
            **kwargs: Additional client configuration
        """
        super().__init__()
        self.model = model
        self.azure_enabled = azure_enabled

        try:
            if azure_enabled:
                self.client = AzureOpenAI(api_key=api_key, **kwargs)
            else:
                self.client = OpenAI(api_key=api_key, **kwargs)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors
        """
        if not self.client:
            logger.warning("No OpenAI client available, returning mock embeddings")
            return self._generate_mock_embeddings(texts)

        embeddings = []

        # Process in batches to respect rate limits
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(input=batch_texts, model=self.model)

                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)

                logger.debug(f"Generated embeddings for batch {i // batch_size + 1}")

            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i // batch_size + 1}: {e}")
                # Add mock embeddings for failed batch
                mock_batch = self._generate_mock_embeddings(batch_texts)
                embeddings.extend(mock_batch)

        return embeddings

    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def _generate_mock_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for testing purposes.

        Args:
            texts: List of texts to embed

        Returns:
            List of mock embedding vectors
        """
        import random

        embeddings = []
        for text in texts:
            # Generate deterministic mock embedding based on text hash
            # Note: This is for testing/mocking only, not cryptographic use
            random.seed(hash(text) % (2**32))  # nosec B311
            embedding = [random.uniform(-1, 1) for _ in range(1536)]  # nosec B311
            embeddings.append(embedding)

        return embeddings

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model.

        Returns:
            Dictionary with model information
        """
        # TODO: Implement actual model info retrieval
        # This would query the OpenAI API for model capabilities
        return {
            "model": self.model,
            "dimensions": 1536,  # Default for text-embedding-3-small
            "max_input_tokens": 8191,
            "azure_enabled": self.azure_enabled,
        }


def create_embedding_client(
    api_key: Optional[str] = None, model: str = "text-embedding-3-small", azure_enabled: Optional[bool] = None, **kwargs
) -> EmbeddingClient:
    """Create an embedding client with automatic configuration detection.

    Args:
        api_key: OpenAI API key (optional, will use environment variables)
        model: Embedding model to use
        azure_enabled: Whether to use Azure OpenAI (auto-detected if None)
        **kwargs: Additional client configuration

    Returns:
        Configured EmbeddingClient instance
    """
    if api_key is None:
        api_key = environ.get("OPENAI_API_KEY") or environ.get("OPENAI_KEY")

    if azure_enabled is None:
        azure_enabled = is_azure()

    return EmbeddingClient(api_key=api_key, model=model, azure_enabled=azure_enabled, **kwargs)
