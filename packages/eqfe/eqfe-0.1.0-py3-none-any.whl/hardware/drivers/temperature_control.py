"""
Temperature control driver for EQFE experiments.

Provides interface for precision temperature controllers
supporting cryogenic and high-temperature applications.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any


class TemperatureControlDriver(ABC):
    """Abstract base class for temperature control drivers."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        """
        Initialize temperature control driver.
        
        Args:
            device_address: Serial port, VISA address, or IP address
            config: Device configuration parameters
        """
        self.device_address = device_address
        self.config = config
        self.is_connected = False
        self.logger = logging.getLogger("EQFE.drivers.temperature_control")
        
        # Temperature controller parameters
        self.temperature_range = config.get('temperature_range', (4.0, 400.0))  # Kelvin
        self.stability = config.get('stability', 0.01)  # Kelvin
        self.max_power = config.get('max_power', 100.0)  # Watts
        
        # Current settings
        self.setpoint = 300.0  # Kelvin
        self.current_temperature = 300.0
        self.heater_power = 0.0
        self.pid_parameters = {
            'kp': 1.0,  # Proportional gain
            'ki': 0.1,  # Integral gain
            'kd': 0.05  # Derivative gain
        }
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to temperature controller."""
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from temperature controller."""
        pass
        
    @abstractmethod
    def set_temperature(self, temperature: float) -> bool:
        """Set target temperature setpoint."""
        pass
        
    @abstractmethod
    def get_temperature(self) -> float:
        """Get current temperature reading."""
        pass
        
    @abstractmethod
    def set_pid_parameters(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID control parameters."""
        pass
        
    @abstractmethod
    def enable_control(self, enable: bool = True) -> bool:
        """Enable or disable temperature control."""
        pass
        
    @abstractmethod
    def get_heater_power(self) -> float:
        """Get current heater power output percentage."""
        pass


class LakeShoreTemperatureDriver(TemperatureControlDriver):
    """Driver for Lake Shore temperature controllers."""
    
    def __init__(self, device_address: str, config: Dict[str, Any]):
        super().__init__(device_address, config)
        self.instrument = None
        self.control_enabled = False
        
    def connect(self) -> bool:
        """Connect to Lake Shore temperature controller."""
        try:
            import pyvisa
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.device_address)
            
            # Configure communication
            self.instrument.timeout = 5000  # 5 second timeout
            self.instrument.write_termination = '\r\n'
            self.instrument.read_termination = '\r\n'
            
            # Test connection
            idn = self.instrument.query("*IDN?")
            self.logger.info(f"Connected to: {idn.strip()}")
            
            # Get current temperature
            self.current_temperature = self.get_temperature()
            
            self.is_connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to temperature controller: {e}")
            return False
            
    def disconnect(self) -> bool:
        """Disconnect from temperature controller."""
        try:
            # Disable control before disconnecting
            self.enable_control(False)
            
            if self.instrument:
                self.instrument.close()
                self.instrument = None
            self.is_connected = False
            self.logger.info("Disconnected from temperature controller")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {e}")
            return False
            
    def set_temperature(self, temperature: float) -> bool:
        """Set target temperature setpoint."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            if not (self.temperature_range[0] <= temperature <= self.temperature_range[1]):
                raise ValueError(f"Temperature {temperature} outside range {self.temperature_range}")
                
            # Set setpoint (using output 1 as default)
            self.instrument.write(f"SETP 1,{temperature}")
            self.setpoint = temperature
            
            self.logger.info(f"Set temperature setpoint: {temperature:.2f} K")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set temperature: {e}")
            return False
            
    def get_temperature(self) -> float:
        """Get current temperature reading."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Read temperature from input A (channel 1)
            temp_str = self.instrument.query("KRDG? A")
            temperature = float(temp_str.strip())
            
            self.current_temperature = temperature
            return temperature
            
        except Exception as e:
            self.logger.error(f"Failed to read temperature: {e}")
            return float('nan')
            
    def set_pid_parameters(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID control parameters."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Set PID parameters for output 1
            self.instrument.write(f"PID 1,{kp},{ki},{kd}")
            
            self.pid_parameters.update({
                'kp': kp,
                'ki': ki,
                'kd': kd
            })
            
            self.logger.info(f"Set PID parameters: P={kp}, I={ki}, D={kd}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set PID parameters: {e}")
            return False
            
    def enable_control(self, enable: bool = True) -> bool:
        """Enable or disable temperature control."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Set control mode (0=Off, 1=Closed Loop PID, 2=Zone, 3=Open Loop)
            mode = 1 if enable else 0
            self.instrument.write(f"CSET 1,A,1,{mode},0")
            
            self.control_enabled = enable
            
            status = "enabled" if enable else "disabled"
            self.logger.info(f"Temperature control {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set control state: {e}")
            return False
            
    def get_heater_power(self) -> float:
        """Get current heater power output percentage."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Read heater output percentage
            power_str = self.instrument.query("HTR? 1")
            power = float(power_str.strip())
            
            self.heater_power = power
            return power
            
        except Exception as e:
            self.logger.error(f"Failed to read heater power: {e}")
            return float('nan')
            
    def get_status(self) -> Dict[str, Any]:
        """Get temperature controller status information."""
        try:
            if not self.is_connected:
                return {'connected': False}
                
            current_temp = self.get_temperature()
            heater_power = self.get_heater_power()
            
            # Check if at setpoint
            at_setpoint = abs(current_temp - self.setpoint) < self.stability
            
            status = {
                'connected': True,
                'current_temperature': current_temp,
                'setpoint': self.setpoint,
                'heater_power': heater_power,
                'control_enabled': self.control_enabled,
                'at_setpoint': at_setpoint,
                'temperature_range': self.temperature_range,
                'stability': self.stability,
                'pid_parameters': self.pid_parameters.copy()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {'connected': False, 'error': str(e)}
            
    def start_temperature_ramp(self, target_temp: float, 
                              ramp_rate: float) -> bool:
        """Start temperature ramp to target at specified rate."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Enable ramping
            self.instrument.write(f"RAMP 1,1,{ramp_rate}")
            
            # Set target temperature
            self.set_temperature(target_temp)
            
            self.logger.info(f"Started ramp to {target_temp:.2f} K "
                           f"at {ramp_rate:.2f} K/min")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start temperature ramp: {e}")
            return False
            
    def stop_temperature_ramp(self) -> bool:
        """Stop temperature ramping."""
        try:
            if not self.is_connected:
                raise RuntimeError("Temperature controller not connected")
                
            # Disable ramping
            self.instrument.write("RAMP 1,0,0")
            
            self.logger.info("Stopped temperature ramp")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop temperature ramp: {e}")
            return False
            
    def wait_for_stable_temperature(self, timeout: float = 600) -> bool:
        """Wait for temperature to stabilize at setpoint."""
        try:
            self.logger.info(f"Waiting for temperature to stabilize at {self.setpoint:.2f} K")
            
            start_time = time.time()
            stable_count = 0
            required_stable_readings = 10  # Number of consecutive stable readings
            
            while time.time() - start_time < timeout:
                current_temp = self.get_temperature()
                
                if abs(current_temp - self.setpoint) < self.stability:
                    stable_count += 1
                    if stable_count >= required_stable_readings:
                        self.logger.info("Temperature stabilized")
                        return True
                else:
                    stable_count = 0
                    
                time.sleep(1)  # Check every second
                
            self.logger.warning("Temperature stabilization timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"Error waiting for stable temperature: {e}")
            return False
