"""
Unified Hardware Manager for EQFE experiments.

Provides a high-level abstraction layer for coordinating
multiple hardware devices in quantum field experiments.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

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


class ExperimentState(Enum):
    """Enumeration of experiment states."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    CALIBRATING = "calibrating"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ExperimentConfig:
    """Configuration for EQFE experiments."""
    # Measurement parameters
    measurement_duration: float = 60.0  # seconds
    sample_rate: float = 1e6  # Hz
    
    # Environmental parameters
    target_temperature: float = 300.0  # Kelvin
    field_frequency: float = 1e6  # Hz
    field_amplitude: float = 1e-6  # Tesla
    
    # Data acquisition
    channels_to_record: List[int] = field(default_factory=lambda: [1, 2])
    trigger_level: float = 0.1  # Volts
    
    # Calibration settings
    auto_calibrate: bool = True
    calibration_interval: float = 3600.0  # seconds


class HardwareManager:
    """Unified hardware management system for EQFE experiments."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize hardware manager.
        
        Args:
            config: Hardware configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("EQFE.hardware.manager")
        
        # Initialize device interfaces
        self.quantum_sensors: Dict[str, QuantumSensorInterface] = {}
        self.field_generators: Dict[str, FieldGeneratorInterface] = {}
        self.data_acquisition: Dict[str, DataAcquisitionInterface] = {}
        self.drivers: Dict[str, Any] = {}
        
        # Calibration systems
        self.sensor_calibration = SensorCalibration(
            config.get('calibration', {})
        )
        self.field_calibration = FieldCalibration(
            config.get('field_calibration', {})
        )
        
        # Experiment state
        self.state = ExperimentState.IDLE
        self.current_experiment = None
        self.last_calibration_time = 0.0
        
        # Data storage
        self.measurement_data = {}
        self.experiment_log = []
        
    def initialize_hardware(self) -> bool:
        """Initialize and connect to all configured hardware devices."""
        try:
            self.logger.info("Starting hardware initialization")
            self.state = ExperimentState.INITIALIZING
            
            # Initialize quantum sensors
            sensor_configs = self.config.get('quantum_sensors', {})
            for sensor_id, sensor_config in sensor_configs.items():
                success = self._initialize_sensor(sensor_id, sensor_config)
                if not success:
                    self.logger.error(f"Failed to initialize sensor {sensor_id}")
                    return False
                    
            # Initialize field generators
            field_configs = self.config.get('field_generators', {})
            for field_id, field_config in field_configs.items():
                success = self._initialize_field_generator(field_id, field_config)
                if not success:
                    self.logger.error(f"Failed to initialize field generator {field_id}")
                    return False
                    
            # Initialize data acquisition systems
            daq_configs = self.config.get('data_acquisition', {})
            for daq_id, daq_config in daq_configs.items():
                success = self._initialize_daq(daq_id, daq_config)
                if not success:
                    self.logger.error(f"Failed to initialize DAQ {daq_id}")
                    return False
                    
            # Initialize device drivers
            driver_configs = self.config.get('drivers', {})
            for driver_id, driver_config in driver_configs.items():
                success = self._initialize_driver(driver_id, driver_config)
                if not success:
                    self.logger.error(f"Failed to initialize driver {driver_id}")
                    return False
                    
            self.logger.info("Hardware initialization complete")
            self.state = ExperimentState.IDLE
            return True
            
        except Exception as e:
            self.logger.error(f"Hardware initialization failed: {e}")
            self.state = ExperimentState.ERROR
            return False
            
    def run_experiment(self, experiment_config: ExperimentConfig) -> bool:
        """
        Run a complete EQFE experiment.
        
        Args:
            experiment_config: Experiment configuration
            
        Returns:
            True if experiment completed successfully
        """
        try:
            self.logger.info("Starting EQFE experiment")
            self.state = ExperimentState.RUNNING
            self.current_experiment = experiment_config
            
            # Pre-experiment calibration
            if experiment_config.auto_calibrate:
                if not self._perform_calibration():
                    self.logger.error("Pre-experiment calibration failed")
                    return False
                    
            # Configure environmental conditions
            if not self._setup_environment(experiment_config):
                self.logger.error("Environment setup failed")
                return False
                
            # Configure data acquisition
            if not self._setup_data_acquisition(experiment_config):
                self.logger.error("Data acquisition setup failed")
                return False
                
            # Start field generation
            if not self._start_field_generation(experiment_config):
                self.logger.error("Field generation start failed")
                return False
                
            # Run measurement sequence
            if not self._run_measurement_sequence(experiment_config):
                self.logger.error("Measurement sequence failed")
                return False
                
            # Stop field generation
            self._stop_field_generation()
            
            # Process and store data
            if not self._process_measurement_data():
                self.logger.error("Data processing failed")
                return False
                
            self.logger.info("EQFE experiment completed successfully")
            self.state = ExperimentState.IDLE
            return True
            
        except Exception as e:
            self.logger.error(f"Experiment failed: {e}")
            self.state = ExperimentState.ERROR
            self._emergency_stop()
            return False
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = {
                'state': self.state.value,
                'timestamp': time.time(),
                'quantum_sensors': {},
                'field_generators': {},
                'data_acquisition': {},
                'drivers': {},
                'calibration_status': {
                    'last_calibration': self.last_calibration_time,
                    'calibration_valid': time.time() - self.last_calibration_time < 3600,
                },
                'system_health': 'healthy'
            }
            
            # Get sensor status
            for sensor_id, sensor in self.quantum_sensors.items():
                if hasattr(sensor, 'get_status'):
                    status['quantum_sensors'][sensor_id] = sensor.get_status()
                    
            # Get field generator status
            for field_id, field in self.field_generators.items():
                if hasattr(field, 'get_field_status'):
                    status['field_generators'][field_id] = field.get_field_status()
                    
            # Get DAQ status
            for daq_id, daq in self.data_acquisition.items():
                if hasattr(daq, 'get_acquisition_status'):
                    status['data_acquisition'][daq_id] = daq.get_acquisition_status()
                    
            # Get driver status
            for driver_id, driver in self.drivers.items():
                if hasattr(driver, 'get_status'):
                    status['drivers'][driver_id] = driver.get_status()
                    
            # Check overall system health
            unhealthy_devices = []
            for category in ['quantum_sensors', 'field_generators', 'data_acquisition', 'drivers']:
                for device_id, device_status in status[category].items():
                    if not device_status.get('connected', False):
                        unhealthy_devices.append(f"{category}.{device_id}")
                        
            if unhealthy_devices:
                status['system_health'] = 'degraded'
                status['unhealthy_devices'] = unhealthy_devices
                
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                'state': ExperimentState.ERROR.value,
                'timestamp': time.time(),
                'error': str(e)
            }
            
    def shutdown_hardware(self) -> bool:
        """Safely shutdown all hardware devices."""
        try:
            self.logger.info("Starting hardware shutdown")
            self.state = ExperimentState.STOPPING
            
            # Stop any running experiments
            if self.state == ExperimentState.RUNNING:
                self._emergency_stop()
                
            # Disconnect all devices
            for sensor in self.quantum_sensors.values():
                if hasattr(sensor, 'disconnect'):
                    sensor.disconnect()
                    
            for field in self.field_generators.values():
                if hasattr(field, 'disconnect'):
                    field.disconnect()
                    
            for daq in self.data_acquisition.values():
                if hasattr(daq, 'disconnect'):
                    daq.disconnect()
                    
            for driver in self.drivers.values():
                if hasattr(driver, 'disconnect'):
                    driver.disconnect()
                    
            self.logger.info("Hardware shutdown complete")
            self.state = ExperimentState.IDLE
            return True
            
        except Exception as e:
            self.logger.error(f"Hardware shutdown failed: {e}")
            return False
            
    def _initialize_sensor(self, sensor_id: str, config: Dict[str, Any]) -> bool:
        """Initialize a quantum sensor."""
        try:
            # Create sensor based on type
            sensor_type = config.get('type', 'generic')
            
            if sensor_type == 'single_photon_detector':
                from .interfaces.quantum_sensors import SinglePhotonDetector
                sensor = SinglePhotonDetector(sensor_id, config)
            elif sensor_type == 'interferometer':
                from .interfaces.quantum_sensors import InterferometerInterface
                sensor = InterferometerInterface(sensor_id, config)
            else:
                self.logger.warning(f"Unknown sensor type: {sensor_type}")
                return False
                
            # Connect to sensor
            if sensor.connect():
                self.quantum_sensors[sensor_id] = sensor
                self.logger.info(f"Initialized sensor: {sensor_id}")
                return True
            else:
                self.logger.error(f"Failed to connect to sensor: {sensor_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Sensor initialization error: {e}")
            return False
            
    def _initialize_field_generator(self, field_id: str, config: Dict[str, Any]) -> bool:
        """Initialize a field generator."""
        try:
            # Create field generator based on type
            field_type = config.get('type', 'generic')
            
            if field_type == 'electromagnetic':
                from .interfaces.field_generators import ElectromagneticFieldGenerator
                field = ElectromagneticFieldGenerator(field_id, config)
            elif field_type == 'temperature':
                from .interfaces.field_generators import TemperatureController
                field = TemperatureController(field_id, config)
            else:
                self.logger.warning(f"Unknown field generator type: {field_type}")
                return False
                
            # Connect to field generator
            if field.connect():
                self.field_generators[field_id] = field
                self.logger.info(f"Initialized field generator: {field_id}")
                return True
            else:
                self.logger.error(f"Failed to connect to field generator: {field_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Field generator initialization error: {e}")
            return False
            
    def _initialize_daq(self, daq_id: str, config: Dict[str, Any]) -> bool:
        """Initialize a data acquisition system."""
        try:
            # Create DAQ based on type
            daq_type = config.get('type', 'generic')
            
            if daq_type == 'high_speed_digitizer':
                from .interfaces.data_acquisition import HighSpeedDigitizer
                daq = HighSpeedDigitizer(daq_id, config)
            elif daq_type == 'oscilloscope':
                from .interfaces.data_acquisition import OscilloscopeInterface
                daq = OscilloscopeInterface(daq_id, config)
            else:
                self.logger.warning(f"Unknown DAQ type: {daq_type}")
                return False
                
            # Connect to DAQ
            if daq.connect():
                self.data_acquisition[daq_id] = daq
                self.logger.info(f"Initialized DAQ: {daq_id}")
                return True
            else:
                self.logger.error(f"Failed to connect to DAQ: {daq_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"DAQ initialization error: {e}")
            return False
            
    def _initialize_driver(self, driver_id: str, config: Dict[str, Any]) -> bool:
        """Initialize a device driver."""
        try:
            # Create driver based on type
            driver_type = config.get('type', 'generic')
            device_address = config.get('address', '')
            
            if driver_type == 'oscilloscope':
                from .drivers.oscilloscope import KeysightOscilloscopeDriver
                driver = KeysightOscilloscopeDriver(device_address, config)
            elif driver_type == 'signal_generator':
                from .drivers.signal_generator import KeysightSignalGeneratorDriver
                driver = KeysightSignalGeneratorDriver(device_address, config)
            elif driver_type == 'temperature_controller':
                from .drivers.temperature_control import LakeShoreTemperatureDriver
                driver = LakeShoreTemperatureDriver(device_address, config)
            else:
                self.logger.warning(f"Unknown driver type: {driver_type}")
                return False
                
            # Connect to device
            if driver.connect():
                self.drivers[driver_id] = driver
                self.logger.info(f"Initialized driver: {driver_id}")
                return True
            else:
                self.logger.error(f"Failed to connect to driver: {driver_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Driver initialization error: {e}")
            return False
            
    def _perform_calibration(self) -> bool:
        """Perform system calibration."""
        try:
            self.logger.info("Starting system calibration")
            self.state = ExperimentState.CALIBRATING
            
            # Calibrate quantum sensors
            for sensor_id, sensor in self.quantum_sensors.items():
                if hasattr(sensor, 'calibrate'):
                    if not sensor.calibrate():
                        self.logger.error(f"Sensor calibration failed: {sensor_id}")
                        return False
                        
            # Calibrate field generators
            for field_id, field in self.field_generators.items():
                # Field calibration would be implemented here
                pass
                
            self.last_calibration_time = time.time()
            self.logger.info("System calibration complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Calibration failed: {e}")
            return False
            
    def _setup_environment(self, config: ExperimentConfig) -> bool:
        """Setup environmental conditions."""
        try:
            # Set temperature
            for field_id, field in self.field_generators.items():
                if hasattr(field, 'set_field_parameters'):
                    parameters = {'temperature': config.target_temperature}
                    if not field.set_field_parameters(parameters):
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
            return False
            
    def _setup_data_acquisition(self, config: ExperimentConfig) -> bool:
        """Setup data acquisition systems."""
        try:
            for daq_id, daq in self.data_acquisition.items():
                if hasattr(daq, 'configure_channels'):
                    channel_config = {}
                    for ch in config.channels_to_record:
                        channel_config[str(ch)] = {
                            'enabled': True,
                            'voltage_range': 1.0
                        }
                    if not daq.configure_channels(channel_config):
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"DAQ setup failed: {e}")
            return False
            
    def _start_field_generation(self, config: ExperimentConfig) -> bool:
        """Start field generation."""
        try:
            for field_id, field in self.field_generators.items():
                if hasattr(field, 'start_field_generation'):
                    if not field.start_field_generation():
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Field generation start failed: {e}")
            return False
            
    def _stop_field_generation(self) -> bool:
        """Stop field generation."""
        try:
            for field_id, field in self.field_generators.items():
                if hasattr(field, 'stop_field_generation'):
                    field.stop_field_generation()
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Field generation stop failed: {e}")
            return False
            
    def _run_measurement_sequence(self, config: ExperimentConfig) -> bool:
        """Run the main measurement sequence."""
        try:
            # Start data acquisition
            for daq_id, daq in self.data_acquisition.items():
                if hasattr(daq, 'start_acquisition'):
                    if not daq.start_acquisition():
                        return False
                        
            # Start sensor measurements
            for sensor_id, sensor in self.quantum_sensors.items():
                if hasattr(sensor, 'measure_correlations'):
                    # Non-blocking measurement start
                    pass
                    
            # Wait for measurement duration
            time.sleep(config.measurement_duration)
            
            # Stop data acquisition
            for daq_id, daq in self.data_acquisition.items():
                if hasattr(daq, 'stop_acquisition'):
                    daq.stop_acquisition()
                    
            # Collect data
            for daq_id, daq in self.data_acquisition.items():
                if hasattr(daq, 'get_data'):
                    self.measurement_data[daq_id] = daq.get_data()
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Measurement sequence failed: {e}")
            return False
            
    def _process_measurement_data(self) -> bool:
        """Process and store measurement data."""
        try:
            # Basic data processing
            self.logger.info("Processing measurement data")
            
            # TODO: Implement data processing algorithms
            # - Correlation analysis
            # - Noise filtering
            # - Statistical analysis
            
            return True
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            return False
            
    def _emergency_stop(self) -> None:
        """Emergency stop all systems."""
        try:
            self.logger.warning("Executing emergency stop")
            
            # Stop field generation immediately
            self._stop_field_generation()
            
            # Stop data acquisition
            for daq in self.data_acquisition.values():
                if hasattr(daq, 'stop_acquisition'):
                    daq.stop_acquisition()
                    
            self.state = ExperimentState.ERROR
            
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
