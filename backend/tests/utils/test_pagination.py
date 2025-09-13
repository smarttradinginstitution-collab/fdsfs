import pytest
from app.Utils.pagination import clamp_limit

def test_clamp_limit_below_min():
    """Test that a limit below 1 is clamped to 1."""
    assert clamp_limit(0) == 1
    assert clamp_limit(-10) == 1

def test_clamp_limit_above_max():
    """Test that a limit above the max_limit is clamped to the max_limit."""
    assert clamp_limit(101) == 100
    assert clamp_limit(200) == 100
    assert clamp_limit(150, max_limit=120) == 120

def test_clamp_limit_within_range():
    """Test that a limit within the valid range remains unchanged."""
    assert clamp_limit(50) == 50
    assert clamp_limit(1) == 1
    assert clamp_limit(100) == 100
