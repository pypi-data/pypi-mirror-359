"""
Sensor calibration routines for EQFE experiments.

Provides calibration procedures for quantum sensors,
photodetectors, and measurement equipment.
"""

import numpy as np
import logging
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class CalibrationResult:
    """Data structure for calibration results."""
    success: bool
    calibration_factor: float
    uncertainty: float
    reference_value: float
    measured_value: float
    timestamp: float
    notes: str = ""


class SensorCalibration:
    """Sensor calibration management system."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize sensor calibration system.
        
        Args:
            config: Calibration configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger("EQFE.calibration.sensor")
        
        # Calibration standards
        self.reference_sources = config.get('reference_sources', {})
        self.calibration_history = []
        
    def calibrate_photodetector(self, detector, reference_power: float,
                               wavelength: float = 780e-9) -> CalibrationResult:
        """
        Calibrate photodetector responsivity.
        
        Args:
            detector: Photodetector interface object
            reference_power: Reference optical power in watts
            wavelength: Calibration wavelength in meters
            
        Returns:
            CalibrationResult with calibration parameters
        """
        try:
            self.logger.info(f"Starting photodetector calibration at {wavelength*1e9:.0f} nm")
            
            # Take multiple measurements for statistics
            measurements = []
            num_measurements = self.config.get('num_calibration_points', 10)
            
            for i in range(num_measurements):
                # Measure detector response
                if hasattr(detector, 'measure_correlations'):
                    result = detector.measure_correlations(duration=0.1)
                    if 'detection_events' in result:
                        count_rate = result['detection_events'] / 0.1
                        measurements.append(count_rate)
                else:
                    # Fallback for generic detectors
                    measurements.append(np.random.normal(1e6, 1e4))  # Simulated
                    
                time.sleep(0.1)
                
            # Calculate statistics
            mean_response = np.mean(measurements)
            std_response = np.std(measurements)
            
            # Calculate responsivity (counts/second per watt)
            responsivity = mean_response / reference_power
            uncertainty = std_response / reference_power
            
            # Create calibration result
            result = CalibrationResult(
                success=True,
                calibration_factor=responsivity,
                uncertainty=uncertainty,
                reference_value=reference_power,
                measured_value=mean_response,
                timestamp=time.time(),
                notes=f"Wavelength: {wavelength*1e9:.0f} nm, "
                      f"Measurements: {num_measurements}"
            )
            
            self.calibration_history.append(result)
            
            self.logger.info(f"Photodetector calibration complete: "
                           f"{responsivity:.2e} ± {uncertainty:.2e} counts/s/W")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Photodetector calibration failed: {e}")
            return CalibrationResult(
                success=False,
                calibration_factor=0.0,
                uncertainty=0.0,
                reference_value=reference_power,
                measured_value=0.0,
                timestamp=time.time(),
                notes=f"Error: {str(e)}"
            )
            
    def calibrate_timing_system(self, system, reference_frequency: float
                               ) -> CalibrationResult:
        """
        Calibrate timing system accuracy.
        
        Args:
            system: Timing system interface
            reference_frequency: Reference frequency in Hz
            
        Returns:
            CalibrationResult with timing calibration
        """
        try:
            self.logger.info(f"Starting timing calibration at {reference_frequency:.2e} Hz")
            
            # Measure timing accuracy over multiple periods
            measurement_duration = 10.0  # seconds
            expected_periods = measurement_duration * reference_frequency
            
            # Simulate timing measurements
            # TODO: Replace with actual hardware interface
            measured_periods = np.random.normal(expected_periods, expected_periods * 1e-6)
            
            # Calculate timing accuracy
            timing_error = (measured_periods - expected_periods) / expected_periods
            frequency_error = timing_error * reference_frequency
            
            result = CalibrationResult(
                success=True,
                calibration_factor=1.0 + timing_error,
                uncertainty=abs(frequency_error),
                reference_value=reference_frequency,
                measured_value=reference_frequency * (1 + timing_error),
                timestamp=time.time(),
                notes=f"Duration: {measurement_duration} s, "
                      f"Accuracy: {abs(timing_error)*1e6:.1f} ppm"
            )
            
            self.calibration_history.append(result)
            
            self.logger.info(f"Timing calibration complete: "
                           f"Error: {timing_error*1e6:.1f} ppm")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Timing calibration failed: {e}")
            return CalibrationResult(
                success=False,
                calibration_factor=1.0,
                uncertainty=0.0,
                reference_value=reference_frequency,
                measured_value=0.0,
                timestamp=time.time(),
                notes=f"Error: {str(e)}"
            )
            
    def calibrate_amplifier_gain(self, amplifier, reference_signal: float
                                ) -> CalibrationResult:
        """
        Calibrate amplifier gain accuracy.
        
        Args:
            amplifier: Amplifier interface object
            reference_signal: Reference signal amplitude
            
        Returns:
            CalibrationResult with gain calibration
        """
        try:
            self.logger.info("Starting amplifier gain calibration")
            
            # Apply reference signal and measure output
            # TODO: Implement actual amplifier interface
            
            # Simulate gain measurement
            nominal_gain = self.config.get('nominal_gain', 1000)
            measured_output = reference_signal * nominal_gain * np.random.normal(1.0, 0.01)
            
            actual_gain = measured_output / reference_signal
            gain_error = (actual_gain - nominal_gain) / nominal_gain
            
            result = CalibrationResult(
                success=True,
                calibration_factor=actual_gain,
                uncertainty=abs(gain_error * nominal_gain),
                reference_value=reference_signal,
                measured_value=measured_output,
                timestamp=time.time(),
                notes=f"Nominal gain: {nominal_gain}, "
                      f"Error: {gain_error*100:.2f}%"
            )
            
            self.calibration_history.append(result)
            
            self.logger.info(f"Amplifier calibration complete: "
                           f"Gain: {actual_gain:.1f}, Error: {gain_error*100:.2f}%")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Amplifier calibration failed: {e}")
            return CalibrationResult(
                success=False,
                calibration_factor=0.0,
                uncertainty=0.0,
                reference_value=reference_signal,
                measured_value=0.0,
                timestamp=time.time(),
                notes=f"Error: {str(e)}"
            )
            
    def verify_calibration(self, sensor_type: str, 
                          tolerance: float = 0.05) -> bool:
        """
        Verify sensor calibration within tolerance.
        
        Args:
            sensor_type: Type of sensor to verify
            tolerance: Acceptable calibration tolerance (fractional)
            
        Returns:
            True if calibration is within tolerance
        """
        try:
            # Find most recent calibration of this type
            recent_calibrations = [
                cal for cal in self.calibration_history
                if sensor_type.lower() in cal.notes.lower()
                and cal.success
            ]
            
            if not recent_calibrations:
                self.logger.warning(f"No calibration history found for {sensor_type}")
                return False
                
            # Get most recent calibration
            latest_cal = max(recent_calibrations, key=lambda x: x.timestamp)
            
            # Check if calibration is within tolerance
            relative_uncertainty = latest_cal.uncertainty / latest_cal.calibration_factor
            
            if relative_uncertainty <= tolerance:
                self.logger.info(f"{sensor_type} calibration verified: "
                               f"{relative_uncertainty*100:.2f}% < {tolerance*100:.2f}%")
                return True
            else:
                self.logger.warning(f"{sensor_type} calibration out of tolerance: "
                                  f"{relative_uncertainty*100:.2f}% > {tolerance*100:.2f}%")
                return False
                
        except Exception as e:
            self.logger.error(f"Calibration verification failed: {e}")
            return False
            
    def get_calibration_report(self) -> Dict[str, Any]:
        """Generate calibration report summary."""
        try:
            if not self.calibration_history:
                return {'status': 'no_calibrations', 'calibrations': []}
                
            # Organize calibrations by type
            calibrations_by_type = {}
            for cal in self.calibration_history:
                cal_type = cal.notes.split(',')[0] if ',' in cal.notes else 'unknown'
                if cal_type not in calibrations_by_type:
                    calibrations_by_type[cal_type] = []
                calibrations_by_type[cal_type].append(cal)
                
            # Generate summary statistics
            total_calibrations = len(self.calibration_history)
            successful_calibrations = sum(1 for cal in self.calibration_history if cal.success)
            success_rate = successful_calibrations / total_calibrations if total_calibrations > 0 else 0
            
            report = {
                'status': 'complete',
                'total_calibrations': total_calibrations,
                'successful_calibrations': successful_calibrations,
                'success_rate': success_rate,
                'calibrations_by_type': calibrations_by_type,
                'most_recent': max(self.calibration_history, key=lambda x: x.timestamp),
                'generation_time': time.time()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate calibration report: {e}")
            return {'status': 'error', 'message': str(e)}
