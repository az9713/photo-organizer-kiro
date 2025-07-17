"""
Basic tests to verify the testing setup.
"""

import pytest

from photo_organizer import __version__


def test_version():
    """Test that the version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)