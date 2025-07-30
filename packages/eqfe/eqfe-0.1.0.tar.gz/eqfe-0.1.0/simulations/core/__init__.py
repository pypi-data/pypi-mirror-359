"""
Core simulation modules for environmental quantum field effects.
"""

from .field_simulator import EnvironmentalFieldSimulator
from .quantum_correlations import CHSHExperimentSimulator

__all__ = ["EnvironmentalFieldSimulator", "CHSHExperimentSimulator"]
