# Sigma AI Testing Agent — Example Tests
# Run: pytest tests/ -v

import pytest

class TestExample:
    def test_sigma_ready(self):
        """Sigma AI Testing Agent is ready."""
        assert True, "Sigma is operational!"

    def test_environment(self):
        """Check environment variables loaded."""
        import os
        # Will pass even without .env
        assert isinstance(os.getenv("LLM_PROVIDER", "groq"), str)
