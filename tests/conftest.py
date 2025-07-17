"""
Pytest configuration file for the Photo Organizer application.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Define fixtures here if needed