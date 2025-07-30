---
layout: default
title: API Reference
permalink: /api-reference/
---

## Core Components

### Hardware Management

#### HardwareManager

The central class for managing all hardware components in EQFE experiments.

```python
from hardware import HardwareManager, ExperimentConfig

# Initialize hardware
manager = HardwareManager(config)
manager.initialize_hardware()

# Run experiment
experiment = ExperimentConfig(
    measurement_duration=60.0,
    target_temperature=300.0,
    field_frequency=1e6
)
success = manager.run_experiment(experiment)
```

### Hardware Interfaces

#### QuantumSensorInterface

Abstract base class for quantum sensor interfaces.

```python
class QuantumSensorInterface(ABC):
    def connect(self) -> bool:
        """Establish connection to the quantum sensor."""
        
    def disconnect(self) -> bool:
        """Disconnect from the quantum sensor."""
        
    def calibrate(self) -> bool:
        """Perform sensor calibration procedure."""
        
    def measure_correlations(self, duration: float) -> Dict[str, np.ndarray]:
        """Measure quantum correlations."""
        
    def get_status(self) -> Dict[str, Any]:
        """Get current sensor status and health metrics."""
```

#### FieldGeneratorInterface

Abstract base class for environmental field generators.

```python
class FieldGeneratorInterface(ABC):
    def connect(self) -> bool:
        """Establish connection to the field generator."""
        
    def disconnect(self) -> bool:
        """Disconnect from the field generator."""
        
    def set_field_parameters(self, parameters: Dict[str, float]) -> bool:
        """Set field generation parameters."""
        
    def start_field_generation(self) -> bool:
        """Start environmental field generation."""
        
    def stop_field_generation(self) -> bool:
        """Stop environmental field generation."""
        
    def get_field_status(self) -> Dict[str, Any]:
        """Get current field generation status."""
```

#### DataAcquisitionInterface

Abstract base class for data acquisition interfaces.

```python
class DataAcquisitionInterface(ABC):
    def connect(self) -> bool:
        """Establish connection to the DAQ system."""
        
    def disconnect(self) -> bool:
        """Disconnect from the DAQ system."""
        
    def configure_channels(self, channel_config: Dict[str, Any]) -> bool:
        """Configure acquisition channels."""
        
    def start_acquisition(self) -> bool:
        """Start data acquisition."""
        
    def stop_acquisition(self) -> bool:
        """Stop data acquisition."""
        
    def get_data(self) -> Dict[str, np.ndarray]:
        """Get acquired data."""
        
    def get_acquisition_status(self) -> Dict[str, Any]:
        """Get current acquisition status."""
```

### Device Drivers

#### OscilloscopeDriver

Driver for oscilloscope control and data acquisition.

```python
class OscilloscopeDriver(ABC):
    def connect(self) -> bool:
        """Connect to oscilloscope."""
        
    def disconnect(self) -> bool:
        """Disconnect from oscilloscope."""
        
    def set_trigger(self, channel: int, level: float, slope: str) -> bool:
        """Configure trigger settings."""
        
    def acquire_waveform(self, channels: List[int]) -> Dict[int, np.ndarray]:
        """Acquire waveform data from specified channels."""
```

#### SignalGeneratorDriver

Driver for signal generator control.

```python
class SignalGeneratorDriver(ABC):
    def connect(self) -> bool:
        """Connect to signal generator."""
        
    def disconnect(self) -> bool:
        """Disconnect from signal generator."""
        
    def set_frequency(self, channel: int, frequency: float) -> bool:
        """Set output frequency for specified channel."""
        
    def set_amplitude(self, channel: int, amplitude: float) -> bool:
        """Set output amplitude for specified channel."""
        
    def set_phase(self, channel: int, phase: float) -> bool:
        """Set output phase for specified channel."""
```

### Information Processing

#### QuantumInformationProcessor

Tools for quantum information analysis.

```python
from complex_systems.information_processing import QuantumInformationProcessor

processor = QuantumInformationProcessor()
result = processor.analyze_correlations(data)
```

#### ComplexityAnalyzer

Tools for analyzing computational complexity in quantum systems.

```python
from complex_systems.information_processing import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
complexity = analyzer.calculate_system_complexity(data)
```

## Calibration System

### SensorCalibration

Tools for calibrating quantum sensors and measurement devices.

```python
from hardware.calibration import SensorCalibration

calibrator = SensorCalibration(config)
result = calibrator.calibrate_photodetector(detector, reference_power)
```

### FieldCalibration

Tools for calibrating field generators and environmental controls.

```python
from hardware.calibration import FieldCalibration

calibrator = FieldCalibration(config)
result = calibrator.calibrate_field_strength(generator, probe)
```

## Data Analysis

### EQFEAnalyzer

Advanced analysis tools for EQFE experiments.

```python
from examples.advanced_analysis import EQFEAnalyzer

analyzer = EQFEAnalyzer()
results = analyzer.analyze_experiment_data(data)
```

## Usage Examples

### Basic Setup

```python
from hardware import HardwareManager
from hardware.interfaces import QuantumSensorInterface
from hardware.calibration import SensorCalibration

# Initialize hardware
config = {
    'quantum_sensors': {
        'id': 'spad_array_1',
        'type': 'SinglePhotonDetector',
        'settings': {...}
    },
    'field_generators': {
        'id': 'em_field_1',
        'type': 'ElectromagneticFieldGenerator',
        'settings': {...}
    }
}

manager = HardwareManager(config)
manager.initialize_hardware()

# Calibrate sensors
calibrator = SensorCalibration(config)
calibrator.calibrate_all_sensors()

# Run experiment
experiment = ExperimentConfig(
    measurement_duration=60.0,
    target_temperature=300.0,
    field_frequency=1e6
)

success = manager.run_experiment(experiment)
data = manager.get_experiment_data()

# Analyze results
analyzer = EQFEAnalyzer()
results = analyzer.analyze_experiment_data(data)
```

## Error Handling

All API methods include comprehensive error handling and return appropriate status codes or raise specific exceptions when errors occur. Error messages include detailed information about the cause of the error and potential solutions.

## Configuration

Configuration is handled through dictionary objects that specify hardware settings, experimental parameters, and analysis options. See the example configurations in the `examples/` directory for detailed examples.
