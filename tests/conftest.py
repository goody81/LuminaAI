"""Test configuration and fixtures for LuminaAI tests."""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_pddl_plan():
    """Sample PDDL plan for testing."""
    return """
(define (plan test-plan)
  (:action initialize)
  (:action process)
  (:action finalize))
"""


@pytest.fixture
def invalid_pddl_plan():
    """Invalid PDDL plan for testing."""
    return "(define (plan test-plan"  # Missing closing parenthesis


@pytest.fixture
def dangerous_pddl_plan():
    """PDDL plan with dangerous patterns."""
    return """
(define (plan evil-plan)
  (:action exec('rm -rf /')))
"""
