"""Test configuration."""

import pytest


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "llm_provider": "openai",
        "api_key": "test-key",
        "model": "gpt-4"
    }
