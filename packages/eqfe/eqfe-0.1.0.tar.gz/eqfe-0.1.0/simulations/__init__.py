"""
Simulations Package

Core simulation modules for environmental quantum field effects.
"""

from .core.field_simulator import EnvironmentalFieldSimulator
from .core.quantum_correlations import CHSHExperimentSimulator

__all__ = ["EnvironmentalFieldSimulator", "CHSHExperimentSimulator"]
