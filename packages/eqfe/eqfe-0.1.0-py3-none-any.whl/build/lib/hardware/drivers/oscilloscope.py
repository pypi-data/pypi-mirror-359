"""
Oscilloscope driver for EQFE experiments.

Provides SCPI/VISA interface for digital oscilloscopes
supporting high-speed quantum measurement applications.
"""

import numpy as np
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class OscilloscopeDriver(ABC):
    """Abstract base class for oscilloscope drivers."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        """
        Initialize oscilloscope driver.
        
        Args:
            device_address: VISA address or IP address
            config: Device configuration parameters
        """
        self.device_address = device_address
        self.config = config
        self.is_connected = False
        self.logger = logging.getLogger(f"EQFE.drivers.oscilloscope")
        
        # Oscilloscope parameters
        self.num_channels = config.get('num_channels', 4)
        self.max_sample_rate = config.get('max_sample_rate', 5e9)
        self.memory_depth = config.get('memory_depth', 1e6)
        self.bandwidth = config.get('bandwidth', 1e9)
        
        # Current settings
        self.timebase = 1e-6  # seconds per division
        self.sample_rate = 1e9  # samples per second
        self.record_length = 10000
        self.trigger_level = 0.0
        self.trigger_source = "CH1"
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to oscilloscope."""
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from oscilloscope."""
        pass
        
    @abstractmethod
    def configure_channel(self, channel: int, voltage_range: float, 
                         coupling: str = "DC", impedance: int = 50) -> bool:
        """Configure oscilloscope channel."""
        pass
        
    @abstractmethod
    def set_timebase(self, timebase: float) -> bool:
        """Set horizontal timebase."""
        pass
        
    @abstractmethod
    def set_trigger(self, source: str, level: float, 
                   slope: str = "RISING") -> bool:
        """Configure trigger settings."""
        pass
        
    @abstractmethod
    def acquire_waveform(self, channels: List[int]) -> Dict[str, np.ndarray]:
        """Acquire waveform data from specified channels."""
        pass
        
    @abstractmethod
    def get_measurement(self, channel: int, 
                       measurement_type: str) -> float:
        """Get automated measurement."""
        pass


class KeysightOscilloscopeDriver(OscilloscopeDriver):
    """Driver for Keysight/Agilent oscilloscopes using SCPI commands."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        super().__init__(device_address, config)
        self.instrument = None
        
    def connect(self) -> bool:
        """Connect to Keysight oscilloscope via VISA."""
        try:
            import pyvisa
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.device_address)
            
            # Configure communication
            self.instrument.timeout = 10000  # 10 second timeout
            self.instrument.write_termination = '\n'
            self.instrument.read_termination = '\n'
            
            # Test connection
            idn = self.instrument.query("*IDN?")
            self.logger.info(f"Connected to: {idn.strip()}")
            
            # Reset to known state
            self.instrument.write("*RST")
            self.instrument.write("*CLS")
            time.sleep(1)
            
            self.is_connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to oscilloscope: {e}")
            return False
            
    def disconnect(self) -> bool:
        """Disconnect from oscilloscope."""
        try:
            if self.instrument:
                self.instrument.close()
                self.instrument = None
            self.is_connected = False
            self.logger.info("Disconnected from oscilloscope")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {e}")
            return False
            
    def configure_channel(self, channel: int, voltage_range: float,
                         coupling: str = "DC", impedance: int = 50) -> bool:
        """Configure oscilloscope channel."""
        try:
            if not self.is_connected:
                raise RuntimeError("Oscilloscope not connected")
                
            # Enable channel
            self.instrument.write(f":CHAN{channel}:DISP ON")
            
            # Set voltage range
            self.instrument.write(f":CHAN{channel}:RANG {voltage_range}")
            
            # Set coupling
            self.instrument.write(f":CHAN{channel}:COUP {coupling}")
            
            # Set impedance
            if impedance == 50:
                self.instrument.write(f":CHAN{channel}:IMP FIFT")
            else:
                self.instrument.write(f":CHAN{channel}:IMP ONEM")
                
            self.logger.info(f"Configured CH{channel}: {voltage_range}V, {coupling}, {impedance}Ω")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure channel {channel}: {e}")
            return False
            
    def set_timebase(self, timebase: float) -> bool:
        """Set horizontal timebase (seconds per division)."""
        try:
            if not self.is_connected:
                raise RuntimeError("Oscilloscope not connected")
                
            self.instrument.write(f":TIM:SCAL {timebase}")
            self.timebase = timebase
            
            # Update sample rate based on timebase
            self.sample_rate = min(self.max_sample_rate, 10 / timebase)
            self.instrument.write(f":ACQ:SRAT {self.sample_rate}")
            
            self.logger.info(f"Set timebase: {timebase:.2e} s/div, "
                           f"sample rate: {self.sample_rate:.2e} Sa/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set timebase: {e}")
            return False
            
    def set_trigger(self, source: str, level: float, 
                   slope: str = "RISING") -> bool:
        """Configure trigger settings."""
        try:
            if not self.is_connected:
                raise RuntimeError("Oscilloscope not connected")
                
            # Set trigger source
            self.instrument.write(f":TRIG:SOUR {source}")
            
            # Set trigger level
            self.instrument.write(f":TRIG:LEV {source},{level}")
            
            # Set trigger slope
            slope_cmd = "POS" if slope.upper() == "RISING" else "NEG"
            self.instrument.write(f":TRIG:SLOP {slope_cmd}")
            
            self.trigger_source = source
            self.trigger_level = level
            
            self.logger.info(f"Set trigger: {source} at {level}V, {slope}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set trigger: {e}")
            return False
            
    def acquire_waveform(self, channels: List[int]) -> Dict[str, np.ndarray]:
        """Acquire waveform data from specified channels."""
        try:
            if not self.is_connected:
                raise RuntimeError("Oscilloscope not connected")
                
            waveforms = {}
            
            # Set single trigger mode
            self.instrument.write(":SING")
            
            # Wait for trigger
            timeout = 10  # seconds
            start_time = time.time()
            while True:
                status = self.instrument.query(":OPER:COND?")
                if int(status) & 8:  # Trigger bit
                    break
                if time.time() - start_time > timeout:
                    raise TimeoutError("Trigger timeout")
                time.sleep(0.01)
                
            # Acquire data from each channel
            for channel in channels:
                # Select channel as data source
                self.instrument.write(f":WAV:SOUR CHAN{channel}")
                
                # Set data format
                self.instrument.write(":WAV:FORM REAL")
                self.instrument.write(":WAV:MODE RAW")
                
                # Get waveform preamble
                preamble = self.instrument.query(":WAV:PRE?")
                preamble_parts = preamble.split(',')
                
                # Extract scaling information
                xinc = float(preamble_parts[4])  # X increment
                xorig = float(preamble_parts[5])  # X origin
                yinc = float(preamble_parts[7])  # Y increment
                yorig = float(preamble_parts[8])  # Y origin
                yref = float(preamble_parts[9])  # Y reference
                
                # Get raw data
                raw_data = self.instrument.query_binary_values(
                    ":WAV:DATA?", datatype='f', is_big_endian=True
                )
                
                # Convert to numpy array and apply scaling
                data_array = np.array(raw_data)
                voltage = (data_array - yref) * yinc + yorig
                
                # Create time array
                time_array = np.arange(len(voltage)) * xinc + xorig
                
                waveforms[f"CH{channel}"] = {
                    'time': time_array,
                    'voltage': voltage,
                    'sample_rate': 1.0 / xinc,
                    'record_length': len(voltage)
                }
                
            self.logger.info(f"Acquired waveforms from channels: {channels}")
            return waveforms
            
        except Exception as e:
            self.logger.error(f"Failed to acquire waveform: {e}")
            return {}
            
    def get_measurement(self, channel: int, measurement_type: str) -> float:
        """Get automated measurement from channel."""
        try:
            if not self.is_connected:
                raise RuntimeError("Oscilloscope not connected")
                
            # Set measurement source
            self.instrument.write(f":MEAS:SOUR CHAN{channel}")
            
            # Get measurement based on type
            measurement_map = {
                'frequency': ':MEAS:FREQ?',
                'period': ':MEAS:PER?',
                'amplitude': ':MEAS:VAMP?',
                'peak_to_peak': ':MEAS:VPP?',
                'rms': ':MEAS:VRMS?',
                'average': ':MEAS:VAV?',
                'maximum': ':MEAS:VMAX?',
                'minimum': ':MEAS:VMIN?',
                'rise_time': ':MEAS:RIS?',
                'fall_time': ':MEAS:FALL?'
            }
            
            if measurement_type.lower() not in measurement_map:
                raise ValueError(f"Unknown measurement type: {measurement_type}")
                
            command = measurement_map[measurement_type.lower()]
            result = float(self.instrument.query(command))
            
            self.logger.debug(f"CH{channel} {measurement_type}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get measurement: {e}")
            return float('nan')
            
    def get_status(self) -> Dict[str, Any]:
        """Get oscilloscope status information."""
        try:
            if not self.is_connected:
                return {'connected': False}
                
            status = {
                'connected': True,
                'timebase': self.timebase,
                'sample_rate': self.sample_rate,
                'trigger_source': self.trigger_source,
                'trigger_level': self.trigger_level,
                'acquisition_state': self.instrument.query(":RUN?").strip(),
                'trigger_status': self.instrument.query(":TRIG:STAT?").strip()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {'connected': False, 'error': str(e)}
