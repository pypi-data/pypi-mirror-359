"""
Signal generator driver for EQFE experiments.

Provides SCPI/VISA interface for signal generators
supporting precise frequency and amplitude control.
"""

import numpy as np
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class SignalGeneratorDriver(ABC):
    """Abstract base class for signal generator drivers."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        """
        Initialize signal generator driver.
        
        Args:
            device_address: VISA address or IP address
            config: Device configuration parameters
        """
        self.device_address = device_address
        self.config = config
        self.is_connected = False
        self.logger = logging.getLogger("EQFE.drivers.signal_generator")
        
        # Signal generator parameters
        self.frequency_range = config.get('frequency_range', (1e3, 6e9))
        self.amplitude_range = config.get('amplitude_range', (-20, 20))  # dBm
        self.num_channels = config.get('num_channels', 2)
        
        # Current settings
        self.channels = {}
        for i in range(1, self.num_channels + 1):
            self.channels[i] = {
                'frequency': 1e6,  # 1 MHz default
                'amplitude': -10,  # -10 dBm default
                'phase': 0.0,  # degrees
                'waveform': 'SIN',
                'enabled': False
            }
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to signal generator."""
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from signal generator."""
        pass
        
    @abstractmethod
    def set_frequency(self, channel: int, frequency: float) -> bool:
        """Set output frequency for specified channel."""
        pass
        
    @abstractmethod
    def set_amplitude(self, channel: int, amplitude: float) -> bool:
        """Set output amplitude for specified channel."""
        pass
        
    @abstractmethod
    def set_phase(self, channel: int, phase: float) -> bool:
        """Set output phase for specified channel."""
        pass
        
    @abstractmethod
    def set_waveform(self, channel: int, waveform: str) -> bool:
        """Set waveform type for specified channel."""
        pass
        
    @abstractmethod
    def enable_output(self, channel: int, enable: bool = True) -> bool:
        """Enable or disable channel output."""
        pass
        
    @abstractmethod
    def sync_channels(self, channels: List[int]) -> bool:
        """Synchronize multiple channels."""
        pass


class KeysightSignalGeneratorDriver(SignalGeneratorDriver):
    """Driver for Keysight signal generators using SCPI commands."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        super().__init__(device_address, config)
        self.instrument = None
        
    def connect(self) -> bool:
        """Connect to Keysight signal generator via VISA."""
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
            self.logger.error(f"Failed to connect to signal generator: {e}")
            return False
            
    def disconnect(self) -> bool:
        """Disconnect from signal generator."""
        try:
            # Turn off all outputs before disconnecting
            for channel in range(1, self.num_channels + 1):
                self.enable_output(channel, False)
                
            if self.instrument:
                self.instrument.close()
                self.instrument = None
            self.is_connected = False
            self.logger.info("Disconnected from signal generator")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {e}")
            return False
            
    def set_frequency(self, channel: int, frequency: float) -> bool:
        """Set output frequency for specified channel."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            if not (self.frequency_range[0] <= frequency <= self.frequency_range[1]):
                raise ValueError(f"Frequency {frequency} outside range {self.frequency_range}")
                
            self.instrument.write(f":SOUR{channel}:FREQ {frequency}")
            self.channels[channel]['frequency'] = frequency
            
            self.logger.info(f"Set CH{channel} frequency: {frequency:.2e} Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set frequency: {e}")
            return False
            
    def set_amplitude(self, channel: int, amplitude: float) -> bool:
        """Set output amplitude for specified channel (in dBm)."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            if not (self.amplitude_range[0] <= amplitude <= self.amplitude_range[1]):
                raise ValueError(f"Amplitude {amplitude} outside range {self.amplitude_range}")
                
            self.instrument.write(f":SOUR{channel}:POW {amplitude}")
            self.channels[channel]['amplitude'] = amplitude
            
            self.logger.info(f"Set CH{channel} amplitude: {amplitude} dBm")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set amplitude: {e}")
            return False
            
    def set_phase(self, channel: int, phase: float) -> bool:
        """Set output phase for specified channel (in degrees)."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            # Normalize phase to 0-360 degrees
            phase = phase % 360
            
            self.instrument.write(f":SOUR{channel}:PHAS {phase}")
            self.channels[channel]['phase'] = phase
            
            self.logger.info(f"Set CH{channel} phase: {phase} degrees")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set phase: {e}")
            return False
            
    def set_waveform(self, channel: int, waveform: str) -> bool:
        """Set waveform type for specified channel."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            # Map waveform names to SCPI commands
            waveform_map = {
                'SIN': 'SIN',
                'SINE': 'SIN',
                'SQUARE': 'SQU',
                'SQU': 'SQU',
                'TRIANGLE': 'TRI',
                'TRI': 'TRI',
                'RAMP': 'RAMP',
                'NOISE': 'NOIS',
                'DC': 'DC'
            }
            
            if waveform.upper() not in waveform_map:
                raise ValueError(f"Unknown waveform type: {waveform}")
                
            scpi_waveform = waveform_map[waveform.upper()]
            self.instrument.write(f":SOUR{channel}:FUNC {scpi_waveform}")
            self.channels[channel]['waveform'] = waveform.upper()
            
            self.logger.info(f"Set CH{channel} waveform: {waveform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set waveform: {e}")
            return False
            
    def enable_output(self, channel: int, enable: bool = True) -> bool:
        """Enable or disable channel output."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            state = "ON" if enable else "OFF"
            self.instrument.write(f":OUTP{channel} {state}")
            self.channels[channel]['enabled'] = enable
            
            self.logger.info(f"CH{channel} output: {state}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set output state: {e}")
            return False
            
    def sync_channels(self, channels: List[int]) -> bool:
        """Synchronize multiple channels."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            # Enable phase synchronization
            for channel in channels:
                self.instrument.write(f":SOUR{channel}:PHAS:SYNC")
                
            self.logger.info(f"Synchronized channels: {channels}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync channels: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get signal generator status information."""
        try:
            if not self.is_connected:
                return {'connected': False}
                
            status = {
                'connected': True,
                'channels': self.channels.copy(),
                'frequency_range': self.frequency_range,
                'amplitude_range': self.amplitude_range
            }
            
            # Get actual instrument settings
            for channel in range(1, self.num_channels + 1):
                try:
                    freq = float(self.instrument.query(f":SOUR{channel}:FREQ?"))
                    amp = float(self.instrument.query(f":SOUR{channel}:POW?"))
                    enabled = self.instrument.query(f":OUTP{channel}?").strip() == "1"
                    
                    status['channels'][channel].update({
                        'actual_frequency': freq,
                        'actual_amplitude': amp,
                        'actual_enabled': enabled
                    })
                except:
                    pass  # Skip if channel not available
                    
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {'connected': False, 'error': str(e)}
            
    def generate_sweep(self, channel: int, start_freq: float, 
                      stop_freq: float, sweep_time: float) -> bool:
        """Generate frequency sweep on specified channel."""
        try:
            if not self.is_connected:
                raise RuntimeError("Signal generator not connected")
                
            # Configure sweep parameters
            self.instrument.write(f":SOUR{channel}:FREQ:STAR {start_freq}")
            self.instrument.write(f":SOUR{channel}:FREQ:STOP {stop_freq}")
            self.instrument.write(f":SOUR{channel}:SWE:TIME {sweep_time}")
            self.instrument.write(f":SOUR{channel}:SWE:STAT ON")
            
            self.logger.info(f"Started sweep CH{channel}: {start_freq:.2e} to "
                           f"{stop_freq:.2e} Hz over {sweep_time} s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate sweep: {e}")
            return False
