"""
Pytest configuration and fixtures
"""
import pytest

@pytest.fixture(autouse=True)
def reset_game_state():
    """
    Automatically reset game state before each test.
    This ensures each test starts with a clean slate.
    """
    yield
    # Cleanup after test if needed
