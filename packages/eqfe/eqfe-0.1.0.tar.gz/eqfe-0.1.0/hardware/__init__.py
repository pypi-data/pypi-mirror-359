"""
Hardware interfaces for Environmental Quantum Field Effects experiments.

This package provides unified interfaces for quantum measurement hardware,
environmental field control, and data acquisition systems.
"""

__version__ = "0.1.0"
__author__ = "EQFE Research Team"

from .hardware_manager import HardwareManager, ExperimentConfig, ExperimentState
from .interfaces import (
    QuantumSensorInterface,
    FieldGeneratorInterface,
    DataAcquisitionInterface
)
from .drivers import (
    OscilloscopeDriver,
    SignalGeneratorDriver,
    TemperatureControlDriver
)
from .calibration import SensorCalibration, FieldCalibration

__all__ = [
    "HardwareManager",
    "ExperimentConfig", 
    "ExperimentState",
    "QuantumSensorInterface",
    "FieldGeneratorInterface",
    "DataAcquisitionInterface",
    "OscilloscopeDriver",
    "SignalGeneratorDriver", 
    "TemperatureControlDriver",
    "SensorCalibration",
    "FieldCalibration"
]
